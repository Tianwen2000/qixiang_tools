<script setup>
// 文件说明：定义 ToolLocalIpLookup 前端组件。
import { ref } from "vue";

import { executeTextTool } from "../api/tools.js";
import { showToast, updateToast } from "../utils/toast.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const loading = ref(false);
const result = ref(null);
const outputVisible = ref(true);

const UNSUPPORTED_TEXT = "此处暂不支持检测";

const PUBLIC_SERVICES = [
  {
    service: "ipify IPv4",
    url: "https://api.ipify.org?format=json",
    parse: async (response) => (await response.json())?.ip,
  },
  {
    service: "ipify IPv4/IPv6",
    url: "https://api64.ipify.org?format=json",
    parse: async (response) => (await response.json())?.ip,
  },
  {
    service: "ipify IPv6",
    url: "https://api6.ipify.org?format=json",
    parse: async (response) => (await response.json())?.ip,
  },
  {
    service: "ipapi.co",
    url: "https://ipapi.co/json/",
    parse: async (response) => (await response.json())?.ip,
  },
  {
    service: "Cloudflare Trace",
    url: "https://www.cloudflare.com/cdn-cgi/trace",
    parse: async (response) => {
      const text = await response.text();
      return text.match(/^ip=(.+)$/m)?.[1]?.trim();
    },
  },
];

function isIpv4(ip) {
  const parts = String(ip || "").split(".").map((part) => Number(part));
  return parts.length === 4 && parts.every((part) => Number.isInteger(part) && part >= 0 && part <= 255);
}

function isIpv6(ip) {
  const value = String(ip || "").trim();
  return value.includes(":") && /^[0-9a-fA-F:.]+$/.test(value);
}

function ipVersion(ip) {
  if (isIpv4(ip)) return "ipv4";
  if (isIpv6(ip)) return "ipv6";
  return "";
}

function isPrivateIpv4(ip) {
  const parts = String(ip || "").split(".").map((part) => Number(part));
  if (!isIpv4(ip)) return false;
  const [a, b] = parts;
  return a === 10 || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168);
}

function extractCandidateIps(candidate) {
  return String(candidate || "")
    .split(/\s+/)
    .map((part) => part.trim().replace(/^\[|\]$/g, ""))
    .filter((part) => !part.endsWith(".local"))
    .filter((part) => isIpv4(part) || isIpv6(part));
}

function unique(values) {
  return Array.from(new Set(values.filter(Boolean)));
}

async function detectBrowserLocalIps() {
  if (typeof RTCPeerConnection === "undefined") {
    return { ipv4: [], ipv6: [] };
  }

  const ipv4 = new Set();
  const ipv6 = new Set();
  const peer = new RTCPeerConnection({ iceServers: [] });
  try {
    peer.createDataChannel("ip-check");
    peer.onicecandidate = (event) => {
      const candidate = event.candidate?.candidate || "";
      for (const ip of extractCandidateIps(candidate)) {
        if (isPrivateIpv4(ip)) {
          ipv4.add(ip);
        } else if (isIpv6(ip)) {
          ipv6.add(ip);
        }
      }
    };
    const offer = await peer.createOffer();
    await peer.setLocalDescription(offer);
    await new Promise((resolve) => window.setTimeout(resolve, 1400));
  } catch {
    return { ipv4: [], ipv6: [] };
  } finally {
    peer.close();
  }
  return { ipv4: Array.from(ipv4), ipv6: Array.from(ipv6) };
}

