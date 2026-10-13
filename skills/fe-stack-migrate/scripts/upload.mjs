/**
 * fe-stack-migrate upload-assets — Gallery STS 直传 + register + manifest
 *
 * 前置：已 export 鉴权环境变量（见 api.mjs 头注释）；工作目录为业务仓根。
 * 产出全部落在 node_modules/.fe-stack-upload/（勿写到仓库根）。
 *
 *   FE_STACK_PROJECT_CODE   默认取 cwd 目录名
 *   FE_STACK_ASSETS_ROOT    默认 src/assets
 *   FE_STACK_ENV            写入 manifest
 *   FE_STACK_FORCE          1=全量重传
 *   FE_STACK_ONLY_REFERENCED 1=只传被源码引用的文件（需先扫引用）
 *   FE_STACK_REFERENCED_LIST 逗号分隔 relativePath 白名单（与 ONLY_REFERENCED 配合）
 *
 * 依赖：业务仓需能 require('ali-oss')（没有则 npm i ali-oss -D，装在本仓即可）
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { callApi, meta } from './api.mjs';

const REPO = process.env.FE_STACK_REPO || process.cwd();
const ENV = process.env.FE_STACK_ENV || 'test';
const PROJECT_CODE = process.env.FE_STACK_PROJECT_CODE || path.basename(REPO);
const ASSETS_REL = process.env.FE_STACK_ASSETS_ROOT || 'src/assets';
const ASSETS_ROOT = path.resolve(REPO, ASSETS_REL);
const FORCE = process.env.FE_STACK_FORCE === '1';
const ONLY_REFERENCED = process.env.FE_STACK_ONLY_REFERENCED === '1';
const REFERENCED = new Set(
  (process.env.FE_STACK_REFERENCED_LIST || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean),
);

const WORK_DIR = path.join(REPO, 'node_modules', '.fe-stack-upload');
fs.mkdirSync(WORK_DIR, { recursive: true });
const MANIFEST_PATH = path.join(WORK_DIR, `manifest.${ENV}.json`);
const REPORT_PATH = path.join(WORK_DIR, `report.${ENV}.json`);

const EXT_RE = /\.(png|jpe?g|gif|webp|svg|ico|ttf|woff2?)$/i;
const MIME = {
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.ttf': 'font/ttf',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
};

const require = createRequire(path.join(REPO, 'package.json'));
let OSS;
try {
  OSS = require('ali-oss');
} catch {
  throw new Error('ali-oss not found in repo; run: npm i ali-oss -D (or pnpm add -D ali-oss)');
}

function walkAssets(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) walkAssets(full, out);
    else if (EXT_RE.test(e.name)) out.push(full);
  }
  return out;
}

let files = walkAssets(ASSETS_ROOT).map((full) => ({
  full,
  rel: path.relative(ASSETS_ROOT, full).split(path.sep).join('/'),
}));

if (ONLY_REFERENCED) {
  if (!REFERENCED.size) {
    throw new Error('FE_STACK_ONLY_REFERENCED=1 but FE_STACK_REFERENCED_LIST is empty');
  }
  files = files.filter((f) => REFERENCED.has(f.rel));
}

const manifest = fs.existsSync(MANIFEST_PATH)
  ? JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'))
  : {
      version: 1,
      env: ENV,
      projectCode: PROJECT_CODE,
      cdnDomain: '',
      assetsRoot: ASSETS_REL,
      files: {},
    };

const tok = await callApi('/stack-service/resource/getGalleryToken', { projectCode: PROJECT_CODE });
if (!tok.json?.success) {
  throw new Error(`getGalleryToken failed: ${tok.text.slice(0, 400)}`);
}

const {
  regionId,
  accessKeyId,
  accessKeySecret,
  securityToken,
  bucketName,
  baseDir,
  cdnDomain,
  resourceUpload,
} = tok.json.data;
// 凭证字段已统一为 cdnDomain（勿再读已废弃的 cdnBaseUrl）
manifest.cdnDomain = String(cdnDomain || '').replace(/\/+$/, '');
const base = String(baseDir || '').replace(/\/+$/, '');
const overwrite = resourceUpload?.overwrite === true;

const client = new OSS({
  region: `oss-${String(regionId || '').replace(/^oss-/, '')}`,
  accessKeyId,
  accessKeySecret,
  stsToken: securityToken,
  bucket: bucketName,
  secure: true,
});

async function ossObjectExists(objectKey) {
  try {
    await client.head(objectKey);
    return true;
  } catch (e) {
    const status = Number(e?.status || e?.statusCode || 0);
    const code = String(e?.code || e?.name || '');
    if (status === 404 || code === 'NoSuchKey' || code === 'NotFound') return false;
    throw e;
  }
}

/** 相对 assets 的对象路径：默认原名；不覆盖且重名时 name_{5位hash}.ext */
async function resolveUploadRel(rel, sha256) {
  const posixRel = rel.split(path.sep).join('/');
  const originalKey = `${base}/${posixRel}`;
  if (overwrite || !(await ossObjectExists(originalKey))) {
    return posixRel;
  }
  const ext = path.extname(posixRel);
  const dir = path.dirname(posixRel);
  const baseName = path.basename(posixRel, ext);
  const collisionName = `${baseName}_${sha256.slice(0, 5)}${ext}`;
  return dir && dir !== '.' ? `${dir}/${collisionName}` : collisionName;
}

