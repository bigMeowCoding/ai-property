适用对象：接入门店运营 App 的 H5 开发、App 开发和测试同学。
代码基线：busyming-operation-app，分支 feature/cwc_2.1.5，提交 34310b6。
核对日期：2026-09-05。本文描述该代码基线，不代表所有线上安装包都已具备这些能力。
所有用户、权限码、地址和凭据示例均为虚构。不要将真实上下文直接粘贴进文档、日志或截图。
使用方法：新项目先读第一部分；查参数、返回值和示例时读第二部分；公共类型集中在附录 A。
阅读导航
我要做什么	去哪里看
尽快完成初始化	第一部分 1：最小接入
找 Token、用户信息、权限码	第一部分 2、3：上下文与认证权限
处理 401、缺数据或桥超时	第一部分 4：失败处理
返回、回首页、打开抽屉	第一部分 5；第二部分 9
拍照、相册、视频、文件上传	第二部分 12、13
查一个桥方法的入参和出参	第二部分 7：完整方法索引
复制 TypeScript 声明	附录 A
联调或验收	附录 B
第一部分：H5 接入指南
1. 最小接入：先拿上下文，再启动业务
1.1 App 和 H5 各自负责什么
● App 负责登录、获取统一门户认证与权限、设备信息，以及相机、定位等原生功能。
● H5 负责等待上下文、选择正确凭证、控制页面与按钮、处理业务请求及错误展示。
● 后端负责最终鉴权。H5 隐藏按钮不能代替后端权限校验。
推荐顺序：等待桥可用 → 获取上下文 → 配置请求与权限 → 启动业务页面。
不要在业务模块顶层写 const token = window.__APP_CONTEXT__?.…，再期待它自动变成最新值。首次拿到空值后，这个变量不会跟着后续注入自动更新。
1.2 可复制的启动封装
先把附录 A 保存为 app-bridge.d.ts 并纳入 H5 的 TypeScript 配置；再将下面代码保存为 app-context.ts。它不依赖 Vue 或 React，也不轮询。
export function getAppContext(timeoutMs = 15000): Promise<ReadyAppContext> {
  if (typeof window === 'undefined') {
    return Promise.reject(Object.assign(new Error('请在客户端获取 App 上下文'), {
      code: 'BRIDGE_UNAVAILABLE',
    }))
  }
  return new Promise((resolve, reject) => {
    let started = false
    let settled = false
    const cleanup = () => {
      window.clearTimeout(timer)
      window.removeEventListener('app-context-bridge-ready', start)
      window.removeEventListener('pagehide', leave)
    }
    const finish = (value: ReadyAppContext | null, error?: unknown) => {
      if (settled) return
      settled = true
      cleanup()
      if (error) reject(error)
      else if (value) resolve(value)
      else reject(new Error('App 未返回上下文'))
    }
    const start = () => {
      if (started || settled || typeof window.__APP_GET_CONTEXT__ !== 'function') return
      started = true
      try {
        window.__APP_GET_CONTEXT__().then(
          context => finish(context),
          error => finish(null, error),
        )
      } catch (error) {
        finish(null, error)
      }
    }
    const leave = () => finish(null, Object.assign(new Error('页面已离开'), {
      code: 'PAGE_CHANGED',
    }))
    const timer = window.setTimeout(() => finish(null, Object.assign(
      new Error('获取 App 上下文超时，请重试或确认 App 版本'),
      { code: 'CONTEXT_TIMEOUT' },
    )), timeoutMs)
    window.addEventListener('app-context-bridge-ready', start)
    window.addEventListener('pagehide', leave)
    start()
  })
}
getAppContext 是本文给 H5 的封装，不是新增的 App 方法。timeoutMs 只控制 H5 总等待时间，不会更改 App 内部超时。
启动入口示意，./business-entry 是接入方自己的模块，需要导出 mount(context)：
import { getAppContext } from './app-context'

async function start() {
  try {
    const context = await getAppContext()
    // 兼容仍读取此字段的旧业务代码；这不是持续订阅。
    window.__APP_CONTEXT__ = context
    // 延迟导入，避免业务模块先于上下文就绪读取 Token。
    const { mount } = await import('./business-entry')
    await mount(context)
  } catch (error) {
    const code = (error as { code?: string })?.code
    if (code === 'PAGE_CHANGED') return
    // 替换成项目的错误页，不打印完整 error、接口响应或上下文。
    const panel = document.createElement('div')
    panel.textContent = '初始化失败，请确认 App 版本、网络和页面接入配置后重试。'
    const retry = document.createElement('button')
    retry.textContent = '重新加载'
    retry.onclick = () => window.location.reload()
    panel.appendChild(retry)
    document.body.appendChild(panel)
  }
}

void start()
在 mount 内完成请求客户端、路由和权限初始化，再挂载 Vue/React。此示例的错误 UI 可以替换，但不要去掉失败出口。
1.3 新老 App 如何兼容
情况	建议做法
当前 App 已提供异步桥	使用上面的启动封装
桥脚本晚于 H5 加载	封装等待 app-context-bridge-ready，不需要轮询
旧 App 没有异步桥	超时后提示升级；不能假装旧对象已准备好
普通浏览器本地开发	使用独立开发 Mock，不请求或携带真实生产认证
非可信页面／专用上下文入口	先与 App 确认接入方式，不能靠延长超时解决
window.__BUSYMING_OPERATION_APP__ 和具体方法存在性用于判断能力；不要只依赖 User-Agent。__APP_BRIDGE_CODE__ = 1 也不能用来判断是否拥有本文的新方法。
2. window.__APP_CONTEXT__ 有哪些数据
2.1 五组数据速览
字段	内容	常用取值
unifiedPortal	统一门户认证与用户信息	accessToken、userInfo
personnel	App 原业务／人资认证、权限与用户信息	accessToken、permissionCodes、userInfo
portalAuthObj	统一门户权限	portalAuthCodes、resourceTree、resourceIds
deviceInfo	当前 App 设备描述，可为 null	id、platform、model、deviceName
zoneOwnerInfo	当前战区与负责人	zoneUserId、zoneUserCode、selectedZoneInfo
personnel 和 portalAuthObj 是平级字段，不在 unifiedPortal 内。旧注入对象里的这两项受可信地址和入口条件限制；新异步桥成功时会返回这两项，但不保证用户资料中的每个字符串都非空。
2.2 结构示例
下面是字段示例，不是可用认证数据。资源树只展示一个虚构节点，不代表真实权限配置。
{
  "unifiedPortal": {
    "accessToken": "DEMO_PORTAL_TOKEN",
    "userInfo": {
      "id": 10001,
      "nickName": "示例用户",
      "isInitPassword": false,
      "accessTokenExpireTime": "示例过期时间",
      "refreshToken": "REDACTED",
      "refreshTokenExpireTime": "示例过期时间",
      "userTypeIdList": [{ "userType": 2, "userId": "20001" }]
    }
  },
  "personnel": {
    "accessToken": "DEMO_BUSINESS_TOKEN",
    "permissionCodes": ["demoPersonnelView"],
    "userInfo": {
      "userId": 20001,
      "userCode": "DEMO001",
      "realName": "示例用户",
      "userName": "demo-user",
      "phone": "REDACTED",
      "orgId": "30001",
      "organizationName": "示例组织",
      "thirdUid": "40001",
      "userStatus": "3",
      "userType": "store",
      "weights": 0,
      "workPost": "demo_post",
      "workPostName": "示例岗位"
    }
  },
  "portalAuthObj": {
    "portalAuthCodes": ["demoPortalView"],
    "resourceTree": [{
      "id": 50001,
      "name": "示例功能",
      "code": "demoPortalView",
      "appId": 60001,
      "parentId": null,
      "children": []
    }],
    "resourceIds": [50001]
  },
  "deviceInfo": {
    "id": "DEMO-DEVICE-ID",
    "type": "APP",
    "platform": "IOS",
    "appVersion": "2.1.5",
    "systemVersion": "15.6.1",
    "model": "iPhone 13",
    "deviceName": "iPhone"
  },
  "zoneOwnerInfo": {
    "zoneUserId": "20001",
    "zoneUserCode": "DEMO001",
    "selectedZoneInfo": null
  }
}
字段约定：
● unifiedPortal.userInfo 来源于门户响应，字段会随后端变化；可能保留 refreshToken 等敏感字段。H5 不得打印它，也不能据此自行接管刷新协议。
● personnel.userInfo 是 App 缓存资料的白名单字段；personnel.accessToken 是原业务 Token，不是 BizMidPlatform 兑换结果。
● portalAuthObj.portalAuthCodes 是 App 根据资源树与用户拥有资源 ID 计算出的有效权限码。
● resourceTree 是应用原始资源树，不是“当前用户能访问的菜单”。节点的 hasPermission、isShow 等原始值不能替代用户权限判断。
● resourceIds 可以是数字或字符串，比较前统一成字符串。
● deviceInfo.platform：iOS 为 IOS，Android 为 AND，其他平台为 WEB。不要发送 ANDROID。
● 当前 deviceName 固定为 iPhone、Android、APP，不再读取用户自定义设备名。设备读取失败时整个 deviceInfo 可为 null。
● 有战区时，selectedZoneInfo 保留选中战区字段；没有战区时为 null，负责人回退当前登录用户。负责人字段可能为 null，接入方仍需检查业务必填条件。
资源树节点的常见字段如下。除 children 的递归结构外，节点字段不是所有系统都必填，不能直接套用某个用户样例的值。
节点字段	常见类型	用途与限制
id	字符串或数字	节点资源 ID，与 resourceIds 统一类型后比较
code	字符串	资源权限码；存在该 code 不代表当前用户拥有
name／label	字符串	展示名称
appId／appCode	字符串或数字／字符串	所属应用
parentId	字符串、数字或 null	父节点
children	节点数组	下级资源；可为空或缺失
uri／path／redirectUrl	字符串或 null	后端定义的地址／路由信息；使用前校验，不自动视为可信跳转
type／level／sort	通常数字	资源类型、层级、顺序；具体枚举需业务合同，本文不猜测含义
riskLevel	数字或字符串	操作风险信息，按门户接口合同使用
status／isShow	后端枚举	状态／展示提示，不代替当前用户授权
hasPermission／isPermission	后端／运行时标志	原始树与计算后扁平树不是同一个对象，不盲目信任原始树标记
resourceObjectDimensions	数组或 null	资源对象维度，具体值以接口合同为准
icon／action／ignore	字符串／布尔等扩展值	由具体应用解释，不代表公共桥方法或通用跳转命令
人员信息中的 userType、userStatus、weights、workPost 等原样描述业务身份，不在本文猜测枚举，也不能拿用户姓名／岗位名替代权限码做授权判断。
2.3 同步对象与异步方法的区别
对比	__APP_CONTEXT__	__APP_GET_CONTEXT__()
形式	注入的对象	返回 Promise 的函数
首次读取	可能尚未注入，不承诺 H5 第一行脚本就可读	等桥可用后调用，成功才消费
门户权限	旧流程可能先给快照，之后更新	等待权限初始化就绪；空权限合法
更新	App 可能重新赋值整个对象	每次完成后再调用，获取当时最新快照
失败	可能缺字段／暂时无对象	reject，包含可处理的错误信息
适用	兼容已有 H5	新接入推荐
拿到 Promise 结果不代表所有其他桥都存在；抽屉等能力有独立条件，每次调用仍需检测。
2.4 哪些地址能用
当前公共异步上下文桥仅对下列配置根路径及其子路径开放；实际域名取决于 App 环境配置：
配置来源	子路径
TARGET_MANAGE_H5_ROOT	target-manage-h5、store-opening-h5、store-hr-h5/meeting
H5_PORTAL_ROOT	store-renovation、operation-h5、store-information/store-profile
新域名、新路径、重定向后的地址都应先与 App 确认。方法存在不等于该地址获准读取认证数据。
显式传入 route.params.appContext 的专用入口返回 UNSUPPORTED_CONTEXT，继续沿用专用协议。例如 unifiedTokenResp、selectStoreInfo、defaultOperateInfo 属于部分专用上下文，不是公共五组数据的必备字段。
3. 认证和权限怎么使用
3.1 先确认接口属于哪套体系
接口类型	使用什么	不要使用什么
原业务／人资接口，合同使用 App 业务 Token	context.personnel.accessToken；兼容字段为 window.__APP_TOKEN__	门户 Token、中台 TokenInfo
明确要求中台 TokenInfo 的接口	await __APP_GET_TOKEN_AUTHINFO__({ bizType: 'BizMidPlatform', brand: 'LSHM' })	根据名称猜一种 Token
统一门户／统一网关接口	context.unifiedPortal.accessToken	原业务 Token
普通原业务接口不需要先调用 TokenInfo 兑换桥。认证头格式以对应后端合同为准，当前 App 业务和门户客户端通常使用 Authorization: Bearer <token>。
3.2 控制页面和按钮
function canUsePersonnel(context: ReadyAppContext, code: string): boolean {
  return context.personnel.permissionCodes.includes(code)
}

