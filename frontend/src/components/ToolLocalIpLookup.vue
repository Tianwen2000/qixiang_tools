<script setup>
import { computed, ref } from "vue";

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
const PRIVATE_RANGE_TEXT =
  "常见内网段：10.0.0.0 ~ 10.255.255.255、172.16.0.0 ~ 172.31.255.255、192.168.0.0 ~ 192.168.255.255";

const PUBLIC_SERVICES = [
  {
    service: "ipify",
    url: "https://api.ipify.org?format=json",
    parse: async (response) => (await response.json())?.ip,
  },
  {
    service: "ipify IPv4/IPv6",
    url: "https://api64.ipify.org?format=json",
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

const splitStatus = computed(() => result.value?.split_result?.status || "unknown");
const splitTone = computed(() => {
  if (splitStatus.value === "same") {
    return "success";
  }
  if (splitStatus.value === "split") {
    return "warning";
  }
  return "danger";
});
const splitLabel = computed(() => {
  if (splitStatus.value === "same") {
    return "出口一致";
  }
  if (splitStatus.value === "split") {
    return "疑似分流";
  }
  return "无法判断";
});
const publicTone = computed(() => {
  const status = result.value?.public_summary?.status;
  if (status === "same") {
    return "success";
  }
  if (status === "different") {
    return "warning";
  }
  return "danger";
});

function displayIp(item) {
  return item?.ip || "暂无结果";
}

function isPrivateIpv4(ip) {
  const parts = String(ip || "").split(".").map((part) => Number(part));
  if (parts.length !== 4 || parts.some((part) => !Number.isInteger(part) || part < 0 || part > 255)) {
    return false;
  }
  const [a, b] = parts;
  return a === 10 || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168);
}

function extractIps(text) {
  return Array.from(new Set(String(text || "").match(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g) || []));
}

async function detectBrowserLocalIps() {
  if (typeof RTCPeerConnection === "undefined") {
    return [];
  }

  const ips = new Set();
  const peer = new RTCPeerConnection({ iceServers: [] });
  try {
    peer.createDataChannel("ip-check");
    peer.onicecandidate = (event) => {
      const candidate = event.candidate?.candidate || "";
      extractIps(candidate).filter(isPrivateIpv4).forEach((ip) => ips.add(ip));
    };
    const offer = await peer.createOffer();
    await peer.setLocalDescription(offer);
    await new Promise((resolve) => window.setTimeout(resolve, 1400));
  } catch {
    return [];
  } finally {
    peer.close();
  }
  return Array.from(ips);
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
    if (!ip) {
      throw new Error("未返回 IP");
    }
    return { service: service.service, ip, ok: true, url: service.url };
  } catch {
    return { service: service.service, ip: "请求失败或浏览器跨域拦截", ok: false, url: service.url };
  }
}

function buildPublicSummary(publicResults, serverSeenIp) {
  const validIps = publicResults.filter((item) => item.ok && item.ip).map((item) => item.ip);
  if (!validIps.length) {
    return {
      status: "failed",
      majority_ip: "",
      message: "浏览器侧公网服务均未返回有效公网 IP。",
      relation: "可能是公网服务被网络或浏览器跨域策略拦截，可稍后重试或换网络检查。",
      votes: [],
    };
  }

  const counts = validIps.reduce((map, ip) => map.set(ip, (map.get(ip) || 0) + 1), new Map());
  const votes = Array.from(counts.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([ip, count]) => ({ ip, count }));
  const majorityIp = votes[0].ip;
  const hasDifferentPublicIps = counts.size > 1;
  const differsFromServer = Boolean(serverSeenIp && serverSeenIp !== majorityIp);

  let status = "same";
  let message = "浏览器侧公网服务结果一致。";
  let relation = serverSeenIp
    ? "浏览器公网出口与访问本站时的后端视角一致，当前大概率没有针对本站的分流。"
    : "未获取到本站后端视角 IP，仅展示浏览器公网服务结果。";

  if (hasDifferentPublicIps || differsFromServer) {
    status = "different";
    message = "公网 IP 结果不一致，可能存在浏览器代理、VPN、策略路由或不同站点分流。";
    relation = differsFromServer
      ? "浏览器公网服务多数 IP 与本站后端看到的访问 IP 不一致，访问不同服务可能走了不同出口。"
      : "多个浏览器公网服务返回不同 IP，网络出口可能较复杂。";
  }

  return { status, majority_ip: majorityIp, message, relation, votes };
}

