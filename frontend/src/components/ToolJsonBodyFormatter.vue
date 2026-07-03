<script setup>
// 文件说明：纯前端实现 JSON 紧凑文本与格式化文本互转。
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
const rawOutput = ref("");
const formattedOutput = ref("");
const error = ref("");

function formatJsonBody(rawText) {
  if (rawText === "") {
    throw new Error("请输入需要格式化的 JSON 内容。");
  }
  try {
    return JSON.stringify(JSON.parse(rawText), null, 2);
  } catch {
    throw new Error("JSON 解析失败，请检查格式。");
  }
}

function compactJsonBody(rawText) {
  if (rawText === "") {
    throw new Error("请输入需要压缩的 JSON 内容。");
  }
  try {
    return JSON.stringify(JSON.parse(rawText));
  } catch {
    throw new Error("JSON 解析失败，请检查格式。");
  }
}

function format() {
  error.value = "";
  formattedOutput.value = "";
  rawOutput.value = input.value;
  const startedAt = performance.now();
  reportToolUsageLog({
    ...buildToolUsageBase(props.tool),
    action: "click",
    success: true,
    inputLength: input.value.length,
  });
  try {
    formattedOutput.value = formatJsonBody(input.value);
    reportToolUsageLog({
      ...buildToolUsageBase(props.tool),
      action: "convert",
      success: true,
      durationMs: performance.now() - startedAt,
      inputLength: input.value.length,
      outputLength: formattedOutput.value.length,
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

function compact() {
  error.value = "";
  formattedOutput.value = "";
  rawOutput.value = input.value;
  const startedAt = performance.now();
  reportToolUsageLog({
    ...buildToolUsageBase(props.tool),
    action: "click",
    success: true,
    inputLength: input.value.length,
  });
  try {
    formattedOutput.value = compactJsonBody(input.value);
    reportToolUsageLog({
      ...buildToolUsageBase(props.tool),
      action: "convert",
      success: true,
      durationMs: performance.now() - startedAt,
      inputLength: input.value.length,
      outputLength: formattedOutput.value.length,
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
    outputLength: formattedOutput.value.length,
  });
  input.value = "";
  rawOutput.value = "";
  formattedOutput.value = "";
  error.value = "";
}

function clearOutput() {
  reportToolUsageLog({
    ...buildToolUsageBase(props.tool),
    action: "clear",
    success: true,
    outputLength: formattedOutput.value.length,
  });
  rawOutput.value = "";
  formattedOutput.value = "";
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
      placeholder='粘贴 JSON 请求体或响应体，例如：{"name":"张三","age":18,"tags":["测试","开发"]}'
    ></textarea>

    <div class="tool-actions">
      <button type="button" @click="format">压缩转格式化</button>
      <button type="button" @click="compact">格式化转压缩</button>
      <button type="button" class="secondary-button" @click="clearAll">清空输入</button>
    </div>

    <div v-if="error" class="local-message error">{{ error }}</div>

    <div v-if="rawOutput" class="result-grid">
      <section class="local-result-card">
        <header>
          <h3>Raw 原始</h3>
        </header>
        <pre>{{ rawOutput }}</pre>
      </section>
    </div>

    <ResultPanel v-if="formattedOutput" :result="formattedOutput" result-type="text" @copy="reportCopy" @clear="clearOutput" />
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

.local-message.error {
  color: #b42318;
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(255, 241, 242, 0.86);
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
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

@media (max-width: 780px) {
  .result-grid {
    grid-template-columns: 1fr;
  }
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