const report = [];
let uploaded = 0;
let updated = 0;
let skipped = 0;
let failed = 0;

for (const { full, rel } of files) {
  const buf = fs.readFileSync(full);
  const sha256 = crypto.createHash('sha256').update(buf).digest('hex');
  const md5 = crypto.createHash('md5').update(buf).digest('hex');
  const prev = manifest.files[rel];
  const realFileName = path.basename(rel);
  if (!FORCE && prev && prev.sha256 === sha256 && prev.cdnUrl) {
    skipped += 1;
    report.push({
      relativePath: rel,
      filePath: prev.filePath || rel.split(path.sep).join('/'),
      fileName: realFileName,
      ossKey: prev.ossKey || `${base}/${prev.filePath || rel.split(path.sep).join('/')}`,
      cdnUrl: prev.cdnUrl,
      uploadStatus: 'skipped',
      error: null,
    });
    continue;
  }

  let filePath = rel.split(path.sep).join('/');
  let ossKey = `${base}/${filePath}`;
  const mime = MIME[path.extname(rel).toLowerCase()] || 'application/octet-stream';
  try {
    filePath = await resolveUploadRel(rel, sha256);
    ossKey = `${base}/${filePath}`;
    // 只 put，不要 putACL/public-read：STS 策略会 Access denied，CDN 访问由桶/CDN 层控制
    // 登记 fileName 始终为真实原始文件名
    await client.put(ossKey, buf, { mime, headers: { 'Content-Type': mime } });
    if (prev) updated += 1;
    else uploaded += 1;
    report.push({
      relativePath: rel,
      filePath,
      fileName: realFileName,
      ossKey,
      cdnUrl: null,
      uploadStatus: prev ? 'updated' : 'uploaded',
      error: null,
      _sha256: sha256,
      _md5: md5,
      _size: buf.length,
      _mime: mime,
    });
  } catch (e) {
    failed += 1;
    report.push({
      relativePath: rel,
      filePath,
      fileName: realFileName,
      ossKey,
      cdnUrl: null,
      uploadStatus: 'failed',
      error: String(e.message || e).slice(0, 200),
    });
  }
}

const toRegister = report.filter((r) => r.uploadStatus === 'uploaded' || r.uploadStatus === 'updated');
if (toRegister.length) {
  const reg = await callApi('/stack-service/resource/register', {
    projectCode: PROJECT_CODE,
    source: 'manage',
    files: toRegister.map((r) => ({
      filePath: r.filePath,
      fileName: r.fileName,
      fileSize: r._size,
      mimeType: r._mime,
      md5: r._md5,
    })),
  });
  if (!reg.json?.success) {
    throw new Error(`register failed: ${reg.text.slice(0, 500)}`);
  }
  const items = reg.json.data?.items || [];
  toRegister.forEach((r, i) => {
    const item = items[i] || {};
    r.cdnUrl = item.cdnUrl || `${manifest.cdnDomain}/${r.ossKey}`;
    r.ossKey = item.ossKey || r.ossKey;
    r.filePath = item.relativePath || r.filePath;
    manifest.files[r.relativePath] = {
      sha256: r._sha256,
      md5: r._md5,
      size: r._size,
      filePath: r.filePath,
      ossKey: r.ossKey,
      cdnUrl: r.cdnUrl,
      uploadedAt: new Date().toISOString(),
    };
    delete r._sha256;
    delete r._md5;
    delete r._size;
    delete r._mime;
  });
}

fs.writeFileSync(MANIFEST_PATH, `${JSON.stringify(manifest, null, 2)}\n`);
const out = {
  env: ENV,
  projectCode: PROJECT_CODE,
  assetsRoot: ASSETS_REL,
  gateway: meta.gatewayOrigin,
  cdnDomain: manifest.cdnDomain,
  workDir: WORK_DIR,
  summary: {
    total: files.length,
    uploaded,
    updated,
    skipped,
    failed,
  },
  files: report,
};
fs.writeFileSync(REPORT_PATH, `${JSON.stringify(out, null, 2)}\n`);
console.log(JSON.stringify(out, null, 2));
