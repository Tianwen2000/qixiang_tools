<script setup>
import { computed, reactive, ref, watch } from "vue";

import { uploadFileTool } from "../api/tools.js";
import GlassSelect from "./GlassSelect.vue";
import ResultPanel from "./ResultPanel.vue";
import { showToast, updateToast } from "../utils/toast.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const fileInputRef = ref(null);

function buildInitialParams(tool) {
  return Object.fromEntries((tool.params || []).map((item) => [item.key, item.default ?? ""]));
}

const file = ref(null);
const result = ref("");
const loading = ref(false);
const params = reactive(
  buildInitialParams(props.tool),
);
const visibleParams = computed(() =>
  (props.tool.params || []).filter((item) => {
    if (!item.showWhen) {
      return true;
    }
    return Object.entries(item.showWhen).every(([key, expected]) => {
      const actual = params[key];
      return Array.isArray(expected) ? expected.includes(actual) : actual === expected;
    });
  }),
);

watch(
  () => props.tool,
  (nextTool) => {
    clearInput();
    result.value = "";
    Object.keys(params).forEach((key) => delete params[key]);
    Object.assign(params, buildInitialParams(nextTool));
  },
);

async function submit() {
  if (!file.value) {
    showToast({
      type: "error",
      title: "操作失败",
      message: "请先选择文件",
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
    title: "正在上传并处理",
    message: `${props.tool.name} 处理中...`,
    duration: 0,
  });
  try {
    const data = await uploadFileTool(props.tool.slug, file.value, { ...params });
    result.value = data.kind === "file" ? data : data.result;
    updateToast(toastId, {
      type: "success",
      title: "处理完成",
      message: toolResultMessage(props.tool.result_type),
      duration: 2400,
    });
  } catch (err) {
    updateToast(toastId, {
      type: "error",
      title: "操作失败",
      message: err.message || "上传失败",
      duration: 3600,
    });
  } finally {
    loading.value = false;
  }
}

function toolResultMessage(resultType) {
  return resultType === "file" ? "结果文件已生成，可在下方下载。" : "结果已更新到下方结果区。";
}

function clearOutput() {
  result.value = "";
}

function clearInput() {
  file.value = null;
  if (fileInputRef.value) {
    fileInputRef.value.value = "";
  }
}
</script>

<template>
  <section class="tool-form">
    <div class="file-picker">
      <input ref="fileInputRef" type="file" @change="file = $event.target.files?.[0] || null" />
      <p v-if="file" class="file-name">已选择：{{ file.name }}</p>
    </div>

    <div v-if="visibleParams.length" class="param-row">
      <label v-for="item in visibleParams" :key="item.key">
        <span>{{ item.label }}</span>
        <GlassSelect
          v-if="item.type === 'select'"
          v-model="params[item.key]"
          :options="item.options"
          :placeholder="item.placeholder || `请选择${item.label}`"
        />
        <input
          v-else-if="item.type === 'text'"
          v-model="params[item.key]"
          type="text"
          :placeholder="item.placeholder || `请输入${item.label}`"
        />
        <textarea
          v-else-if="item.type === 'textarea'"
          v-model="params[item.key]"
          rows="6"
          :placeholder="item.placeholder || `请输入${item.label}`"
        ></textarea>
        <div v-else-if="item.type === 'radio'" class="radio-row">
          <label v-for="option in item.options" :key="option.value" class="radio-item">
            <input v-model="params[item.key]" type="radio" :name="item.key" :value="option.value" />
            <span>{{ option.label }}</span>
          </label>
        </div>
      </label>
    </div>

    <div class="tool-actions">
      <button type="button" :disabled="loading" @click="submit">
        {{ loading ? "处理中..." : "上传并执行" }}
      </button>
      <button type="button" class="secondary-button" @click="clearInput">清空输入</button>
    </div>

    <ResultPanel v-if="result" :result="result" :result-type="tool.result_type" @clear="clearOutput" />
  </section>
</template>