function canUsePortal(context: ReadyAppContext, code: string): boolean {
  return context.portalAuthObj.portalAuthCodes.includes(code)
}

function ownsPortalResource(context: ReadyAppContext, id: string | number): boolean {
  return context.portalAuthObj.resourceIds.some(owned => String(owned) === String(id))
}
权限码由业务与后端共同确定，示例码不能直接使用。无权限展示无权限页面或隐藏按钮；不要持续等待数组变成非空。资源树用于组织菜单时，应结合用户拥有的资源 ID，并按产品规则保留必要父节点，不能把整棵树直接当成授权菜单。
3.3 Token 不等于完整请求配置
统一门户部分接口还要求 MSE 签名、x-device-info、X-Operate-Info 等。公共上下文提供认证与权限数据，但不提供 App Secret，也没有通用的“代 H5 请求任意门户接口”桥。
● H5 不自行调用 App 的 find-unified-token 兑换链路。
● H5 直连网关需单独确认签名、设备头编码及操作信息协议；不要因为拿到 Token 就默认可直连。
● 不要把 App 内部 permissionCode 字段直接当成网关最终请求头。
● 不要在 H5 内置生产 Secret；有签名需求时与后端确定代理方案。
● App 网络客户端的 401 自动刷新，不会自动拦截 H5 自己发出的 fetch／Axios 请求。
3.4 请求头最小示例
下面只演示“如何选正确的认证头”，不代表完整网关请求已满足签名要求。两个函数分别交给各自的请求客户端，禁止合并成一个通用 Token 字段。
function businessAuthorization(context: ReadyAppContext): Record<string, string> {
  const token = context.personnel.accessToken.trim()
  if (!token) throw new Error('缺少原业务认证')
  return { Authorization: `Bearer ${token}` }
}

function portalAuthorization(context: ReadyAppContext): Record<string, string> {
  const token = context.unifiedPortal.accessToken.trim()
  if (!token) throw new Error('缺少统一门户认证')
  return { Authorization: `Bearer ${token}` }
}
请求客户端应使用当前有效上下文，不在模块顶层永久缓存最早的空 Token。对设备头：当前 App 会做专用编码处理；如果 H5 直连也需要发送设备头，应按已确认的网关解码合同实现，不直接把含 Unicode 字符的 JSON 填入 HTTP Header，也不能在未确认合同前随意叠加 URL 编码、Base64 或二次编码。
第一部分只提供已确认的凭证选择方式；具体业务 endpoint、MSE 密钥管理、X-Operate-Info 构造和 401 刷新必须按对接系统确认，本文不提供虚构的通用可用签名代码。
4. 401、缺数据和超时如何处理
现象	H5 应做什么	不应做什么
网络失败、请求超时	展示重试，保留必要页面状态	清理整个 App 登录态
403 或正常空权限	展示无权限，联系业务管理员确认授权	无限刷新 Token
后端确认原业务登录已失效	停止受保护请求，调用 __APP_GO_LOGIN__()	每个并发失败请求各跳一次登录
门户接口 401	核对门户凭证与合同；可重新获取上下文检查 App 是否已有新凭证；持续失败按约定走重新登录	把 __APP_GET_CONTEXT__() 当成强制刷新 Token
桥不存在	等待安装或提示升级／非 App 环境	直接调用 undefined
UNTRUSTED_PAGE	核对页面最终地址和可信路径配置	延长等待时间或绕过地址校验
UNSUPPORTED_CONTEXT	确认专用入口协议	覆盖专用字段为公共对象
页面离开、身份变化	丢弃旧任务，由新页面重新初始化	使用上一账号的快照
当前 __APP_GET_CONTEXT__() **没有参数，也不支持 **{ forceRefreshToken: true }。重复获取可能仍返回有效缓存的同一个 Token。不要自动无限重发 401 请求；有副作用的提交接口不能未经业务确认自动重放。
只在确认需要重新登录时调用：
let loginRequested = false

export function requestAppRelogin(): void {
  if (loginRequested) return
  if (typeof window.__APP_GO_LOGIN__ !== 'function') {
    throw new Error('当前环境不能唤起 App 登录，请返回 App 重新登录')
  }
  loginRequested = true
  window.__APP_GO_LOGIN__()
}
该方法会清除用户相关登录缓存，并把 App 导航重置到登录页；不是只清当前 H5 Token，不提供“登录完成后返回原 H5”的回调承诺。
5. 导航、更新与页面生命周期
5.1 选对导航方式
场景	选择
同一个 H5 内部列表 → 详情	H5 自己的 Router
回退／关闭当前 App WebView	__APP_ROUTER_BACK__()，具体行为见第二部分
回 App 主容器的运营指导工作台	__APP_GO_HOME_TAB__()
打开独立原生 WebView	__APP_OPEN_NEW_WINDOW__(url, …)
当前工作台唤起抽屉	检测并调用 __APP_OPEN_WORKBENCH_DRAWER__()
指定跳转到任意 App Tab	当前没有公共桥；需要单独扩展，不可传入虚构 tab 参数
新 WebView 不继承当前 Vue/React 组件状态、内存缓存和 H5 路由栈。抽屉目前仅由提供 onOpenWorkbenchDrawer 的宿主注入，例如新店工作台；普通二级 WebView 不能假设存在。
5.2 数据不是永久不变的
● 旧 __APP_CONTEXT__ 的 Token／权限变化继续通过热注入更新；不能将其描述为“每次 Token 更新都重建 WebView”。
● 用户或战区身份变化、恢复流程可能重建 WebView；H5 必须可重复初始化。
● 异步桥返回的是快照，不自动更新 H5 自己保存的对象。需要新数据时重新调用；App 没有通用 appContextChanged 事件可供依赖。
● 桥会隔离旧页面、旧账号与旧战区的结果。无法安全回传时旧调用可能通过超时结束。
● 页面销毁时清理 H5 自己的监听和请求；不要把完整上下文长期写入 localStorage。
5.3 App 主动通知 H5
这些是回调或事件，不是让 H5 主动调用的 App 方法。
名称	形式／数据	接入要求
onAppToken(token)	App 调用 H5 函数；原业务 Token 字符串	更新原业务客户端，不混成门户 Token
onAppCity(adcode)	App 调用 H5 函数；城市代码字符串	无订阅取消接口，根模块统一管理
onAppGeo(geo)	App 调用 H5 函数；latitude,longitude	检查空值并转换数字
onReactNativeSafeAreaInsetsChange(insets)	App 调用 H5 函数；四边数值	与安全区同步读取方法配合
app-context-bridge-ready	DOM 事件，无业务数据	只表示上下文桥已安装
appLifecycleChange	CustomEvent<AppLifecyclePayload>	读取初始状态并按 sequence 去重
appZoneChanged	DOM 事件，detail 为战区相关对象／空值	旧业务同步协议，优先用新上下文中的负责人信息
appLocalZoneChanged	局部战区选择事件	仅专用选择器业务，不用于修改全局战区
onAppUpdateList()	原生返回部分列表后调用	选址／列表业务专用
receiveRNData(data) 等	旧媒体上传回调	见第二部分 13
生命周期监听示例，onState 由 H5 提供：
function observeAppLifecycle(onState: (state: AppLifecyclePayload) => void): () => void {
  let sequence = -1
  const accept = (value?: AppLifecyclePayload) => {
    if (!value || value.sequence <= sequence) return
    sequence = value.sequence
    onState(value)
  }
  const listener = (event: Event) => accept((event as CustomEvent<AppLifecyclePayload>).detail)
  window.addEventListener('appLifecycleChange', listener)
  accept(window.__APP_LIFECYCLE_STATE__)
  return () => window.removeEventListener('appLifecycleChange', listener)
}
5.4 其他兼容字段
字段	当前类型／含义
__BUSYMING_OPERATION_APP__	true，App 容器标识
__APP__	字符串 SITESTORE，不是桥对象
__APP_TOKEN__	原业务 Token 字符串，ignoreToken 时为空；该开关不是所有上下文凭据的总开关
__APP_CITY__	城市代码字符串，可能为空
__APP_GEO__	经纬度字符串，可能为空
__APP_PLATFORM__	ios／android；不同于设备头的 IOS／AND
__APP_PLATFORM_ANDROID_BRAND__	Android 品牌，iOS 通常为空
__APP_STATUS_BAR_HEIGHT__	数字字符串，使用前 Number(...)
__APP_LIFECYCLE_BRIDGE_VERSION__	数字，当前为 1
__APP_LIFECYCLE_STATE__	最近一次前后台状态对象
localStorage['common-select-store']	旧战区同步协议，不是新 H5 通用认证存储
6. App 侧接入新 H5 的最小配置
此节供 App 配合同学使用，不是 H5 可以任意发出的桥消息。
navigation.navigate('WebViewScreen', {
  url: 'https://example.com/operation-h5/home', // 换成环境配置中的可信地址
  mode: 'start',
  id: 'example-h5-' + Date.now(),
  needSafeArea: true,
  needNavBar: false,
  narbarTitle: '示例应用',
})
url 使用完整 HTTPS 地址；id 区分实例；新公共接入不要误传 appContext，否则进入专用上下文协议。历史 needNarBar／narBarTitle 已兼容到 needNavBar／narbarTitle，不要再照旧文档写成参数失效。
联调时同时确认 App 安装包版本、环境、可信路径、重定向地址及入口是否支持抽屉等局部能力。普通浏览器、企微 WebView 和运营 App WebView 不是同一个运行环境。
第二部分：桥方法指南
7. 完整方法索引与公共约定
桥方法指 App 注入到 window、供 H5 调用的函数。本文只把实际注入的公共方法列为 API，不把原生内部 action 当成公共桥。
分类	方法	详细章节
认证与上下文	__APP_GET_CONTEXT__、__APP_GET_TOKEN_AUTHINFO__、__APP_GO_LOGIN__	8
导航与容器	__APP_ROUTER_BACK__、__APP_GO_HOME_TAB__、__APP_OPEN_WORKBENCH_DRAWER__、__APP_OPEN_NEW_WINDOW__、__OPEN_APP_WEBVIEW__	9
设备与适配	__APP_GET_VERSION__、__APP_GET_SAFE_AREA__、__APP_ORIENTATION__、__APP_REGISTER_KEYBOARD_LISTENER__	10
定位与权限	__APP_GET_CURRENT_LOCATION__、__APP_GET_CURRENT_ADDRESS__、__APP_GET_PERMISSION_LOCATION__、__APP_NOTIFICATION_PERMISSION__、__APP_CHECK_OR_REQUEST_PERMISSION__、__APP_OPEN_SETTING__	11
新媒体协议	__APP_OPEN_PICKER_WITH_RESULT__、__APP_GO_TO_CAMERA_WITH_RESULT__、__APP_OPEN_TRANSCRIBE_WITH_RESULT__、__APP_OPEN_SIGNATURE__	12
旧媒体协议	__APP_OPEN_PICKER__、__APP_GO_TO_CAMERA__、__APP_OPEN_TRANSCRIBE__、__APP_OPEN_FILE_PICKER__、__APP_CANCEL_REQUEST__	13
预览与系统操作	__APP_SCAN_CODE__、__APP_PREVIEW_IMAGE__、__APP_PREVIEW_VIDEO__、__APP_DOCUMENT_VIEW__、__APP_OPEN_FILE__、__APP_IMAGE_TO_DATA_URL__、__APP_PHOTO_DOWNLOAD__、__APP_CALL_PHONE__、__APP_COPY_TEXT__、__APP_OPEN_MAP__	14
业务专用	__APP_OPEN_REPORT_SHARE__、__APP_REPORT_SHARE_IMAGE_READY__、__APP_PATROL_START_INSPECTION__、__APP_PATROL_CONTINUE_INSPECTION__、__APP_ACTION__、__APP_LOCATION__	15
7.1 调用前检测
将下面工具保存为 app-bridge.ts，类型来自附录 A。后续方法示例默认已引入 requireBridge、withBridgeTimeout；业务处理函数以文字说明，由接入方实现。
export function requireBridge<K extends keyof AppBridgeMethods>(name: K): AppBridgeMethods[K] {
  if (typeof window === 'undefined' || typeof window[name] !== 'function') {
    throw Object.assign(new Error(`当前页面不支持 ${name}`), { code: 'BRIDGE_UNAVAILABLE' })
  }
  return window[name] as AppBridgeMethods[K]
}

