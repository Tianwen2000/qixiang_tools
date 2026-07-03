<script setup>
// 文件说明：纯前端实现 key: value 请求信息与 JSON 的双向转换。
import { ref } from "vue";

import { buildToolUsageBase, reportToolUsageLog } from "../api/tool-usage.js";
import ResultPanel from "./ResultPanel.vue";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const input = ref("");
const output = ref("");
const notices = ref([]);
const error = ref("");

function parseKvLinesToJson(text) {
  const result = {};
  const messages = [];
  const seenKeys = new Set();
  const invalidLines = [];
  const emptyValueKeys = [];

  text.split(/\r?\n/).forEach((rawLine, index) => {
    if (!rawLine.trim()) {
      return;
    }
    const colonIndex = rawLine.indexOf(":");
    if (colonIndex < 0) {
      invalidLines.push(index + 1);
      return;
    }

    const key = rawLine.slice(0, colonIndex).trim().toLowerCase();
    const value = rawLine.slice(colonIndex + 1).trim();
    if (!key) {
      invalidLines.push(index + 1);
      return;
    }
    if (seenKeys.has(key)) {
      messages.push(`重复 key「${key}」已使用最后一次出现的值。`);
    }
    if (value === "") {
      emptyValueKeys.push(key);
    }
    seenKeys.add(key);
    result[key] = value;
  });

  if (invalidLines.length) {
    throw new Error(`第 ${invalidLines.join("、")} 行无法识别，请确认每行包含冒号。`);
  }
  if (emptyValueKeys.length) {
    messages.push(`以下 key 的 value 为空，已保留为空字符串：${emptyValueKeys.join("、")}。`);
  }

  return {
    json: JSON.stringify(result, null, 2),
    messages,
  };
}

function jsonToKvLines(text) {
  if (text === "") {
    throw new Error("请输入需要转换的 JSON 内容。");
  }
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    throw new Error("JSON 解析失败，请检查格式。");
  }
  if (!data || Array.isArray(data) || typeof data !== "object") {
    throw new Error("JSON 转 KV 只支持对象格式，例如 {\"user-agent\":\"Dart/3.12\"}。");
  }
  return Object.entries(data)
    .map(([key, value]) => {
      const stringValue =
        value === null || value === undefined
          ? ""
          : typeof value === "object"
            ? JSON.stringify(value)
            : String(value);
      return `${key}: ${stringValue}`;
    })
    .join("\n");
}

function convertKvToJson() {
  error.value = "";
  notices.value = [];
  output.value = "";
  const startedAt = performance.now();
  reportToolUsageLog({
    ...buildToolUsageBase(props.tool),
    action: "click",
    success: true,
    inputLength: input.value.length,
  });
  try {
    const parsed = parseKvLinesToJson(input.value);
    output.value = parsed.json;
    notices.value = parsed.messages;
    reportToolUsageLog({
      ...buildToolUsageBase(props.tool),
      action: "convert",
      success: true,
      durationMs: performance.now() - startedAt,
      inputLength: input.value.length,
      outputLength: output.value.length,
    });
  } catch (err) {
    error.value = err.message || "无法识别";
    reportToolUsageLog({
      ...buildToolUsageBase(props.tool),
      action: "convert",
      success: false,
      durationMs: performance.now() - startedAt,
      inputLength: input.value.length,
      errorMessage: error.value,
    });
  }
}

function convertJsonToKv() {
  error.value = "";
  notices.value = [];
  output.value = "";
  const startedAt = performance.now();
  reportToolUsageLog({
    ...buildToolUsageBase(props.tool),
    action: "click",
    success: true,
    inputLength: input.value.length,
  });
  try {
    output.value = jsonToKvLines(input.value);
    reportToolUsageLog({
      ...buildToolUsageBase(props.tool),
      action: "convert",
      success: true,
      durationMs: performance.now() - startedAt,
      inputLength: input.value.length,
      outputLength: output.value.length,
    });
  } catch (err) {
    error.value = err.message || "JSON 解析失败，请检查格式。";
    reportToolUsageLog({
      ...buildToolUsageBase(props.tool),
      action: "convert",
      success: false,
      durationMs: performance.now() - startedAt,
      inputLength: input.value.length,
      errorMessage: error.value,
    });
  }
}

function clearAll() {
  reportToolUsageLog({
    ...buildToolUsageBase(props.tool),
    action: "clear",
    success: true,
    inputLength: input.value.length,
    outputLength: output.value.length,
  });
  input.value = "";
  output.value = "";
  notices.value = [];
  error.value = "";
}

function clearOutput() {
  reportToolUsageLog({
    ...buildToolUsageBase(props.tool),
    action: "clear",
    success: true,
    outputLength: output.value.length,
  });
  output.value = "";
}

function reportCopy(event) {
  reportToolUsageLog({
    ...buildToolUsageBase(props.tool),
    action: "copy",
    success: true,
    outputLength: event?.outputLength || 0,
  });
}
</script>

<template>
  <section class="local-text-tool">
    <textarea
      v-model="input"
      rows="12"
      spellcheck="false"
      placeholder="粘贴 key: value 格式内容，例如：
user-agent: Dart/3.12
accept: text/event-stream
host: 47.86.26.13:7052
authorization: Bearer xxx

也可以粘贴 JSON 对象后转换为 key: value。"
    ></textarea>

    <div class="tool-actions">
      <button type="button" @click="convertKvToJson">KV 转 JSON</button>
      <button type="button" @click="convertJsonToKv">JSON 转 KV</button>
      <button type="button" class="secondary-button" @click="clearAll">清空输入</button>
    </div>

    <div v-if="error" class="local-message error">{{ error }}</div>
    <div v-if="notices.length" class="local-message">
      <p v-for="item in notices" :key="item">{{ item }}</p>
    </div>

    <ResultPanel v-if="output" :result="output" result-type="text" @copy="reportCopy" @clear="clearOutput" />
  </section>
</template>

<style scoped>
.local-text-tool {
  display: grid;
  gap: 16px;
}

textarea {
  width: 100%;
  min-height: 260px;
  resize: vertical;
  padding: 16px;
  border: 1px solid rgba(148, 191, 220, 0.72);
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(236, 252, 255, 0.72));
  color: #172033;
  font: 14px/1.7 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  outline: none;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

textarea:focus {
  border-color: rgba(45, 179, 160, 0.86);
  box-shadow: 0 0 0 4px rgba(45, 179, 160, 0.12);
}

.tool-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.tool-actions button {
  min-height: 46px;
  padding: 0 24px;
  border: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, #25c9a8, #1db899);
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 14px 24px rgba(29, 184, 153, 0.22);
}

.tool-actions .secondary-button {
  background: rgba(255, 255, 255, 0.86);
  color: #31516f;
  border: 1px solid rgba(160, 191, 218, 0.5);
  box-shadow: none;
}

.local-message,
.local-result-card {
  border-radius: 16px;
  border: 1px solid rgba(160, 191, 218, 0.46);
  background: rgba(255, 255, 255, 0.82);
  padding: 14px 16px;
  color: #42617e;
}

.local-message p {
  margin: 0;
}

.local-message.error {
  color: #b42318;
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(255, 241, 242, 0.86);
}

.local-result-card header {
  margin-bottom: 10px;
}

.local-result-card h3 {
  margin: 0;
  font-size: 16px;
  color: #172033;
}

pre {
  max-height: 420px;
  margin: 0;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font: 14px/1.7 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}

@media (max-width: 640px) {
  textarea {
    min-height: 220px;
  }

  .tool-actions button {
    width: 100%;
  }
}
</style>
