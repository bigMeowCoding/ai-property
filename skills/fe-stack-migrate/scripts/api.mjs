/**
 * fe-stack-migrate upload-assets — MSE 签名请求（对齐 busy-front-toolkit setMSESignature）
 *
 * 用法：由 upload.mjs 引用；或单独做签名自检。
 * 鉴权一律从环境变量读取，禁止把 secret/token 写入 git。
 *
 * 必填环境变量（通常由 Agent 从用户「Copy as cURL」解析后 export）：
 *   FE_STACK_GATEWAY_ORIGIN  如 https://test-gateway.busyming.com
 *   FE_STACK_APP_KEY         如 basic-test
 *   FE_STACK_APP_SECRET      管理端 VITE_APP_SECRET
 *   FE_STACK_AUTH            Bearer … 或裸 JWT（脚本会补 Bearer）
 *   FE_STACK_DEVICE_ID       localStorage X_DEVICE_INFO_ID（与 token 同会话）
 *   FE_STACK_OPERATE_INFO    浏览器真实请求里的 X-Operate-Info 完整 JSON 字符串
 * 可选：
 *   FE_STACK_ORIGIN / FE_STACK_UA / FE_STACK_PERMISSION_CODE
 */
import crypto from 'node:crypto';

function requireEnv(name) {
  const v = process.env[name];
  if (v == null || String(v).trim() === '') {
    throw new Error(`missing env: ${name}`);
  }
  return String(v).trim();
}

const GATEWAY_ORIGIN = requireEnv('FE_STACK_GATEWAY_ORIGIN').replace(/\/+$/, '');
const APP_KEY = requireEnv('FE_STACK_APP_KEY');
const APP_SECRET = requireEnv('FE_STACK_APP_SECRET');
const AUTH_RAW = requireEnv('FE_STACK_AUTH');
const AUTH = AUTH_RAW.startsWith('Bearer ') ? AUTH_RAW : `Bearer ${AUTH_RAW}`;
const DEVICE_ID = requireEnv('FE_STACK_DEVICE_ID');
const OPERATE_INFO = requireEnv('FE_STACK_OPERATE_INFO');

const UA =
  process.env.FE_STACK_UA ||
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';
const ORIGIN = (process.env.FE_STACK_ORIGIN || '').replace(/\/+$/, '');
const PERMISSION_CODE = process.env.FE_STACK_PERMISSION_CODE || '';

const DEVICE_INFO = JSON.stringify({
  id: DEVICE_ID,
  type: 'PC',
  platform: 'WEB',
  appVersion: UA.replace(/^Mozilla\//, ''),
  systemVersion: UA,
  model: 'PC',
});

/** 与 vanilla setMSESignature 一致：对当次 body 现算 Content-MD5 + HmacSHA256 */
export function signPost(pathWithStackService, bodyString) {
  const method = 'POST';
  const accept = 'application/json, text/plain, */*';
  const contentType = 'application/json';
  const contentMD5 = crypto.createHash('md5').update(bodyString, 'utf8').digest('base64');
  const xCaTimestamp = Date.now();
  const headersString = `x-ca-timestamp:${xCaTimestamp}\n`;
  const stringToSign = `${[method, accept, contentMD5, contentType, ''].join('\n')}\n${headersString}${pathWithStackService}`;
  const signature = crypto.createHmac('sha256', APP_SECRET).update(stringToSign, 'utf8').digest('base64');
  return {
    accept,
    contentType,
    contentMD5,
    xCaTimestamp,
    stringToSign,
    signature,
    headers: {
      Accept: accept,
      'Content-Type': contentType,
      'Content-MD5': contentMD5,
      'x-ca-timestamp': String(xCaTimestamp),
      'x-ca-key': APP_KEY,
      'x-ca-signature-method': 'HmacSHA256',
      'x-ca-signature-headers': 'x-ca-timestamp',
      'x-ca-signature': signature,
      timestamp: String(Math.floor(xCaTimestamp / 1000)),
      'x-device-info': DEVICE_INFO,
      'X-Operate-Info': OPERATE_INFO,
      ...(PERMISSION_CODE ? { permissionCode: PERMISSION_CODE } : {}),
      'User-Agent': UA,
      ...(ORIGIN
        ? { Origin: ORIGIN, Referer: `${ORIGIN}/` }
        : {}),
      Authorization: AUTH,
    },
  };
}

/**
 * @param {string} pathWithStackService 必须以 /stack-service 开头，如 /stack-service/resource/getGalleryToken
 * @param {object} body
 */
export async function callApi(pathWithStackService, body) {
  if (!pathWithStackService.startsWith('/stack-service/')) {
    throw new Error(`path must start with /stack-service/: ${pathWithStackService}`);
  }
  const bodyString = JSON.stringify(body ?? {});
  const signed = signPost(pathWithStackService, bodyString);
  const res = await fetch(`${GATEWAY_ORIGIN}${pathWithStackService}`, {
    method: 'POST',
    headers: signed.headers,
    body: bodyString,
  });
  const text = await res.text();
  let json = null;
  try {
    json = JSON.parse(text);
  } catch {
    /* keep text */
  }
  return { status: res.status, json, text, signed };
}

/**
 * 签名自检：用 curl 里的 path + bodyString + x-ca-timestamp 重算，与 curl 的 x-ca-signature 比对。
 * 注意：必须用 curl 当时的 timestamp，不能用 Date.now()。
 */
export function verifySignatureAgainstCurl({
  pathWithStackService,
  bodyString,
  xCaTimestamp,
  expectedSignature,
  expectedContentMD5,
}) {
  const method = 'POST';
  const accept = 'application/json, text/plain, */*';
  const contentType = 'application/json';
  const contentMD5 = crypto.createHash('md5').update(bodyString, 'utf8').digest('base64');
  const headersString = `x-ca-timestamp:${xCaTimestamp}\n`;
  const stringToSign = `${[method, accept, contentMD5, contentType, ''].join('\n')}\n${headersString}${pathWithStackService}`;
  const signature = crypto.createHmac('sha256', APP_SECRET).update(stringToSign, 'utf8').digest('base64');
  return {
    contentMD5Match: expectedContentMD5 == null || contentMD5 === expectedContentMD5,
    signatureMatch: signature === expectedSignature,
    contentMD5,
    signature,
    stringToSign,
  };
}

export const meta = {
  gatewayOrigin: GATEWAY_ORIGIN,
  appKey: APP_KEY,
  deviceIdSuffix: DEVICE_ID.slice(-8),
};