export function withBridgeTimeout<T>(task: Promise<T>, timeoutMs: number): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(Object.assign(new Error('App 操作等待超时'), {
      code: 'BRIDGE_TIMEOUT',
    })), timeoutMs)
    task.then(value => {
      clearTimeout(timer)
      resolve(value)
    }, error => {
      clearTimeout(timer)
      reject(error)
    })
  })
}
所有示例放在自己的异步事件处理器中，并在外层 try/catch 显示错误；不要打印整个错误对象。无返回值方法不能据此判断原生操作成功。可选链 ?.() 适合可选功能，但会把缺少桥变成静默无操作，不适合必需认证流程。
7.2 返回值、超时与并发
● void：只发送操作，没有完成回执，不要 await 后当成成功。
● Promise<T>：等待回传，既要检查 T 内的失败标志，也要捕获 reject；部分旧桥可能 reject 字符串而不是 Error。
● string：例如安全区是同步 JSON 字符串，需要解析。
● 事件流：先注册回调，再调用；上传进度不是 Promise。
● H5 超时包装只停止当前等待，不会关闭相机、取消上传或清理 App 内部任务。超时后不要自动重复打开原生页面。
● 上下文桥可并发复用；相机、相册、扫码、签名、分享等交互功能建议按钮加忙碌状态，串行调用。
● 不传 callbackId、不覆盖内部回调、不自行操作 __APP_CONTEXT_BRIDGE_V1__。普通业务不直接发送 postMessage({ action: … })。
详细参数和返回类型均以附录 A 为统一定义；以下按方法补充默认值、真实行为和用法。
8. 认证与上下文
8.1 __APP_GET_CONTEXT__：异步获取认证、权限和业务上下文
__APP_GET_CONTEXT__(): Promise<ReadyAppContext>
项目	说明
入参	无。不要传 Token、用户 ID、callbackId 或刷新参数
成功	直接返回对象，包含第一部分介绍的五组数据；不要再 JSON.parse
失败	reject 一个带 code 的 Error，显示其适合用户阅读的 message
并发	同一文档正在获取时，重复调用复用待完成 Promise
再次调用	上一次结束后会重新构建快照，但底层 Token／资源可能来自缓存
权限等待	复用正在初始化的门户请求；失败后新的主动调用可尝试初始化，不无限重试
时限	App 构建默认 10 秒；桥等待 12 秒；本文 H5 启动封装默认总计 15 秒
页面限制	可信路径、主页面窗口、无专用 route appContext；不是 iframe 通用桥
最短用法（确定桥已经安装时）：
const context = await requireBridge('__APP_GET_CONTEXT__')()
const businessToken = context.personnel.accessToken
const portalToken = context.unifiedPortal.accessToken
const personnelCodes = context.personnel.permissionCodes
const portalCodes = context.portalAuthObj.portalAuthCodes
// 将各自凭证交给对应请求客户端，不输出这些值。
首次启动优先使用第一部分的 getAppContext()，因为只检查函数存在性不能等待桥晚到。
错误码	含义	建议
BRIDGE_UNAVAILABLE	通道或方法不可用	确认 App 环境、版本和桥安装时机
CONTEXT_TIMEOUT	桥／H5 总等待超时	允许用户重试，核查网络与版本
PAGE_CHANGED	页面离开	不再操作旧页面，不弹干扰提示
SESSION_CHANGED	无有效业务登录会话	走重新登录流程
UNTRUSTED_PAGE	请求地址不在允许范围	联系 App 配置正确入口
UNSUPPORTED_CONTEXT	专用上下文入口	按专用协议接入
APP_USER_CONTEXT_MISSING	App 用户缺失或身份变化	重新打开／重新登录，不用旧用户资料
PERSONNEL_TOKEN_MISSING	原业务 Token 无效或无法解析	确认 App 登录状态
TOKEN_MISSING	未获得有效门户 Token	重试，持续失败联系 App／认证服务
AUTH_UNAUTHORIZED	认证返回 401	按第一部分 4 处理，不无限重放业务请求
AUTH_FORBIDDEN	认证返回 403	展示无权限，不靠轮询解决
AUTH_TIMEOUT	App 构建或认证请求超时	检查网络后重试
NETWORK_ERROR	网络不可用	网络恢复后重试
UNKNOWN／CONTEXT_ERROR／其他	未归类错误／兜底	显示明确失败状态，记录脱敏错误码
原生内部错误可能含 retryable、traceId，但当前异步桥对 H5 只保证错误的 code/message，不要依赖内部字段。
依据：webViewAppContextBridge.ts、buildOperationH5AppContext.ts。
8.2 __APP_GET_TOKEN_AUTHINFO__：兑换指定中台 TokenInfo
__APP_GET_TOKEN_AUTHINFO__(args?: TokenAuthInfoArgs): Promise<Record<string, unknown> | ''>
参数	类型	必填	默认值／说明
args.bizType	string	建议传	当前有效用途为 BizMidPlatform；其他值也走默认分支，不代表支持其他体系
args.brand	string	否	默认 LSHM，品牌取业务约定
成功返回 /personnel/web/token/replace/hr-platform 的 data.tokenInfo 对象，内部字段由该平台合同确定；失败或返回结构不符时通常 resolve ''，不是 reject。原生通道异常仍应捕获，当前方法无统一超时保护。
const tokenInfo = await withBridgeTimeout(
  requireBridge('__APP_GET_TOKEN_AUTHINFO__')({ bizType: 'BizMidPlatform', brand: 'LSHM' }),
  45000,
)
if (!tokenInfo || typeof tokenInfo !== 'object') throw new Error('中台认证获取失败')
// 按中台接口合同使用 tokenInfo，不能当成普通字符串 Token。
依据：bridgeConfig.ts → getTokenAuthInfo。普通业务／门户请求不要额外调用此方法。
8.3 __APP_GO_LOGIN__：使 App 登录失效并进入登录页
__APP_GO_LOGIN__(): void
入参无，返回无。App 复用登录失效处理，提示登录过期，尝试清除业务 Token、解绑推送账号、清除用户相关缓存，再将登录页设为根路由。失败清理有内部容错，H5 不会收到逐项完成结果。
requireBridge('__APP_GO_LOGIN__')()
只用于确认认证失效后的重新登录。它不是刷新门户 Token，不是仅关闭当前页面，也没有自动回到原 H5 的承诺。并发 401 应由 H5 统一拦截、去重。依据：bridgeConfig.ts → goLogin、sessionExpire.ts。
9. 导航与容器
9.1 __APP_ROUTER_BACK__：回退当前页面
__APP_ROUTER_BACK__(): void
无参数、无返回值。若 WebView 有网页历史则后退；没有历史且宿主提供 onRootBack 时交给宿主；否则原生导航有上一页才关闭当前原生页。它不保证每次都关闭整个 WebView，也不是 history.back() 的完全等价物。
requireBridge('__APP_ROUTER_BACK__')()
依据：WebViewScreen.tsx → handleMessage、bridgeConfig.ts → goBack。
9.2 __APP_GO_HOME_TAB__：回到 App 主容器
__APP_GO_HOME_TAB__(): void
无参数、无返回值。当前实现先选择“运营指导”工作台，再 popTo('MainTabs')，复用已有主容器并移除其上层页面。不要写成“重置整个 App”或“重新执行 App 初始化”。
requireBridge('__APP_GO_HOME_TAB__')()
限制：不接受 Tab 名称或索引，不能指定跳到“我的”等任意 Tab。 当前桥也没有显式传入子 Tab 路由，主容器的具体可见 Tab 还受已有导航状态影响；若业务要求任意入口都强制选定某个 Tab，需要 App 补充明确协议并验收，不能靠 H5 多传一个参数实现。
依据：NavigationService.ts → navigateToHomeTab。
9.3 __APP_OPEN_WORKBENCH_DRAWER__：打开当前工作台抽屉
__APP_OPEN_WORKBENCH_DRAWER__(): void
无参数、无返回值。不改变 H5 路由，调用当前宿主的抽屉回调。目前 NewStoreWorkbench 提供此能力；普通二级 WebView 未必有它。
if (typeof window.__APP_OPEN_WORKBENCH_DRAWER__ === 'function') {
  window.__APP_OPEN_WORKBENCH_DRAWER__()
} else {
  // 隐藏入口，或提示该页面不支持工作台抽屉。
}
不要先回首页后继续在已销毁 H5 内调用这个方法，也不要把它当成所有页面都有的通用侧栏。依据：WebViewScreen.tsx → workbenchDrawerBridgeScript、pages/NewStoreWorkbench.tsx。
9.4 __APP_OPEN_NEW_WINDOW__：新开原生 WebView
__APP_OPEN_NEW_WINDOW__(
  url: string,
  needSafeArea?: boolean,
  needNarBar?: boolean,
  narBarTitle?: string,
): void
位置参数	必填	默认值	说明
url	是	无	完整可信 HTTPS 地址；不是 H5 相对路由
needSafeArea	否	false	是否由原生容器包安全区
needNarBar	否	false	原生导航栏配置，历史拼写不要自行改名
narBarTitle	否	''	原生导航栏标题
requireBridge('__APP_OPEN_NEW_WINDOW__')(
  'https://example.com/operation-h5/detail?id=100', true, true, '示例详情',
)
返回 undefined，无页面打开完成回执。App push 新的 WebViewScreen，自动补 mode: 'start' 和实例 ID，当前已兼容导航栏历史字段。新页面还要重新做自己的上下文初始化。不要通过 URL 传 Token。
依据：bridgeConfig.ts → openNewWindow、webViewRouteParams.ts。
9.5 __OPEN_APP_WEBVIEW__：修改当前页顶部栏
__OPEN_APP_WEBVIEW__(isShowBack?: boolean, title?: string): void
参数	默认值	说明
isShowBack	false	是否显示当前容器的返回栏
title	''	当前容器标题
requireBridge('__OPEN_APP_WEBVIEW__')(true, '门店详情')
无返回值。尽管名称里有 OPEN，它不新开 WebView，只发送 showBackButton 修改当前容器显示。最终栏位显示还受当前页面布局和宿主影响。依据：WebViewScreen.tsx。
10. 设备与页面适配
10.1 __APP_GET_VERSION__：读取安装包版本
__APP_GET_VERSION__(): Promise<string>
无参数。成功返回 DeviceInfo.getVersion() 字符串，例如 2.1.5；不是同步属性，也不是完整桥能力版本。无内置统一超时，建议包装等待。
const version = await withBridgeTimeout(requireBridge('__APP_GET_VERSION__')(), 5000)
// 用于用户反馈版本，不代替具体桥方法存在性检查。
依据：bridgeConfig.ts → getAppVersion。
10.2 __APP_GET_SAFE_AREA__：读取安全区
__APP_GET_SAFE_AREA__(): string
无参数，同步返回 JSON 字符串，不是 Promise。解析后包含 top/right/bottom/left 四边数值；按布局单位使用，不能当作物理屏幕像素。桥早期返回值、屏幕旋转后的值可能不同。
const insets = JSON.parse(requireBridge('__APP_GET_SAFE_AREA__')()) as AppInsets
window.onReactNativeSafeAreaInsetsChange = nextInsets => {
  // 更新 H5 布局；此回调收到的是对象，不再 JSON.parse。
}
必须捕获 JSON 解析失败，并避免 H5 padding 与原生 needSafeArea 重复叠加。依据：WebViewScreen.tsx。
10.3 __APP_ORIENTATION__：锁定屏幕方向
__APP_ORIENTATION__(orientation?: 'landscape' | 'portrait'): void
landscape 锁横屏并隐藏状态栏；portrait 锁竖屏并显示状态栏；不传或其他值也按竖屏处理。无结果回执。
requireBridge('__APP_ORIENTATION__')('landscape')
// 离开需要横屏的业务时，按产品要求恢复竖屏。
requireBridge('__APP_ORIENTATION__')('portrait')
该能力影响原生方向和状态栏，退出页面、前后台切换需真机验收。依据：bridgeConfig.ts → orientation。
10.4 __APP_REGISTER_KEYBOARD_LISTENER__：监听键盘
__APP_REGISTER_KEYBOARD_LISTENER__(callback: (status: KeyboardStatus) => void): void
callback 必填；数据为 { visible: boolean, height: number }。注册方法返回 undefined，没有注销函数，也不保证注册后立即推送当前状态。
requireBridge('__APP_REGISTER_KEYBOARD_LISTENER__')(status => {
  document.documentElement.style.setProperty('--app-keyboard-height', `${status.height}px`)
})
只在 H5 根模块注册一次，再自行分发。不能在组件每次渲染时注册，不能把返回值当成 unsubscribe。依据：WebViewScreen.tsx。
11. 定位与系统权限
11.1 __APP_GET_CURRENT_LOCATION__：获取当前位置
__APP_GET_CURRENT_LOCATION__(options?: LocationOptions): Promise<AppLocationResult>
参数	必填	默认值／单位	说明
options.timeout	否	40000 毫秒	本次原生定位等待时间，建议正数；不是整个 H5 桥的总超时
options.accuracy	否	不传时用 App 默认策略	high／balanced／low；未识别值不传给定位实现
当前成功结果是带扩展字段的 new String(...) 对象，不是普通 JSON 对象，也不保证 typeof result === 'string'。 失败或超时通常返回原始空字符串 ''。
成功结果字段	类型	说明
String(result)	string	latitude,longitude，保留旧 .split(',') 使用习惯
location	string	同上
latitude／longitude	number	经纬度
accuracyMeters	number 或 null	精度米数
formattedAddress	可选 string	地址，不保证有
poiName／aoiName	可选 string	兴趣点／区域名，不保证有
const result = await withBridgeTimeout(
  requireBridge('__APP_GET_CURRENT_LOCATION__')({ timeout: 40000, accuracy: 'balanced' }),
  45000,
)
const text = String(result || '')
if (!text) throw new Error('未获取到定位，请检查权限和系统定位开关')
const [latitude, longitude] = text.split(',').map(Number)
if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) throw new Error('定位结果格式异常')
const accuracyMeters = typeof result === 'object' ? result.accuracyMeters : null
不要再用旧写法 __APP_GET_CURRENT_LOCATION__(40000)；当前参数是对象。App 有短时定位缓存，不承诺每次调用都是新的 GPS 采样。坐标系、地图厂商及精度满足业务要求与否需单独确认。
依据：WebViewScreen.tsx、bridgeConfig.ts → getLocation、locationHelper.ts。
11.2 __APP_GET_CURRENT_ADDRESS__：读取 App 缓存地址
__APP_GET_CURRENT_ADDRESS__(timeout?: number): Promise<string>
参数 timeout 在注入函数中默认 40000 毫秒，但当前原生处理器不使用它。返回 userStore.address 或 ''，不是主动定位或逆地理编码结果，没有新鲜度保证。
const address = await withBridgeTimeout(requireBridge('__APP_GET_CURRENT_ADDRESS__')(), 5000)
if (!address) {
  // 显示地址不可用，不能把空字符串当认证错误。
}
依据：bridgeConfig.ts → getAddress。
11.3 __APP_GET_PERMISSION_LOCATION__：检查定位权限
__APP_GET_PERMISSION_LOCATION__(): Promise<AppPermissionStatus | ''>
无参数，只检查权限，不主动申请。返回定位权限状态；检查异常时可能返回 ''，不可视为已授权。
const status = await withBridgeTimeout(requireBridge('__APP_GET_PERMISSION_LOCATION__')(), 5000)
if (status === 'blocked') {
  // 向用户说明原因，再由用户点击打开设置。
}
权限通过也不保证系统定位开关已开启或能获得有效坐标。依据：bridgeConfig.ts → getPermissionNow。
11.4 __APP_NOTIFICATION_PERMISSION__：检查通知权限
__APP_NOTIFICATION_PERMISSION__(): Promise<AppPermissionStatus>
无参数，返回 checkNotifications().status，只检查不申请。平台异常没有统一失败回调保证，H5 应包等待超时。
const status = await withBridgeTimeout(requireBridge('__APP_NOTIFICATION_PERMISSION__')(), 5000)
不要调用通用权限桥并传 NOTIFICATION，当前映射没有该值。依据：bridgeConfig.ts → checkNotificationPermission。
11.5 __APP_CHECK_OR_REQUEST_PERMISSION__：检查或申请权限
__APP_CHECK_OR_REQUEST_PERMISSION__(args: PermissionArgs): Promise<AppPermissionStatus>
参数	类型	必填	默认值／说明
permission	CAMERA／LOCATION／PHOTO／MICROPHONE／CONTACTS	是	大写权限名称
requestDirectly	boolean	否	默认 false 只检查；true 调用系统权限申请
const status = await withBridgeTimeout(
  requireBridge('__APP_CHECK_OR_REQUEST_PERMISSION__')({ permission: 'CAMERA', requestDirectly: true }),
  60000,
)
if (status !== 'granted') {
  // 按下表提示，不自动反复申请。
}
状态	接入含义
granted	已授权
limited	有限授权，照片等能力可能只有部分可访问内容
denied	未授权；是否可再次弹框取决于系统及请求历史
blocked	通常需要用户在系统设置中修改
unavailable	当前系统／设备不提供该权限能力
不支持的名称会 reject 字符串（例如 … not supported）；检查或申请异常会 reject permission check/request failed。不要假设 catch 值一定具有 .message。
Android 的 PHOTO 在较新系统映射为图片权限，不是“所有图片和视频都已授权”的证明。具体 SDK 选择器能力与平台差异要真机确认。依据：bridgeConfig.ts → PERMISSION_MAP / checkOrRequestPermission。
11.6 __APP_OPEN_SETTING__：打开系统 App 设置
__APP_OPEN_SETTING__(): void
无参数、无返回值。App 调用系统 openSettings；H5 不会收到用户是否修改权限的结果。
requireBridge('__APP_OPEN_SETTING__')()
用户从设置回到 App 后重新检查权限；不要调用一次就认为已经授权。依据：bridgeConfig.ts → openLocationSetting。
12. 媒体、上传与签名：新项目优先使用
12.1 三个媒体 Promise 方法的公共结果
相册、拍照、录像的新方法都由 App 选择／拍摄并上传，返回上传后的文件信息，不是只选择本地文件交给 H5 上传。
interface MediaBridgeResult {
  success: boolean
  data: UploadedFile[]
  error?: string
}