function analyzeSplit(publicSummary) {
  if (publicSummary.status === "same") {
    return {
      status: "same",
      message: "浏览器公网服务与本站后端视角一致，当前大概率没有分流，或访问本站和公网检测服务走的是同一出口。",
    };
  }
  if (publicSummary.status === "different") {
    return {
      status: "split",
      message: "检测到公网结果不一致，可能存在 VPN、代理、策略路由、DNS 分流或站点差异出口。",
    };
  }
  return {
    status: "unknown",
    message: "公网服务未返回足够结果，暂时无法判断是否存在分流。",
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
    message: "正在检测内网、公网与分流出口...",
    duration: 0,
  });
  try {
    const [serverData, localIps, publicResults] = await Promise.all([
      executeTextTool(props.tool.slug, { text: "", params: {} }).catch(() => ({ result: {} })),
      detectBrowserLocalIps(),
      Promise.all(PUBLIC_SERVICES.map(queryPublicService)),
    ]);
    const serverSeen = serverData.result?.server_seen || {};
    const serverSeenIp = serverSeen.ok ? serverSeen.ip : "";
    const publicSummary = buildPublicSummary(publicResults, serverSeenIp);
    result.value = {
      local_ips: localIps,
      local_ip: localIps.length ? localIps.join("，") : "浏览器未暴露内网 IP",
      server_seen: serverSeen,
      public_results: publicResults,
      public_summary: publicSummary,
      split_result: analyzeSplit(publicSummary),
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
          <p>查询由当前浏览器发起，会尽力检测网页端内网 IP、公网出口与访问本站时的后端视角。{{ PRIVATE_RANGE_TEXT }}</p>
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
      <p class="empty-hint">点击“开始查询”后，会返回网页端内网 IP、浏览器公网出口、本站后端看到的访问 IP 和分流判断。</p>
    </section>

    <template v-else-if="outputVisible">
      <div class="insight-grid">
        <article class="insight-card">
          <span class="insight-label">网页端内网 IP</span>
          <strong class="insight-value">{{ result.local_ip }}</strong>
        </article>
        <article class="insight-card">
          <span class="insight-label">浏览器公网多数 IP</span>
          <strong class="insight-value">{{ result.public_summary.majority_ip || "暂无结果" }}</strong>
          <small>由当前网页直接请求公网服务</small>
        </article>
        <article class="insight-card">
          <span class="insight-label">本站后端看到的访问 IP</span>
          <strong class="insight-value">{{ displayIp(result.server_seen) }}</strong>
          <small>{{ result.server_seen?.url || "未返回来源" }}</small>
        </article>
        <article class="insight-card">
          <span class="insight-label">分流判断</span>
          <strong class="insight-value">{{ splitLabel }}</strong>
          <span class="summary-chip" :class="splitTone">{{ result.split_result.message }}</span>
        </article>
      </div>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>公网服务交叉验证</h3>
          <span class="summary-chip" :class="publicTone">
            {{ result.public_summary.majority_ip || "暂无多数 IP" }}
          </span>
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
          <h3>结果分析</h3>
          <span class="summary-chip" :class="publicTone">{{ result.public_summary.message }}</span>
        </div>
        <div class="ip-lookup-vote-list">
          <article v-for="vote in result.public_summary.votes" :key="vote.ip" class="ip-lookup-vote-item">
            <strong>{{ vote.ip }}</strong>
            <span>{{ vote.count }} 票</span>
          </article>
        </div>
        <p class="empty-hint">{{ result.public_summary.relation }}</p>
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
