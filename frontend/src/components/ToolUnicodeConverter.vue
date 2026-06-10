<script setup>
import { ref, watch } from "vue";

import { executeTextTool } from "../api/tools.js";
import ResultPanel from "./ResultPanel.vue";
import { showToast, updateToast } from "../utils/toast.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const actions = [
  { value: "to_text", label: "Unicode 转字符" },
  { value: "to_codepoints", label: "字符转 Unicode 码点" },
  { value: "to_escape", label: "字符转 Unicode 转义" },
];

const text = ref("");
const result = ref("");
const loadingAction = ref("");
const lastAction = ref("");
const includeDetailTable = ref(false);

watch(
  () => props.tool,
  () => {
    text.value = "";
    result.value = "";
    loadingAction.value = "";
    lastAction.value = "";
    includeDetailTable.value = false;
  },
);

async function submit(action) {
  if (loadingAction.value) {
    return;
  }
  loadingAction.value = action;
  const activeAction = actions.find((item) => item.value === action);
  const toastId = showToast({
    type: "loading",
    title: "正在执行",
    message: `${activeAction?.label || props.tool.name} 处理中...`,
    duration: 0,
  });
  try {
    const data = await executeTextTool(props.tool.slug, {
      text: text.value,
      params: {
        action,
        include_detail_table: includeDetailTable.value,
      },
    });
    result.value = data.result;
    lastAction.value = action;
    updateToast(toastId, {
      type: "success",
      title: "执行完成",
      message: "结果已更新到下方结果区。",
      duration: 2200,
    });
  } catch (err) {
    updateToast(toastId, {
      type: "error",
      title: "操作失败",
      message: err.message || "执行失败",
      duration: 3600,
    });
  } finally {
    loadingAction.value = "";
  }
}

function clearOutput() {
  result.value = "";
}
</script>

<template>
  <section class="tool-form unicode-converter-tool">
    <textarea v-model="text" rows="14" :placeholder="tool.description"></textarea>

    <div class="unicode-converter-actions" aria-label="转换方式">
      <span class="unicode-converter-label">转换方式</span>
      <div class="unicode-converter-action-row">
        <button
          v-for="item in actions"
          :key="item.value"
          type="button"
          :class="{ active: lastAction === item.value }"
          :disabled="Boolean(loadingAction)"
          @click="submit(item.value)"
        >
          {{ loadingAction === item.value ? "处理中..." : item.label }}
        </button>
      </div>
    </div>

    <div class="unicode-detail-option">
      <label>
        <input v-model="includeDetailTable" type="checkbox" />
        <span>输入字符进制详情表打印</span>
      </label>
    </div>

    <div class="tool-actions">
      <button type="button" class="secondary-button" @click="text = ''">清空输入</button>
    </div>

    <ResultPanel v-if="result" :result="result" result-type="text" @clear="clearOutput" />
  </section>
</template>