async function queryPublicService(service) {
  try {
    const response = await fetch(service.url, {
      cache: "no-store",
      mode: "cors",
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const ip = String((await service.parse(response)) || "").trim();
    const version = ipVersion(ip);
    if (!version) {
      throw new Error("未返回 IP");
    }
    return { service: service.service, ip, version, ok: true, url: service.url };
  } catch {
    return { service: service.service, ip: "请求失败或浏览器跨域拦截", version: "", ok: false, url: service.url };
  }
}

function voteMajority(items, version) {
  const ips = items.filter((item) => item.ok && item.version === version).map((item) => item.ip);
  const counts = ips.reduce((map, ip) => map.set(ip, (map.get(ip) || 0) + 1), new Map());
  const votes = Array.from(counts.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([ip, count]) => ({ ip, count }));
  return {
    ip: votes[0]?.ip || "",
    votes,
    results: items.filter((item) => item.version === version || !item.ok),
  };
}

function sceneFromType(type) {
  const value = String(type || "").toLowerCase();
  if (value.includes("mobile")) return "蜂窝移动网络";
  if (value.includes("hosting") || value.includes("data")) return "IDC / 云服务器 / 机房";
  if (value.includes("business")) return "企业/商业宽带";
  if (value.includes("education")) return "教育科研网络";
  if (value.includes("isp") || value.includes("residential")) return "家庭/运营商宽带";
  return "";
}

function normalizeOperatorName(value) {
  const raw = String(value || "").trim();
  if (!raw) return UNSUPPORTED_TEXT;
  const lower = raw.toLowerCase();
  const rules = [
    [/china\s*telecom|chinanet|ctc|中国电信|电信/, "中国电信"],
    [/china\s*mobile|cmcc|cmi|中国移动|移动/, "中国移动"],
    [/china\s*unicom|unicom|中国联通|联通/, "中国联通"],
    [/china\s*broadcast|cbn|中国广电|广电/, "中国广电"],
    [/cernet|china education|中国教育|教育网/, "中国教育和科研计算机网"],
    [/dr\.?peng|鹏博士/, "鹏博士宽带"],
    [/great\s*wall|长城宽带/, "长城宽带"],
    [/founder|方正宽带/, "方正宽带"],
    [/tencent|tencent cloud|腾讯/, "腾讯云"],
    [/aliyun|alibaba|alibaba cloud|alicloud|阿里/, "阿里云"],
    [/huawei|huawei cloud|华为/, "华为云"],
    [/baidu|baidu cloud|百度/, "百度智能云"],
    [/jd cloud|jingdong|京东/, "京东云"],
    [/ucloud|优刻得/, "UCloud 优刻得"],
    [/qingcloud|青云/, "青云 QingCloud"],
    [/kingsoft|金山云/, "金山云"],
    [/oracle|oracle cloud/, "甲骨文云"],
    [/amazon|aws|amazon technologies/, "亚马逊云 AWS"],
    [/google|google cloud/, "谷歌云"],
    [/microsoft|azure/, "微软 Azure"],
    [/ibm|softlayer/, "IBM Cloud"],
    [/cloudflare/, "Cloudflare"],
    [/akamai|linode/, "Akamai / Linode"],
    [/fastly/, "Fastly"],
    [/edgecast|verizon/, "Verizon / Edgecast"],
    [/digitalocean/, "DigitalOcean"],
    [/vultr/, "Vultr"],
    [/ovh/, "OVHcloud"],
    [/hetzner/, "Hetzner"],
    [/leaseweb/, "Leaseweb"],
    [/zenlayer/, "Zenlayer"],
    [/cogent/, "Cogent"],
    [/level\s*3|lumen/, "Lumen"],
    [/softbank/, "软银"],
    [/ntt\s*docomo|docomo/, "NTT DoCoMo"],
    [/ntt/, "NTT 通信"],
    [/kddi/, "KDDI"],
    [/rakuten/, "乐天移动"],
    [/chunghwa|cht/, "中华电信"],
    [/taiwan\s*mobile/, "台湾大哥大"],
    [/far\s*eas(t|tone)|fetnet/, "远传电信"],
    [/hkt|hong kong telecommunications/, "香港电讯"],
    [/pccw/, "电讯盈科 PCCW"],
    [/hutchison|three/, "和记电讯 3HK"],
    [/singtel/, "新加坡电信"],
    [/starhub/, "星和 StarHub"],
    [/m1\s*limited|m1net/, "新加坡 M1"],
    [/sk\s*telecom/, "韩国 SK 电讯"],
    [/korea\s*telecom|kt\s*corporation|\bkt\b/, "韩国 KT"],
    [/lg\s*u\+|lgu/, "韩国 LG U+"],
  ];
  const matched = rules.find(([pattern]) => pattern.test(lower));
  return matched ? matched[1] : raw;
}

async function queryIpDetail(ip, fallbackScene = "") {
  if (!ip) {
    return {
      supported: false,
      location: UNSUPPORTED_TEXT,
      operator: UNSUPPORTED_TEXT,
      scene: UNSUPPORTED_TEXT,
    };
  }
  if (isPrivateIpv4(ip)) {
    return {
      supported: true,
      location: "内网地址",
      operator: "当前局域网",
      scene: "内网 / 局域网",
    };
  }
  try {
    const response = await fetch(`https://ipwho.is/${encodeURIComponent(ip)}?lang=zh-CN`, {
      cache: "no-store",
      mode: "cors",
    });
    const data = await response.json();
    if (!response.ok || data?.success === false) {
      throw new Error("lookup failed");
    }
    const location = unique([data.country, data.region, data.city]).join(" ") || UNSUPPORTED_TEXT;
    const operator = normalizeOperatorName(data.connection?.isp || data.connection?.org || data.org);
    const scene = sceneFromType(data.connection?.type) || fallbackScene || UNSUPPORTED_TEXT;
    return { supported: true, location, operator, scene };
  } catch {
    return {
      supported: false,
      location: UNSUPPORTED_TEXT,
      operator: UNSUPPORTED_TEXT,
      scene: fallbackScene || UNSUPPORTED_TEXT,
    };
  }
}

function makeIpItem(ip, detail, fallback = UNSUPPORTED_TEXT) {
  return {
    ip: ip || fallback,
    available: Boolean(ip),
    detail,
  };
}

function analyzeVersion(version, publicIp, serverIp) {
  const label = version === "ipv4" ? "IPv4" : "IPv6";
  if (!publicIp || !serverIp) {
    return {
      status: "unknown",
      label: "暂不判断",
      tone: "danger",
      message: `${label} 缺少浏览器公网结果或本站服务视角结果，此处暂不支持检测。`,
    };
  }
  if (publicIp === serverIp) {
    return {
      status: "same",
      label: "出口一致",
      tone: "success",
      message: `${label} 境外服务视角公网 IP 与本站国内服务视角公网 IP 一致，当前大概率没有 ${label} 分流。`,
    };
  }
  return {
    status: "split",
    label: "疑似分流",
    tone: "warning",
    message: `${label} 境外服务视角公网 IP 与本站国内服务视角公网 IP 不一致，可能存在代理、VPN、策略路由或站点分流。`,
  };
}

function buildDualStackNotice(ipv4Public, ipv4Server, ipv6Public, ipv6Server) {
  const hasIpv4 = Boolean(ipv4Public || ipv4Server);
  const hasIpv6 = Boolean(ipv6Public || ipv6Server);
  if (!hasIpv4 || !hasIpv6) {
    return "";
  }
  return "检测到 IPv6 出口和 IPv4 出口同时存在，这是蜂窝网络/双栈网络的常见情况，不一定代表代理或分流。";
}

async function buildVersionResult(version, localIps, majority, serverSeen) {
  const isV4 = version === "ipv4";
  const serverIp = serverSeen.version === version ? serverSeen.ip : "";
  const [localDetails, publicDetail, serverDetail] = await Promise.all([
    Promise.all(localIps.map((ip) => queryIpDetail(ip))),
    queryIpDetail(majority.ip),
    queryIpDetail(serverIp, "访问本站的公网出口"),
  ]);
  return {
    version,
    title: isV4 ? "IPv4" : "IPv6",
    localLabel: isV4 ? "您本机当前网络的内网 IPv4" : "您本机当前的 IPv6",
    publicLabel: isV4 ? "境外服务视角的公网 IPv4" : "境外服务视角的公网 IPv6",
    serverLabel: isV4 ? "本站国内服务视角的公网 IPv4" : "本站国内服务视角的公网 IPv6",
    splitLabel: isV4 ? "IPv4 分流判断" : "IPv6 分流判断",
    local: makeIpItem(localIps.join("，"), localDetails[0]),
    public: makeIpItem(majority.ip, publicDetail),
    server: makeIpItem(serverIp, serverDetail),
    votes: majority.votes,
    services: majority.results,
    split: analyzeVersion(version, majority.ip, serverIp),
  };
}

async function lookupIp() {
  if (loading.value) {
    return;
  }
  loading.value = true;
  outputVisible.value = true;
  const toastId = showToast({
    type: "loading",
    title: "正在查询",
    message: "正在检测 IPv4、IPv6、公网归属地与分流出口...",
    duration: 0,
  });
  try {
    const [serverData, localIps, publicResults] = await Promise.all([
      executeTextTool(props.tool.slug, { text: "", params: {} }).catch(() => ({ result: {} })),
      detectBrowserLocalIps(),
      Promise.all(PUBLIC_SERVICES.map(queryPublicService)),
    ]);
    const serverRaw = serverData.result?.server_seen || {};
    const serverSeen = {
      ...serverRaw,
      ip: serverRaw.ok ? serverRaw.ip : "",
      version: ipVersion(serverRaw.ok ? serverRaw.ip : ""),
    };
    const ipv4Majority = voteMajority(publicResults, "ipv4");
    const ipv6Majority = voteMajority(publicResults, "ipv6");
    const [ipv4, ipv6] = await Promise.all([
      buildVersionResult("ipv4", localIps.ipv4, ipv4Majority, serverSeen),
      buildVersionResult("ipv6", localIps.ipv6, ipv6Majority, serverSeen),
    ]);
    result.value = {
      ipv4,
      ipv6,
      public_results: publicResults,
      dual_stack_notice: buildDualStackNotice(ipv4Majority.ip, serverSeen.version === "ipv4" ? serverSeen.ip : "", ipv6Majority.ip, serverSeen.version === "ipv6" ? serverSeen.ip : ""),
      notes: serverData.result?.notes || [],
    };
    updateToast(toastId, {
      type: "success",
      title: "查询完成",
      message: "IP 检测结果已更新。",
      duration: 2200,
    });
  } catch (err) {
    updateToast(toastId, {
      type: "error",
      title: "查询失败",
      message: err.message || "IP 查询失败",
      duration: 3600,
    });
  } finally {
    loading.value = false;
  }
}

function clearOutput() {
  outputVisible.value = false;
  showToast({
    type: "info",
    title: "已清空输出",
    message: "IP 查询结果已从当前页面隐藏。",
    duration: 1800,
  });
}
</script>

<template>
  <section class="tool-form local-tool-panel">
    <div class="local-tool-header">
      <div class="local-tool-header-bar">
        <div>
          <h3>内网、公网与分流 IP 检测</h3>
          <p>
            IPv4：本机内网 IPv4：尽力检测当前浏览器所在网络的 IPv4 地址；境外服务视角公网 IPv4：由多个境外接口返回结果投票决定；本站国内服务视角公网 IPv4：访问本站接口时服务器看到的来源 IPv4
          </p>
          <p>
            IPv6：本机 IPv6 地址：尽力检测当前浏览器可见的 IPv6 地址，可能包含公网 IPv6、私有 IPv6 或链路本地 IPv6；境外服务视角公网 IPv6：由多个支持 IPv6 的境外接口返回结果投票决定；本站国内服务视角公网 IPv6：访问本站接口时服务器看到的来源 IPv6
          </p>
        </div>
        <div class="tool-actions">
          <button type="button" :disabled="loading" @click="lookupIp">{{ loading ? "查询中..." : "开始查询" }}</button>
          <button v-if="result" type="button" class="secondary-button" @click="clearOutput">清空输出</button>
        </div>
      </div>
    </div>

    <section v-if="!result" class="result-panel">
      <div class="result-panel-head">
        <h3>等待查询</h3>
      </div>
      <p class="empty-hint">点击“开始查询”后，会分别返回 IPv4 / IPv6 的本机地址、公网出口、本站服务视角和分流判断。</p>
    </section>

    <template v-else-if="outputVisible">
      <section v-if="result.dual_stack_notice" class="result-panel">
        <div class="result-panel-head">
          <h3>双栈网络提示</h3>
          <span class="summary-chip warning">IPv4 / IPv6</span>
        </div>
        <p class="empty-hint">{{ result.dual_stack_notice }}</p>
      </section>

      <section v-for="group in [result.ipv4, result.ipv6]" :key="group.version" class="result-panel ip-version-panel">
        <div class="result-panel-head">
          <h3>{{ group.title }}</h3>
          <span class="summary-chip" :class="group.split.tone">{{ group.split.label }}</span>
        </div>

        <div class="insight-grid ip-version-grid">
          <article class="insight-card ip-info-card">
            <span class="insight-label">{{ group.localLabel }}</span>
            <strong class="insight-value">{{ group.local.ip }}</strong>
            <dl class="ip-detail-list">
              <div><dt>归属地</dt><dd>{{ group.local.detail?.location || UNSUPPORTED_TEXT }}</dd></div>
              <div><dt>运营商</dt><dd>{{ group.local.detail?.operator || UNSUPPORTED_TEXT }}</dd></div>
            </dl>
          </article>

          <article class="insight-card ip-info-card">
            <span class="insight-label">{{ group.publicLabel }}</span>
            <strong class="insight-value">{{ group.public.ip }}</strong>
            <dl class="ip-detail-list">
              <div><dt>归属地</dt><dd>{{ group.public.detail?.location || UNSUPPORTED_TEXT }}</dd></div>
              <div><dt>运营商</dt><dd>{{ group.public.detail?.operator || UNSUPPORTED_TEXT }}</dd></div>
            </dl>
          </article>

          <article class="insight-card ip-info-card">
            <span class="insight-label">{{ group.serverLabel }}</span>
            <strong class="insight-value">{{ group.server.ip }}</strong>
            <dl class="ip-detail-list">
              <div><dt>归属地</dt><dd>{{ group.server.detail?.location || UNSUPPORTED_TEXT }}</dd></div>
              <div><dt>运营商</dt><dd>{{ group.server.detail?.operator || UNSUPPORTED_TEXT }}</dd></div>
            </dl>
          </article>

          <article class="insight-card ip-info-card ip-split-card">
            <span class="insight-label">{{ group.splitLabel }}</span>
            <strong class="insight-value">{{ group.split.label }}</strong>
            <span class="summary-chip ip-split-message" :class="group.split.tone">{{ group.split.message }}</span>
          </article>
        </div>

        <div class="ip-lookup-vote-list">
          <article v-for="vote in group.votes" :key="`${group.version}-${vote.ip}`" class="ip-lookup-vote-item">
            <strong>{{ vote.ip }}</strong>
            <span>{{ vote.count }} 票</span>
          </article>
          <article v-if="!group.votes.length" class="ip-lookup-vote-item">
            <strong>{{ UNSUPPORTED_TEXT }}</strong>
            <span>0 票</span>
          </article>
        </div>
      </section>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>公网服务原始结果</h3>
        </div>
        <div class="ip-lookup-service-list">
          <article v-for="item in result.public_results" :key="item.service" class="ip-lookup-service-item">
            <div>
              <strong>{{ item.service }}</strong>
              <small>{{ item.url || "请求失败" }}</small>
            </div>
            <span class="status-chip" :class="{ success: item.ok, danger: !item.ok }">{{ item.ip }}</span>
          </article>
        </div>
      </section>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>说明</h3>
        </div>
        <ul class="ip-lookup-note-list">
          <li v-for="note in result.notes" :key="note">{{ note }}</li>
        </ul>
      </section>
    </template>

    <section v-else class="result-panel">
      <div class="result-panel-head">
        <h3>结果</h3>
      </div>
      <p class="empty-hint">输出已清空，可点击“开始查询”重新检测。</p>
    </section>
  </section>
</template>