interface UploadedFile {
  name: string
  url: string
  path: string
  fileUrl: string
  fileSize: number
  contentType: string
  fileExtension: string
  key: string
  status: 'success' | 'error'
  error?: string
}
返回字段	含义
顶层 success	整个操作是否进入正常结果回传；为 true 时仍可能有文件失败
data	文件结果数组，可能为空
顶层 error	常见为 cancel、picker_failed、recording_failed、大小限制提示等；不是封闭枚举
文件 status	单个文件真实上传状态，必须逐个检查
fileUrl／url／path	新协议成功文件通常为同一个远程文件地址，不是本地相机路径
fileSize	文件大小数值，通常按字节消费；缺失时可能为 0，不能当严格校验结果
contentType／fileExtension	服务返回的 MIME／扩展名，可能为空
key	文件任务标识，不等于业务数据 ID
建议共用结果判断：
function getSuccessfulFiles(result: MediaBridgeResult): UploadedFile[] {
  if (!result.success) {
    if (result.error === 'cancel') return []
    throw new Error('媒体操作失败，请重试')
  }
  return result.data.filter(file => file.status === 'success' && Boolean(file.fileUrl))
}
还应对 result.data 中的失败文件给出提示，不能仅过滤后悄悄忽略。上传完成不等于业务单据保存完成，仍需 H5 提交自己的业务表单。
交互等待可能包含用户拍摄和多个文件上传，不要机械地给所有媒体桥设置 5 秒／15 秒超时。若设置 H5 超时，提示“操作仍可能在 App 中进行”，不要自动重复打开选择器。
12.2 __APP_OPEN_PICKER_WITH_RESULT__：选择相册并上传
__APP_OPEN_PICKER_WITH_RESULT__(args?: PickerArgs): Promise<MediaBridgeResult>
参数	类型	必填	默认值／说明
count	number	建议传	> 1 启用多选；不传时按单选；最终返回最多 count 项
mediaType	photo／video／any	否	默认 photo
fileSizeLimit	number	否	单文件上限 MB，按 1024 × 1024 换算；不传则不加此层限制
uuid	string	否	业务标识；新 Promise 结果不保证原样回传，不靠它关联并发
proName／brand	string	否	当前外层容器会接收，但此新相册处理器没有旧相册的水印合成逻辑
超大文件会被过滤并提示；全部超限返回 success: false, data: []。取消通常返回 error: 'cancel'。上传阶段可出现顶层成功、部分文件 status: 'error'。
const result = await requireBridge('__APP_OPEN_PICKER_WITH_RESULT__')({
  count: 3,
  mediaType: 'photo',
  fileSizeLimit: 20,
})
const files = getSuccessfulFiles(result)
const failedCount = result.data.filter(file => file.status === 'error').length
// 显示 files；failedCount > 0 时提示部分上传失败。
此方法仍可能调用旧的 onOpenPickerCallback。如果项目还没有统一注册，可以在根模块注册空函数兼容，避免旧通知产生控制台错误；实际上传结果以 Promise 为准。
window.onOpenPickerCallback ??= () => {}
不要给新相册方法传旧协议的水印开关并承诺水印生效。需要水印时先与 App 确认方案。依据：bridgeConfig.ts → openPickerWithResult、helper.ts → uploadFilesWithResult。
12.3 __APP_GO_TO_CAMERA_WITH_RESULT__：拍照并上传
__APP_GO_TO_CAMERA_WITH_RESULT__(args?: CameraArgs): Promise<MediaBridgeResult>
参数	类型	必填	默认值／说明
count	number	否	总数量上限；不传／无效值按 1
number	number	否	当前已有数量，默认 0；剩余可拍数量与 count 联动
uuid	string	否	旧业务批次标识；Promise 结果不保证回传
proName	string	否	默认空字符串；水印项目／门店文案
brand	string	否	默认空字符串；水印品牌文案
fileSizeLimit	number	否	单文件 MB 上限；不传不加此层限制
cameraPosition	front／back	否	前／后摄像头，默认行为由 App 相机决定
cameraTip	CameraTip	否	自定义相机提示；见下表
cameraTip 字段	类型	默认值／说明
title	string	标题；与 subtitle 都为空时不显示提示块
subtitle	string	副标题；注意不是 content
marginTop	number 或数字字符串	默认 90，App 布局偏移单位
titleStyle.color／subtitleStyle.color	string	文本颜色
titleStyle.fontSize／subtitleStyle.fontSize	number 或数字字符串	字号
titleStyle.lineHeight／subtitleStyle.lineHeight	number 或数字字符串	行高
window.onOpenCameraCallback ??= () => {}
const result = await requireBridge('__APP_GO_TO_CAMERA_WITH_RESULT__')({
  count: 3,
  number: 0,
  fileSizeLimit: 20,
  proName: '示例门店',
  cameraPosition: 'back',
  cameraTip: { title: '拍摄门店正面', subtitle: '请保持门头完整、文字清楚' },
})
const files = getSuccessfulFiles(result)
相机完成后汇总返回文件结果；返回／取消通常为 { success: false, data: [], error: 'cancel' }。原生权限、上传异常可能由相机页提示并保留页面，不保证每次弹提示都会立即结束 Promise。按每个文件的 status 判断上传结果。
依据：bridgeConfig.ts → goToCameraWithResult、pages/Camera/index.tsx。
12.4 __APP_OPEN_TRANSCRIBE_WITH_RESULT__：录制视频并上传
__APP_OPEN_TRANSCRIBE_WITH_RESULT__(args?: VideoArgs): Promise<MediaBridgeResult>
参数	类型	必填	默认值／说明
uuid	string	否	业务标识；新 Promise 结果不保证回传
fileSizeLimit	number	否	单文件 MB 上限；不传不加此层限制
当前录制页只明确消费以上业务参数。不要把相机的 count、cameraTip 或相册的 mediaType 当成该页已实现的功能。
window.onOpenTranscribeCallback ??= () => {}
const result = await requireBridge('__APP_OPEN_TRANSCRIBE_WITH_RESULT__')({ fileSizeLimit: 100 })
const files = getSuccessfulFiles(result)
成功返回视频上传文件数组；取消通常返回 error: 'cancel'，录制失败可返回 recording_failed。大小超限、相机／麦克风不可用等也可能在原生页显示提示，等待用户后续处理。上传逐项状态仍需检查。
依据：bridgeConfig.ts → openTranscribeWithResult、pages/VideoShoot/index.tsx。
12.5 __APP_OPEN_SIGNATURE__：手写签名
__APP_OPEN_SIGNATURE__(args?: SignatureArgs): Promise<SignatureResult>
参数	类型	必填	默认值／说明
penColor	string	否	#000000
penWidth	number	否	4，传正数
placeholder	string	否	“请在空白区域内横向书写”
returnBase64	boolean	否	false，是否请求额外 Base64
title	string	否	“手写签名”
返回字段	类型	说明
success	boolean	是否成功
fileUrl	可选 string	上传成功的签名图地址
base64	可选 string	签名图数据，不能打印或写入日志
localFilePath	可选 string	App 本地文件路径，H5 不应假设能直接 fetch
reason	可选 string	失败原因，例如 cancelled、timeout 或上传错误
const result = await requireBridge('__APP_OPEN_SIGNATURE__')({
  title: '门店确认签名', penColor: '#000000', penWidth: 4, returnBase64: false,
})
if (!result.success) {
  if (result.reason !== 'cancelled') throw new Error('签名未完成，请重试')
} else if (!result.fileUrl) {
  throw new Error('签名未返回可保存的文件地址')
}
原生等待 5 分钟后返回 success: false, reason: 'timeout'；常规取消／失败通过结果返回，不是统一 reject。但 JSON 序列化或通道异常仍可能使调用抛错，外层仍要捕获。
不要并发打开多个签名页；不要把超时理解为原生签名页必然自动关闭。依据：bridgeConfig.ts → openSignature。
13. 旧媒体与文件协议：仅在兼容或特定需求时使用
13.1 先认识回调，避免把“打开成功”当成“上传成功”
旧方法返回 void，上传结果经 window.receiveRNData 回传。onOpen…Callback 当前通常收到字符串 'true'／'false'，必须精确比较，Boolean('false') 仍然是 true。
先在根模块注册，再发起操作：
window.onOpenCameraCallback = value => { /* value === 'true' 表示入口通知 */ }
window.onOpenPickerCallback = value => { /* 不在这里保存业务附件 */ }
window.onOpenTranscribeCallback = value => { /* 也可能是录制取消／失败通知 */ }
window.onOpenFilePickerCallback = value => { /* 只表示文件入口通知 */ }
window.receiveRNData = data => {
  if (data.uuid !== 'demo-batch') return
  if (data.status === 'progress') {
    // 依据 key 更新进度，rnProgress 可能缺失。
  } else if (data.status === 'success' || (data.eventType === 'video' && data.status === 'complated')) {
    // 验证 fileUrl，再添加附件。complated 是现有视频协议的历史拼写。
  } else if (data.status === 'cancel' || data.status === 'error') {
    // 分别处理取消和失败，不把取消强制弹成错误。
  }
}
receiveRNData 字段	类型	说明
uuid	可选 string	调用时业务批次 ID
key	可选 string	文件任务 ID；有 key 后可用于取消
eventType	可选 string	常见 cameraCallback、pickerCallback、video，不要假设所有方法统一
status	可选 string	常见 progress／success／error／cancel；旧视频成功还可能为 complated
rnProgress	可选数值	转发上传进度；并非每种媒体都会回传；以实际事件确认范围
fileUrl／url／path	可选 string	远程文件地址
name	可选 string	由上游 fileName 转发，可能缺失
contentType／fileExtension	可选 string	文件类型信息
fileSize	可选 number	文件大小
totalFileCount	可选 number	批次总量，不保证每种操作都有
error	可选 string	失败原因
旧文件选择取消可能没有完整结束事件；旧视频错误可能只通知 onOpenTranscribeCallback('false')。不要把所有旧方法统一封成“必定 resolve／reject”的 Promise。
13.2 __APP_OPEN_PICKER__：旧相册选择与上传
__APP_OPEN_PICKER__(jsonArgs: string): void
推荐传 JSON 字符串，当前也兼容对象；为避免新老包差异，本文类型只推荐字符串。
JSON 字段	类型	默认值／说明
uuid	string	建议必传，用于回调关联
count	number	建议明确传正整数；大于 1 多选
mediaType	photo／video／any	默认 photo
fileSizeLimit	number	单文件 MB 上限，可不传
watermark／needWatermark／addWatermark	布尔值、0／1 或对应字符串	是否申请旧相册图片水印；推荐只传一个布尔开关
proName／brand	string	水印文案
requireBridge('__APP_OPEN_PICKER__')(JSON.stringify({
  uuid: 'demo-batch', count: 3, mediaType: 'photo', fileSizeLimit: 20,
  watermark: true, proName: '示例门店',
}))
回调为 onOpenPickerCallback 和 receiveRNData。只有图片与对应开关条件满足时尝试加水印；GIF／视频会跳过，水印生成失败可能回退原图，不能用于必须保证水印的合规证明。
依据：WebViewScreen.tsx → openPicker 分支、bridgeConfig.ts → openPicker。
13.3 __APP_GO_TO_CAMERA__：旧拍照与上传
__APP_GO_TO_CAMERA__(jsonArgs: string): void
JSON 参数与 12.3 的 CameraArgs 一致，建议增加唯一 uuid；count 默认 1、number 默认 0。当前也兼容对象，但新老包接入建议统一 JSON 字符串。
requireBridge('__APP_GO_TO_CAMERA__')(JSON.stringify({
  uuid: 'demo-batch', count: 2, number: 0, cameraPosition: 'back', fileSizeLimit: 20,
}))
通过 onOpenCameraCallback 接收入口通知，receiveRNData 按文件接收上传状态，不是汇总返回数组。依据：bridgeConfig.ts → goToCamera、相机页。
13.4 __APP_OPEN_TRANSCRIBE__：旧视频录制与上传
__APP_OPEN_TRANSCRIBE__(jsonArgs: string): void
必须 JSON 字符串；业务参数为 uuid、fileSizeLimit，含义同 12.4。不要直接传对象给原生 JSON.parse 分支。
requireBridge('__APP_OPEN_TRANSCRIBE__')(JSON.stringify({ uuid: 'demo-batch', fileSizeLimit: 100 }))
入口／部分失败经 onOpenTranscribeCallback；上传成功可经 receiveRNData 返回 eventType: 'video', status: 'complated'。不要只监听 status === 'success'。依据：bridgeConfig.ts → openTranscribe、视频页。
13.5 __APP_OPEN_FILE_PICKER__：文件选择并上传
__APP_OPEN_FILE_PICKER__(jsonArgs: string): void
JSON 字段	类型	必填	默认值／说明
uuid	string	建议	业务回调批次 ID
count	number	建议	上传数量上限，正整数；不传则使用所选文件数量
type	string[]	否	默认全部文件；使用 MIME 类型，例如 application/pdf
allowMultiSelection	boolean	否	默认 true；count 主要限制后续结果，不等于系统选择器 UI 上限
fileSizeLimit	number	否	单文件上限 MB
dir	boolean	否	默认 false；true 虽有目录入口，但没有完整文件数组上传回调保证，不推荐
requireBridge('__APP_OPEN_FILE_PICKER__')(JSON.stringify({
  uuid: 'demo-batch', count: 1, type: ['application/pdf'],
  allowMultiSelection: false, fileSizeLimit: 20, dir: false,
}))
结果经 onOpenFilePickerCallback 和 receiveRNData。系统取消、类型不符等分支可能只提示或直接结束，不保证收到统一 cancel 事件；需要 H5 可手动恢复忙碌状态。没有公开的 __APP_OPEN_FILE_PICKER_WITH_RESULT__，不要自行调用这个不存在的方法。
依据：bridgeConfig.ts → openFilePicker。
13.6 __APP_CANCEL_REQUEST__：取消已知上传任务
__APP_CANCEL_REQUEST__(key: string): void
key 必填，来自文件上传事件，不是业务 UUID，也不是整个批次 ID。无返回值，不提供取消成功回执。
// uploadKey 应取自 receiveRNData 中当前文件的 key。
const uploadKey = '示例任务标识'
requireBridge('__APP_CANCEL_REQUEST__')(uploadKey)
适用于旧事件流已获得 key 的任务；新媒体 Promise 完成前通常还拿不到逐文件 key，不能据此提供通用“取消当前原生拍摄”的能力。依据：bridgeConfig.ts → cancelRequest。
14. 预览、文件与系统操作
14.1 __APP_SCAN_CODE__：扫码
__APP_SCAN_CODE__(args?: Record<string, never>): Promise<ScanResult>
当前没有对外业务参数，直接不传。成功返回 { success: true, data: string }；取消／失败通常返回 { success: false }，不是返回裸文本。
const result = await requireBridge('__APP_SCAN_CODE__')()
if (result.success && result.data) {
  // 根据业务白名单解析扫码内容，不直接执行二维码内的地址或脚本。
}
没有统一交互超时，按钮防重复点击；旧包返回形式如需兼容，另按目标安装包实测，不把旧宽松联合类型当成当前保证。依据：bridgeConfig.ts → scanCode、useScanner.ts。
14.2 __APP_PREVIEW_IMAGE__：图片预览
__APP_PREVIEW_IMAGE__(args: { urls: string[] | string; current?: number | string }): void
urls 必填，推荐非空 URL 数组；单字符串会转成数组。current 可为从 0 开始的索引或数组中某个 URL；缺失、URL 未找到时从首张显示，数值越界由 App 裁剪。
requireBridge('__APP_PREVIEW_IMAGE__')({
  urls: ['https://example.com/a.jpg', 'https://example.com/b.jpg'], current: 1,
})
无返回值，空数组直接不打开；关闭预览没有公共完成回调。依据：bridgeConfig.ts → previewImage、ImagesPreview.tsx。
14.3 __APP_PREVIEW_VIDEO__：视频预览
__APP_PREVIEW_VIDEO__(args: { url: string }): void
url 必填，为 App 可访问的视频地址。返回 undefined；缺地址时直接不打开，没有播放结束回调。
requireBridge('__APP_PREVIEW_VIDEO__')({ url: 'https://example.com/demo.mp4' })
能否播放取决于编码、网络和平台，不是浏览器能播就保证 App 可播。依据：bridgeConfig.ts → previewVideo。
14.4 __APP_DOCUMENT_VIEW__：文档预览
__APP_DOCUMENT_VIEW__(args: { url: string; type?: string; title?: string }): Promise<never>
参数	必填	说明
url	是	App 可访问的文件地址
type	否	扩展类型，不带点；doc、xls 走外部系统能力，其他值进入 App 文档页
title	否	App 文档页标题
当前函数虽然创建 Promise，但没有 resolve／reject 完成通道，正常调用不会结束等待。必须按“只打开，不等待”使用。
void requireBridge('__APP_DOCUMENT_VIEW__')({ url: 'https://example.com/demo.pdf', type: 'pdf', title: '示例文件' })
没有预览成功／关闭回调；外部应用未安装或文件不可达时由 App 提示或预览页处理。不要在它后面 await 再关 loading。依据：WebViewScreen.tsx、bridgeConfig.ts → documentView。
14.5 __APP_OPEN_FILE__：通过系统打开链接
__APP_OPEN_FILE__(url: string): void
url 必填，当前处理器要求 http:// 或 https:// 开头；否则提示无法打开文件。无完成返回，不会将文件内容回传 H5。
requireBridge('__APP_OPEN_FILE__')('https://example.com/demo.pdf')
是否能打开取决于系统关联和已安装应用。与上一个方法不同，它不按 type/title 创建 App 文档页。依据：bridgeConfig.ts → openFile。
14.6 __APP_IMAGE_TO_DATA_URL__：读取远程图片为 data URL
__APP_IMAGE_TO_DATA_URL__(url: string): Promise<string>
url 必填。App 下载图片并返回 data:image/...;base64,... 字符串，可供需要本地图片数据的 H5 绘图／截图流程使用；不是任意文件代理。
const dataUrl = await withBridgeTimeout(
  requireBridge('__APP_IMAGE_TO_DATA_URL__')('https://example.com/report.png'), 45000,
)
失败通常 reject 字符串 image_to_data_url_failed。大图片会增加内存占用；只传可信图片地址，不在 URL 放认证凭据，不输出返回内容。依据：bridgeConfig.ts → imageToDataUrl、helper.ts → imageUrlToDataUrl。
14.7 __APP_PHOTO_DOWNLOAD__：保存图片到系统相册
__APP_PHOTO_DOWNLOAD__(url: string): void
url 必填，为可下载图片地址。App 尝试保存并自行提示，H5 不接收保存成功／失败结果。
requireBridge('__APP_PHOTO_DOWNLOAD__')('https://example.com/report.png')
用户可能需要授权，方法返回不代表已保存。依据：bridgeConfig.ts → photoDownload、helper.ts → saveImageToGallery。
14.8 __APP_CALL_PHONE__：唤起拨号
__APP_CALL_PHONE__(phone: string): void
phone 必填，电话号码字符串，不传对象。系统拨号操作，无通话结果回调。
requireBridge('__APP_CALL_PHONE__')('10086')
号码来源必须可信，用户点击后调用；模拟器或无通话能力设备不保证可用。依据：bridgeConfig.ts → call。
14.9 __APP_COPY_TEXT__：复制文本
__APP_COPY_TEXT__(text: string): void
text 必填，字符串。App 写剪贴板并自行提示，没有成功返回值。
requireBridge('__APP_COPY_TEXT__')('示例门店编号：DEMO001')
不要复制 Token、刷新凭据等敏感信息到系统剪贴板。依据：bridgeConfig.ts → copyText。
14.10 __APP_OPEN_MAP__：唤起外部地图导航
__APP_OPEN_MAP__(args: { params: MapNavigationArgs }): void
注意外层 params 必须保留，区别于大多数直接传对象的桥。
字段	必填	类型／说明
params.map	是	baidu／amap／qqmap／apple
params.from.lat／from.lng	是	起点纬度／经度，数字
params.to.lat／to.lng	是	终点纬度／经度，数字
params.from.name	否	默认“我的位置”
params.to.name	否	默认“目的地”
requireBridge('__APP_OPEN_MAP__')({ params: {
  map: 'amap',
  from: { lat: 28.1, lng: 112.9, name: '当前位置' },
  to: { lat: 28.2, lng: 113.0, name: '示例门店' },
} })
无返回值。App 根据地图 scheme 调起已安装应用；未安装会提示，不保证降级网页地图。apple 仅适用于具备该能力的平台；不同地图的坐标系和起点使用方式需业务确认，不能盲目混用经纬度。
依据：bridgeConfig.ts → openMap、helper.ts → openMapNavigation。
15. 业务专用桥
以下方法会进入真实业务流程，可能修改 App 业务状态或发起建单、打卡等操作。只在对应业务接入时使用，不作为通用导航工具，也不要用生产账号随意测试。
15.1 __APP_OPEN_REPORT_SHARE__：打开报告分享面板
__APP_OPEN_REPORT_SHARE__(args: ReportShareArgs): void
参数	类型	必填条件／说明
imageUrl	string	已生成报告图；保存图片时需要它或下方延迟生成协议
requestId	string	没有 imageUrl、需要延迟生成时必填；一次任务唯一
title	string	可选，企微转发卡片标题
fileName	string	可选，保存图片文件名
shareUrl	string	企微页面分享时需要，不能带认证信息
description	string	可选，卡片说明
thumbUrl	string	可选，公网 HTTP(S) 缩略图，不支持 Base64
requireBridge('__APP_OPEN_REPORT_SHARE__')({
  imageUrl: 'https://example.com/report.png',
  title: '示例门店报告', fileName: 'report.png',
  shareUrl: 'https://example.com/report/100',
  thumbUrl: 'https://example.com/thumb.png', description: '示例报告说明',
})
无分享完成回执。组件内部虽然还有 modalTitle 属性，但当前 H5 桥处理器没有转发，不能把它写成 H5 可用参数。依据：bridgeConfig.ts → openReportShare、ReportShareBottomSheet.tsx。
15.2 __APP_REPORT_SHARE_IMAGE_READY__：回传延迟生成的报告图
__APP_REPORT_SHARE_IMAGE_READY__(args: ReportShareImageResult): void
参数	必填	说明
requestId	是	与打开分享面板的任务 ID 完全一致
success	是	图片生成是否成功
imageUrl	成功时	已上传、App 可访问的图片 URL
message	否	失败时可读的提示文字
完整流程：注册 H5 生成函数 → 打开分享面板 → 用户点击保存 → App 调用 H5 生成函数 → H5 上传图片 → 用此桥通知 App。不是 Promise 返回图片给 App。
// uploadReportImage 为 H5 实际实现的截图及上传函数。
function registerReportImageGenerator(uploadReportImage: () => Promise<string>): void {
  window.__H5_GENERATE_REPORT_SHARE_IMAGE__ = async requestId => {
    try {
      const imageUrl = await uploadReportImage()
      requireBridge('__APP_REPORT_SHARE_IMAGE_READY__')({ requestId, success: true, imageUrl })
    } catch {
      requireBridge('__APP_REPORT_SHARE_IMAGE_READY__')({
        requestId, success: false, message: '报告图片生成失败，请重试',
      })
    }
  }
}

