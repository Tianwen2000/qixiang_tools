<script setup>
// 文件说明：定义 ToolHttpTester 前端组件。
import { reactive, ref } from "vue";

import GlassSelect from "./GlassSelect.vue";
import { showToast, updateToast } from "../utils/toast.js";

const methodOptions = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"].map((method) => ({
  label: method,
  value: method,
}));

const form = reactive({
  url: "",
  method: "GET",
  headers: "{\n  \"Accept\": \"application/json\"\n}",
  body: "",
});

const loading = ref(false);
const responseData = ref(null);

function parseHeaders(text) {
  if (!text.trim()) {
    return {};
  }
  try {
    const value = JSON.parse(text);
    if (!value || typeof value !== "object" || Array.isArray(value)) {
      throw new Error("请求头必须是 JSON 对象");
    }
    return value;
  } catch (err) {
    throw new Error(err.message || "请求头 JSON 解析失败");
  }
}

async function submit() {
  if (!form.url.trim()) {
    showToast({
      type: "error",
      title: "请求未发送",
      message: "请输入请求地址",
      duration: 3200,
    });
    return;
  }

  if (loading.value) {
    return;
  }

  loading.value = true;
  const toastId = showToast({
    type: "loading",
    title: "正在发送请求",
    message: `${form.method} ${form.url}`,
    duration: 0,
  });

  try {
    const headers = parseHeaders(form.headers);
    const options = {
      method: form.method,
      headers,
    };

    if (!["GET", "HEAD"].includes(form.method) && form.body.trim()) {
      options.body = form.body;
    }

    const startedAt = performance.now();
    const response = await fetch(form.url, options);
    const elapsed = Math.round(performance.now() - startedAt);
    const contentType = response.headers.get("content-type") || "";
    const rawText = await response.text();

    let formattedBody = rawText;
    if (contentType.includes("application/json") && rawText) {
      try {
        formattedBody = JSON.stringify(JSON.parse(rawText), null, 2);
      } catch {
        formattedBody = rawText;
      }
    }

    responseData.value = {
      ok: response.ok,
      status: response.status,
      elapsed,
      headers: JSON.stringify(Object.fromEntries(response.headers.entries()), null, 2),
      body: formattedBody || "(空响应体)",
    };
    updateToast(toastId, {
      type: response.ok ? "success" : "error",
      title: response.ok ? "请求完成" : "请求返回异常",
      message: `状态码 ${response.status}，耗时 ${elapsed} 毫秒`,
      duration: 3000,
    });
  } catch (err) {
    updateToast(toastId, {
      type: "error",
      title: "请求失败",
      message: err.message || "请求失败，可能是网络错误或 CORS 拦截",
      duration: 3800,
    });
  } finally {
    loading.value = false;
  }
}

function clearOutput() {
  responseData.value = null;
}
</script>

<template>
  <section class="tool-form local-tool-panel">
    <div class="local-tool-header">
      <h3>HTTP 接口测试</h3>
      <p>请求会直接从浏览器发起。如果目标站点未开放 CORS，浏览器可能会阻止请求。</p>
    </div>

    <div class="tester-grid">
      <label>
        <span>请求地址</span>
        <input v-model="form.url" type="text" placeholder="https://api.example.com/users" />
      </label>
      <label>
        <span>请求方法</span>
        <GlassSelect v-model="form.method" :options="methodOptions" placeholder="请选择请求方法" />
      </label>
    </div>

    <label class="tester-block">
      <span>请求头 JSON</span>
      <textarea v-model="form.headers" rows="8" placeholder="请输入请求头 JSON"></textarea>
    </label>

    <label class="tester-block">
      <span>请求 Body</span>
      <textarea v-model="form.body" rows="10" placeholder="GET 或 HEAD 请求可留空"></textarea>
    </label>

    <div class="tool-actions">
      <button type="button" :disabled="loading" @click="submit">
        {{ loading ? "请求中..." : "发送请求" }}
      </button>
    </div>

    <template v-if="responseData">
      <section class="result-panel">
        <div class="result-panel-head">
          <h3>响应概览</h3>
          <div class="result-actions">
            <button type="button" class="secondary-button" @click="clearOutput">清空输出</button>
          </div>
        </div>
        <div class="http-summary">
          <span class="summary-chip" :class="{ success: responseData.ok, danger: !responseData.ok }">
            {{ responseData.ok ? "请求成功" : "请求失败" }}
          </span>
          <span class="summary-chip">状态码 {{ responseData.status }}</span>
          <span class="summary-chip">耗时 {{ responseData.elapsed }} 毫秒</span>
        </div>
      </section>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>响应头</h3>
        </div>
        <pre>{{ responseData.headers }}</pre>
      </section>

      <section class="result-panel">
        <div class="result-panel-head">
          <h3>响应体</h3>
        </div>
        <pre>{{ responseData.body }}</pre>
      </section>
    </template>
  </section>
</template>