// 先调用 registerReportImageGenerator 注册业务实现，再打开面板。
requireBridge('__APP_OPEN_REPORT_SHARE__')({ requestId: 'demo-report-task-1', title: '示例报告' })
面板已关闭或 requestId 不匹配时结果会被忽略。没有统一的 H5 生成超时回收保证，生成逻辑自身必须结束或回报失败；不要同时打开多个互相覆盖的分享任务。
依据：ReportShareBottomSheet.tsx → saveImage / handleImageReady。
15.3 __APP_PATROL_START_INSPECTION__：开始巡店
__APP_PATROL_START_INSPECTION__(args?: PatrolArgs): Promise<PatrolResult>
App 负责检查登录、当前进行中记录、定位与业务流程。可能返回打卡／排班提示页面，不保证直接进入巡店填写页。
参数	类型	默认值／说明
autoNavigate	boolean	默认 true：App 自动新开结果页面；false：只返回 URL，由 H5 决定导航
needSafeArea	boolean	可选，自动打开新 WebView 时使用
needNarBar／narBarTitle	boolean／string	可选，自动打开新 WebView 的导航栏配置
closeTarget	PatrolCloseTarget	退出目标，见下表；未传时沿用巡店自身默认逻辑
closeRoute	string	H5 退出目标路径，和 closeTarget 配合，使用有效业务路径
entrySource	string	来源标记，便于业务区分
closeTarget	含义
APP_HOME	回 App 首页方向的退出流程
SOURCE_WEBVIEW	回来源 WebView
SOURCE_H5_ROUTE	回来源 H5 路由
SOURCE_H5_RELAUNCH	按来源 H5 路由重建 H5 页面栈
关闭语义由巡店结果 H5 配合执行，不代表桥本身可以任意操作其他 H5 路由。
const result = await requireBridge('__APP_PATROL_START_INSPECTION__')({
  autoNavigate: false, closeTarget: 'SOURCE_H5_RELAUNCH',
  closeRoute: '/pages/storInspection/storInspection', entrySource: 'example-h5',
})
if (result.code === 'CANCELLED') {
  // 用户取消或重复请求被拦截，不再导航。
} else if (result.success && result.url) {
  // 校验 URL 属于本业务后，交给 H5 Router；不要在 autoNavigate:true 时再打开一次。
}
当前开始巡店有并发拦截，第二次调用可返回 CANCELLED，不是等待并共享第一笔结果。业务建单有副作用，不应自动重复调用。依据：patrolBridgeHandlers.ts。
15.4 __APP_PATROL_CONTINUE_INSPECTION__：继续巡店
__APP_PATROL_CONTINUE_INSPECTION__(args?: PatrolArgs): Promise<PatrolResult>
参数与 15.3 完全一致。App 查询／恢复当前进行中的巡店流程；未找到记录时会执行一次内部刷新后再判断，不是新建任意巡店单据。
const result = await requireBridge('__APP_PATROL_CONTINUE_INSPECTION__')({
  autoNavigate: true, closeTarget: 'APP_HOME', entrySource: 'example-h5',
})
// autoNavigate:true 时不要再次用 result.url 新开页面。
开始与继续巡店的公共返回：
字段	类型	说明
success	boolean	流程是否正常返回；CANCELLED 也可能为 true
code	PatrolCode	下表中的流程结果
url	可选 string	目标页面地址
recordId	可选 string 或 number	巡店记录 ID，不保证每条流程都有
message	可选 string	提示文字
appToastShown	可选 boolean	true 时 App 已提示，不重复 Toast；缺失不证明 App 没提示
code	H5 处理
OPEN_WEBVIEW	有结果页面；结合 autoNavigate 决定是否自己导航
SIGN_IN_CLOCK	转打卡相关页
SCHEDULE_REMINDER	转排班提醒相关页
CANCELLED	正常结束本次等待，不作失败提交
TOAST	App 已有流程提示，避免重复弹出
USER_NOT_READY	用户资料未就绪
ERROR	流程异常，展示错误或允许用户重试
该协议没有所有步骤的统一超时与取消桥；继续巡店按钮也应防重复点击。依据：patrolBridgeHandlers.ts、types/patrol.ts。
15.5 __APP_ACTION__：打开选址商圈／点位
__APP_ACTION__(target: 'shopcircle' | 'point', action: string, id: string | number): void
三个位置参数均需提供。target 决定商圈／点位详情接口，action 是当前选址业务约定的动作字符串，id 是该对象业务 ID。App 查询详情、更新地图 Store 并打开地图页。
requireBridge('__APP_ACTION__')('point', 'detail', 10001)
无结果回调；接口失败由 App 提示。不是通用 action 执行器，不能用来导航到任意 App 页面。detail 示例需与选址业务约定匹配。依据：WebViewScreen.tsx → list。
15.6 __APP_LOCATION__：按位置进入 App 选址地图
__APP_LOCATION__(args: AppMapLocationArgs): void
参数	必填	类型／说明
target	是	固定 location
latitude／longitude	是	数字，经纬度
city	是	城市名字符串
cityCode	是	城市代码字符串；当前该分支也用它设置 adcode
adcode	否	虽被解构，但当前分支未按独立区县编码使用；不可依赖
icon	否	地图标记图标 URL，未传则用 App 默认图标
requireBridge('__APP_LOCATION__')({
  target: 'location', latitude: 28.1, longitude: 112.9,
  city: '示例城市', cityCode: '430100',
})
无返回值，会改变 App 全局地图相关状态并新开地图页面。它不是“获取当前位置”；需要读定位请用 11.1。依据：WebViewScreen.tsx → list / location。
15.7 选择器与其他内部 action 的边界
代码中还有 onSelectorConfirm、openPage、uniPages、showAlert 等内部 action，但当前没有对应稳定公共 window 方法。新 H5 不应直接拼这些消息。
专用选择器项目继续使用原有配套协议，包括 appLocalZoneChanged、局部“全部战区”等语义；不要让局部选择覆盖 App 全局战区。若新项目需要通用选择器或指定 Tab 导航，应由 App 新增公开方法、定义结果与权限边界后再写入本手册。
附录 A：完整 TypeScript 声明
保存为 H5 项目的 app-bridge.d.ts，并确认位于 tsconfig.json 的 include 范围内。下列声明可整体复制，不依赖 App 项目里的 @/ 类型路径。
说明：
● 所有 window 桥都声明为可选，真实调用前必须检查。
● AppContext 描述可能不完整的旧注入；ReadyAppContext 描述当前公共异步桥成功结果。
● 原始门户响应是可扩展数据，不将单个用户样例的所有字段都声明成必填。
● 表示公共 API 的类型没有 callbackId；这是 App 注入代码内部生成的字段。
● 字段类型反映当前协议，不代表业务校验已完成；例如空字符串、空权限、null 设备都要按业务处理。
export {}

declare global {
  interface PortalUserInfo {
    id?: string | number
    nickName?: string
    isInitPassword?: boolean
    accessTokenExpireTime?: string | number
    /** 敏感透传字段：不打印、不自行用它建立刷新协议。 */
    refreshToken?: string
    refreshTokenExpireTime?: string | number
    userTypeIdList?: Array<{ userType: number; userId: string | number }>
    [field: string]: unknown
  }

  interface PersonnelUserInfo {
    orgId: string
    organizationName: string
    phone: string
    realName: string
    thirdUid: string
    userCode: string
    userId: string | number
    userName: string
    userStatus: string
    userType: string
    weights: number
    workPost: string
    workPostName: string
  }

  interface PersonnelContext {
    accessToken: string
    permissionCodes: string[]
    userInfo: PersonnelUserInfo
  }

  interface ResourceObjectDimension {
    objectKey?: string | number
    objectType?: string
    values?: unknown[]
  }

  interface PortalResourceNode {
    id?: string | number
    key?: string | number
    code?: string
    name?: string
    label?: string
    appId?: string | number
    appCode?: string
    parentId?: string | number | null
    children?: PortalResourceNode[]
    resourceTreeSimpleVO?: PortalResourceNode[]
    riskLevel?: string | number
    isShow?: string | number | boolean
    isPermission?: boolean
    ispermission?: string | boolean
    hasPermission?: string | number | boolean
    resourceObjectDimensions?: ResourceObjectDimension[] | null
    resourceObjectDimensionVOS?: ResourceObjectDimension[] | null
    /** uri、path、type、sort、action 等原始接口扩展字段。 */
    [field: string]: unknown
  }

  interface PortalAuthContext {
    portalAuthCodes: string[]
    resourceTree: PortalResourceNode[]
    resourceIds: Array<string | number>
  }

  interface AppDeviceInfo {
    id: string
    type: 'APP'
    platform: 'IOS' | 'AND' | 'WEB'
    appVersion: string
    systemVersion: string
    model: string
    deviceName: string
  }

  interface SelectedZoneInfo {
    id?: string | number
    name?: string
    parentId?: string | number | null
    orgType?: string | number
    orgCode?: string
    leaderId?: string | number
    leaderName?: string
    userCode?: string
    path?: string
    type?: string
    isOptional?: boolean
    zoneUserId: string | null
    zoneUserCode: string | null
    [field: string]: unknown
  }

  interface AppContext {
    unifiedPortal: { accessToken: string; userInfo: PortalUserInfo }
    deviceInfo: AppDeviceInfo | null
    zoneOwnerInfo: {
      zoneUserId: string | null
      zoneUserCode: string | null
      selectedZoneInfo: SelectedZoneInfo | null
    }
    personnel?: PersonnelContext
    portalAuthObj?: PortalAuthContext
  }

  interface ReadyAppContext extends AppContext {
    personnel: PersonnelContext
    portalAuthObj: PortalAuthContext
  }

  interface AppBridgeError extends Error { code?: string }

  interface TokenAuthInfoArgs {
    bizType?: 'BizMidPlatform'
    brand?: string
  }

  interface AppInsets { top: number; right: number; bottom: number; left: number }
  interface KeyboardStatus { visible: boolean; height: number }

  interface AppLifecyclePayload {
    version: 1
    sequence: number
    state: 'background' | 'active'
    /** 毫秒时间戳。 */
    changedAt: number
    backgroundAt: number | null
    activeAt: number | null
  }

  interface LocationOptions {
    /** 毫秒，默认 40000。 */
    timeout?: number
    accuracy?: 'high' | 'balanced' | 'low'
  }

  /** 当前成功结果为装箱 String，特意不声明成原始 string。 */
  interface AppLocationValue extends String {
    location: string
    latitude: number
    longitude: number
    accuracyMeters: number | null
    formattedAddress?: string
    poiName?: string
    aoiName?: string
  }
  type AppLocationResult = AppLocationValue | ''

  type AppPermissionStatus = 'unavailable' | 'denied' | 'blocked' | 'granted' | 'limited'
  interface PermissionArgs {
    permission: 'CAMERA' | 'LOCATION' | 'PHOTO' | 'MICROPHONE' | 'CONTACTS'
    requestDirectly?: boolean
  }

  interface PickerArgs {
    uuid?: string
    count?: number
    mediaType?: 'photo' | 'video' | 'any'
    /** MB。 */
    fileSizeLimit?: number
    /** 容器接收，不保证新相册方法合成水印。 */
    proName?: string
    brand?: string
  }

  interface CameraTipTextStyle {
    color?: string
    fontSize?: number | string
    lineHeight?: number | string
  }
  interface CameraTip {
    title?: string
    subtitle?: string
    marginTop?: number | string
    titleStyle?: CameraTipTextStyle
    subtitleStyle?: CameraTipTextStyle
  }
  interface CameraArgs {
    uuid?: string
    count?: number
    number?: number
    proName?: string
    brand?: string
    fileSizeLimit?: number
    cameraPosition?: 'front' | 'back'
    cameraTip?: CameraTip
  }
  interface VideoArgs { uuid?: string; fileSizeLimit?: number }

  interface UploadedFile {
    name: string
    url: string
    path: string
    fileUrl: string
    fileSize: number
    contentType: string
    fileExtension: string
    key: string
    status: 'success' | 'error'
    error?: string
  }
  interface MediaBridgeResult { success: boolean; data: UploadedFile[]; error?: string }

  type WatermarkSwitch = boolean | 0 | 1 | '0' | '1' | 'true' | 'false'
  interface LegacyPickerArgs extends PickerArgs {
    watermark?: WatermarkSwitch
    needWatermark?: WatermarkSwitch
    addWatermark?: WatermarkSwitch
  }
  interface LegacyFilePickerArgs {
    uuid?: string
    count?: number
    type?: string[]
    allowMultiSelection?: boolean
    fileSizeLimit?: number
    dir?: boolean
  }
  type LegacyOpenStatus = boolean | 'true' | 'false'
  interface LegacyUploadMessage {
    uuid?: string
    key?: string
    name?: string
    url?: string
    path?: string
    fileUrl?: string
    contentType?: string
    fileExtension?: string
    fileSize?: number
    eventType?: string
    status?: string
    error?: string
    rnProgress?: number
    totalFileCount?: number
  }

  interface SignatureArgs {
    penColor?: string
    penWidth?: number
    placeholder?: string
    returnBase64?: boolean
    title?: string
  }
  interface SignatureResult {
    success: boolean
    fileUrl?: string
    base64?: string
    localFilePath?: string
    reason?: string
  }

  interface ScanResult { success: boolean; data?: string }
  interface MapPoint { lat: number; lng: number; name?: string }
  interface MapNavigationArgs {
    map: 'baidu' | 'amap' | 'qqmap' | 'apple'
    from: MapPoint
    to: MapPoint
  }

  interface ReportShareArgs {
    imageUrl?: string
    requestId?: string
    title?: string
    fileName?: string
    shareUrl?: string
    description?: string
    thumbUrl?: string
  }
  interface ReportShareImageResult {
    requestId: string
    success: boolean
    imageUrl?: string
    message?: string
  }

  type PatrolCloseTarget = 'APP_HOME' | 'SOURCE_WEBVIEW' | 'SOURCE_H5_ROUTE' | 'SOURCE_H5_RELAUNCH'
  interface PatrolArgs {
    autoNavigate?: boolean
    needSafeArea?: boolean
    needNarBar?: boolean
    narBarTitle?: string
    closeTarget?: PatrolCloseTarget
    closeRoute?: string
    entrySource?: string
  }
  type PatrolCode = 'OPEN_WEBVIEW' | 'SIGN_IN_CLOCK' | 'SCHEDULE_REMINDER' |
    'CANCELLED' | 'TOAST' | 'USER_NOT_READY' | 'ERROR'
  interface PatrolResult {
    success: boolean
    code: PatrolCode
    url?: string
    recordId?: string | number
    message?: string
    appToastShown?: boolean
  }

  interface AppMapLocationArgs {
    target: 'location'
    latitude: number
    longitude: number
    city: string
    cityCode: string
    /** 当前地图分支不独立使用此值。 */
    adcode?: string
    icon?: string
  }

  interface AppBridgeMethods {
    __APP_GET_CONTEXT__: () => Promise<ReadyAppContext>
    __APP_GET_TOKEN_AUTHINFO__: (args?: TokenAuthInfoArgs) => Promise<Record<string, unknown> | ''>
    __APP_GO_LOGIN__: () => void
    __APP_ROUTER_BACK__: () => void
    __APP_GO_HOME_TAB__: () => void
    __APP_OPEN_WORKBENCH_DRAWER__: () => void
    __APP_OPEN_NEW_WINDOW__: (
      url: string, needSafeArea?: boolean, needNarBar?: boolean, narBarTitle?: string,
    ) => void
    __OPEN_APP_WEBVIEW__: (isShowBack?: boolean, title?: string) => void
    __APP_GET_VERSION__: () => Promise<string>
    __APP_GET_SAFE_AREA__: () => string
    __APP_ORIENTATION__: (orientation?: 'landscape' | 'portrait') => void
    __APP_REGISTER_KEYBOARD_LISTENER__: (callback: (status: KeyboardStatus) => void) => void
    __APP_GET_CURRENT_LOCATION__: (options?: LocationOptions) => Promise<AppLocationResult>
    __APP_GET_CURRENT_ADDRESS__: (timeout?: number) => Promise<string>
    __APP_GET_PERMISSION_LOCATION__: () => Promise<AppPermissionStatus | ''>
    __APP_NOTIFICATION_PERMISSION__: () => Promise<AppPermissionStatus>
    __APP_CHECK_OR_REQUEST_PERMISSION__: (args: PermissionArgs) => Promise<AppPermissionStatus>
    __APP_OPEN_SETTING__: () => void
    __APP_OPEN_PICKER_WITH_RESULT__: (args?: PickerArgs) => Promise<MediaBridgeResult>
    __APP_GO_TO_CAMERA_WITH_RESULT__: (args?: CameraArgs) => Promise<MediaBridgeResult>
    __APP_OPEN_TRANSCRIBE_WITH_RESULT__: (args?: VideoArgs) => Promise<MediaBridgeResult>
    __APP_OPEN_SIGNATURE__: (args?: SignatureArgs) => Promise<SignatureResult>
    __APP_OPEN_PICKER__: (jsonArgs: string) => void
    __APP_GO_TO_CAMERA__: (jsonArgs: string) => void
    __APP_OPEN_TRANSCRIBE__: (jsonArgs: string) => void
    __APP_OPEN_FILE_PICKER__: (jsonArgs: string) => void
    __APP_CANCEL_REQUEST__: (key: string) => void
    __APP_SCAN_CODE__: (args?: Record<string, never>) => Promise<ScanResult>
    __APP_PREVIEW_IMAGE__: (args: { urls: string[] | string; current?: number | string }) => void
    __APP_PREVIEW_VIDEO__: (args: { url: string }) => void
    /** 正常路径不回调，禁止 await。 */
    __APP_DOCUMENT_VIEW__: (args: { url: string; type?: string; title?: string }) => Promise<never>
    __APP_OPEN_FILE__: (url: string) => void
    __APP_IMAGE_TO_DATA_URL__: (url: string) => Promise<string>
    __APP_PHOTO_DOWNLOAD__: (url: string) => void
    __APP_CALL_PHONE__: (phone: string) => void
    __APP_COPY_TEXT__: (text: string) => void
    __APP_OPEN_MAP__: (args: { params: MapNavigationArgs }) => void
    __APP_OPEN_REPORT_SHARE__: (args: ReportShareArgs) => void
    __APP_REPORT_SHARE_IMAGE_READY__: (args: ReportShareImageResult) => void
    __APP_PATROL_START_INSPECTION__: (args?: PatrolArgs) => Promise<PatrolResult>
    __APP_PATROL_CONTINUE_INSPECTION__: (args?: PatrolArgs) => Promise<PatrolResult>
    __APP_ACTION__: (target: 'shopcircle' | 'point', action: string, id: string | number) => void
    __APP_LOCATION__: (args: AppMapLocationArgs) => void
  }

  interface Window extends Partial<AppBridgeMethods> {
    ReactNativeWebView?: { postMessage(data: string): void }
    __BUSYMING_OPERATION_APP__?: boolean
    __APP__?: string
    __APP_BRIDGE_CODE__?: number
    __APP_CONTEXT__?: AppContext
    __APP_TOKEN__?: string
    __APP_CITY__?: string
    __APP_GEO__?: string
    __APP_STATUS_BAR_HEIGHT__?: string
    __APP_PLATFORM__?: 'ios' | 'android' | string
    __APP_PLATFORM_ANDROID_BRAND__?: string
    __APP_LIFECYCLE_BRIDGE_VERSION__?: number
    __APP_LIFECYCLE_STATE__?: AppLifecyclePayload
    onAppToken?: (token: string) => void
    onAppCity?: (adcode: string) => void
    onAppGeo?: (geo: string) => void
    onReactNativeSafeAreaInsetsChange?: (insets: AppInsets) => void
    onAppUpdateList?: () => void
    onOpenCameraCallback?: (value: LegacyOpenStatus) => void
    onOpenPickerCallback?: (value: LegacyOpenStatus) => void
    onOpenTranscribeCallback?: (value: LegacyOpenStatus) => void
    onOpenFilePickerCallback?: (value: LegacyOpenStatus) => void
    receiveRNData?: (data: LegacyUploadMessage) => void
    __H5_GENERATE_REPORT_SHARE_IMAGE__?: (requestId: string) => void | Promise<void>
  }
}
专用 route.appContext 页面请建立自己的类型，不要强制转换成 ReadyAppContext 来绕过字段检查。若项目已有同名全局声明，需合并而不是再复制一份产生冲突。
附录 B：联调、排错与验收清单
B.1 提交给 App 同学的信息
信息	要写清什么
H5 环境和地址	test／uat／prod 的完整入口及最终重定向路径，不携带 Token
认证体系	原业务、TokenInfo、统一门户分别调用哪些后端接口
权限需求	页面／按钮对应哪套权限码，资源 ID 来源
所需桥	方法名、使用页面、调用时机、失败时预期 UI
页面导航	H5 内部跳转还是新 WebView，关闭后回哪一层
特殊能力	抽屉、横屏、媒体水印、文件类型、地图平台等
最低安装包范围	与 App 发布记录确认，不能只填当前分支名
B.2 最小验收用例
场景	应验证的结果
冷启动首次打开	先得到异步上下文，再发依赖认证的请求
桥脚本晚到	等待就绪事件，无轮询；超时有明确提示
入口重定向／自动补斜杠	不因入口 URL 与最终 URL 不同而静默丢失初始化
门户权限慢于 Token	不提前按空权限启动依赖权限的业务
合法无权限	正常返回空权限，H5 展示无权限，而不是无限 loading
一次网络失败后恢复	用户主动重试能够继续初始化，不被旧错误永久阻断
原业务登录失效	统一去重处理，回 App 登录；不反复跳转
门户接口 401	确认凭证归属和刷新协议；不无限重试，不混用业务 Token
页面离开／重新加载	旧回调不更新新页面，旧计时和监听不持续污染 UI
切换账号／战区	不使用旧身份快照，重新初始化对应业务
回首页／抽屉	测清调用入口和返回位置；普通二级页面没有抽屉时正常降级
相机／相册／视频取消	不当成成功附件，不重复打开原生页
部分文件上传失败	逐个检查 status；不能仅看顶层 success
超大文件／无文件	明确提示，不保存空 URL
权限拒绝／blocked／limited	正确区分；从设置返回后重新检查
原生文档预览	打开即可，不因 await 未完成一直 loading
普通浏览器／旧 App	开发 Mock 或明确升级提示，不使用真实生产认证
锁屏／前后台／弱网	页面状态可恢复，不重复初始化交互流程
必须在目标 iOS 和 Android 安装包上验证。模拟器无法代表通话、真实定位、相机、相册授权、企微分享等能力。代码检查或单元测试通过不等于这些平台功能已验收。
B.3 可以记录什么，禁止记录什么
建议记录：App 版本、系统版本、桥方法名、错误码、是否成功、耗时、脱敏业务任务 ID，以及不含查询凭据的页面路径。
禁止记录：原始 Token、refreshToken、TokenInfo、签名、Secret、完整 __APP_CONTEXT__、原始接口响应、用户手机号、签名 Base64。分享地址、错误对象、资源树也可能夹带敏感信息，不能直接全量打印。
本地排错也尽量记录“字段是否存在”和数组长度，不用真实用户信息充当文档示例。
B.4 常见问题
为什么我明明在 App 内，函数仍然不存在？
可能是桥还没注入、安装包较旧、页面不是此容器，或该能力只在特定宿主提供。异步上下文可以等专用 ready 事件；其他方法必须分别检查，不存在时不要继续假装成功。
为什么调用成功后还是没有权限？
异步成功表示数据构建完成，不表示该用户被授予所有权限。先区分 personnel.permissionCodes 和 portalAuthObj.portalAuthCodes；正常空数组就是需要展示的业务状态。
可以把新桥理解成“等整个 App 所有数据都加载完”吗？
不可以。新桥等待的是本次上下文所需的门户权限与认证链路，不等待 App 的全部接口，也不保证所有个人资料、定位、地址、可选设备字段非空。
为什么重新获取上下文后 Token 没变化？
底层可复用有效缓存。__APP_GET_CONTEXT__() 不暴露强制刷新参数，不能用重复调用制造强制刷新。应与认证后端和 App 确定真正的失效处理，而不是轮询直到 Token 字符串改变。
为什么 Promise 超时后相机还在？
H5 超时只结束自己的等待，不控制原生界面关闭。不要随后自动再开一次相机。用户返回后按当前业务状态恢复，必要时允许手动重新进入流程。
为什么已有用户样例里能看见 refreshToken？
原始门户 userInfo 可能透传该字段。存在字段不等于 H5 获得刷新协议的所有权。它是敏感信息，不能输出到文档、监控或 URL。
可以直接调用 App 内部 action 来跳任意 Tab 吗？
不应这样接入。当前没有公开的任意 Tab 桥；内部 openPage 等 action 不保证路由、权限和兼容性。先由 App 定义公开方法及其参数再使用。
方法的返回值可以统一包装成 success/data 吗？
可以在 H5 自己的封装层转换，但必须保留原始协议差异。例如 TokenInfo 空字符串、媒体逐文件失败、巡店 CANCELLED 也可能 success 为 true、文档预览不结束 Promise。不能通过统一类型把这些区别抹掉。
附录 C：代码依据、更新规则与已知边界
C.1 核对入口
以下路径均相对 App 仓库，便于在其他机器或语雀中阅读，不依赖作者本地目录。
范围	代码入口
注入方法、消息分发、窗口事件	src/components/WebViewScreen.tsx
异步上下文、请求归属、超时和错误回传	src/components/webViewAppContextBridge.ts
五组上下文结构与门户权限等待	src/api/unifiedPortal/buildOperationH5AppContext.ts
可信地址、旧对象注入、专用对象兼容	src/components/webViewAppContext.ts
门户资源树、有效权限码、用户资源 ID	src/api/unifiedPortal/permissionRuntime.ts
门户权限初始化与共享请求	src/api/unifiedPortal/runtime.ts
设备描述和固定 deviceName	src/api/unifiedPortal/deviceInfo.ts
通用原生处理器	src/config/bridgeConfig.ts
返回主容器、登录路由	src/services/NavigationService.ts
登录失效清理	src/utils/sessionExpire.ts、src/utils/logoutCleanup.ts
历史导航栏参数兼容	src/config/webViewRouteParams.ts
工作台抽屉宿主	src/pages/NewStoreWorkbench.tsx
App 前后台状态	src/components/webViewAppLifecycle.ts
相机及相机提示参数	src/pages/Camera/index.tsx
视频录制与结果事件	src/pages/VideoShoot/index.tsx
文件上传、图片转换、外部地图	src/utils/helper.ts
扫码回调	src/hooks/useScanner.ts
图片／视频预览	src/components/ImagesPreview.tsx、src/components/VideoPreviewModal.tsx
报告分享	src/components/ReportShareBottomSheet.tsx
巡店流程与类型	src/components/NewHomeScreen/patrol/patrolBridgeHandlers.ts、src/types/patrol.ts
C.2 已知能力边界汇总
能力	当前明确边界
任意 Tab 跳转	没有公共方法；goHomeTab 也不接受 tab 参数
强制刷新门户 Token	新上下文桥不提供 force 参数
统一上下文变更订阅	没有通用 appContextChanged 事件；对象热注入与主动获取各有用途
抽屉	仅提供宿主回调的页面注入
公共上下文	仅可信路径；专用 route appContext 不支持新桥
文档预览 Promise	当前正常路径不结束，不 await
键盘监听	只有注册，无公共注销
新相册水印	未实现旧相册的图片水印合成链路，不能仅传参数就承诺生效
目录选择／旧文件取消	没有完整统一结果协议，不承诺每次有结束事件
新媒体上传	检查每个文件 status，不只检查顶层 success
全部桥的通用超时／取消	没有；H5 等待超时不等于原生任务取消
App 版本	分支和提交号不是线上可用性证明；方法存在性与目标安装包联调必须同时确认
C.3 后续如何维护
1. 修改注入函数时，同时核对原生 handler、实际回调和 H5 类型；不能只改方法列表。
2. 新方法必须补：用途、参数默认值／单位、返回值、取消与失败、超时、平台限制、例子和代码入口。
3. 如果方法名不变但参数或返回变化，标明兼容策略；不要用“最新版本”替代具体发布记录。
4. 代码支持但尚未发布或真机验证的能力，应明确标识，不写成所有用户都可用。
5. 新增可信页面、认证字段和导航能力需要同步确认安全边界；不把内部 action 顺手开放为公共 API。
6. 修改用户样例时保持脱敏；资源树示例只用于解释结构，不复制真实用户的全部权限。
本文更新的是接入说明，不修改 App 行为。仍未实现的能力应另提代码需求，不应通过文档示例让 H5 依赖它。
