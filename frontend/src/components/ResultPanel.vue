<script setup>
// 文件说明：定义 ResultPanel 前端组件。
import { computed, onBeforeUnmount, ref, watch } from "vue";

import { writeClipboardText } from "../utils/clipboard.js";
import { downloadBlob, downloadText } from "../utils/download.js";
import { showToast } from "../utils/toast.js";

const props = defineProps({
  result: {
    type: [String, Object],
    required: true,
  },
  resultType: {
    type: String,
    default: "text",
  },
});
const emit = defineEmits(["clear", "copy"]);

const copied = ref(false);
const previewUrl = ref("");
const isImageDataUrl = computed(
  () => typeof props.result === "string" && props.result.startsWith("data:image/"),
);
const isFileResult = computed(() => typeof props.result === "object" && props.result?.kind === "file");
const isImageFileResult = computed(
  () => isFileResult.value && typeof props.result?.contentType === "string" && props.result.contentType.startsWith("image/"),
);

watch(
  () => props.result,
  (value) => {
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value);
      previewUrl.value = "";
    }
    if (typeof value === "object" && value?.kind === "file" && value?.blob && value?.contentType?.startsWith("image/")) {
      previewUrl.value = URL.createObjectURL(value.blob);
    }
  },
  { immediate: true },
);

onBeforeUnmount(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
});

async function copyResult() {
  if (typeof props.result !== "string") {
    return;
  }
  try {
    await writeClipboardText(props.result);
    emit("copy", { outputLength: props.result.length });
    copied.value = true;
    showToast({
      type: "success",
      title: "复制成功",
      message: "结果内容已经写入剪贴板。",
      duration: 1800,
    });
    window.setTimeout(() => {
      copied.value = false;
    }, 1500);
  } catch (error) {
    showToast({
      type: "error",
      title: "复制失败",
      message: error?.message || "浏览器未允许写入剪贴板。",
      duration: 3200,
    });
  }
}

function downloadResult() {
  if (typeof props.result === "string") {
    downloadText("结果.txt", props.result);
    showToast({
      type: "success",
      title: "已开始下载",
      message: "文本结果正在下载。",
      duration: 1800,
    });
    return;
  }
  if (isFileResult.value) {
    downloadBlob(props.result.filename, props.result.blob);
    showToast({
      type: "success",
      title: "已开始下载",
      message: `${props.result.filename} 正在下载。`,
      duration: 1800,
    });
  }
}

function clearResult() {
  emit("clear");
  showToast({
    type: "info",
    title: "结果已清空",
    message: "当前结果区域已重置。",
    duration: 1600,
  });
}
</script>

<template>
  <section class="result-panel">
    <div class="result-panel-head">
      <h3>结果</h3>
      <div class="result-actions">
        <button v-if="typeof result === 'string'" type="button" @click="copyResult">
          {{ copied ? "已复制" : "复制结果" }}
        </button>
        <button type="button" @click="downloadResult">下载结果</button>
        <button type="button" class="secondary-button" @click="clearResult">清空输出</button>
      </div>
    </div>

    <img v-if="isImageDataUrl" :src="result" alt="结果预览" class="result-image" />
    <img v-else-if="isImageFileResult" :src="previewUrl" alt="文件结果预览" class="result-image" />
    <pre v-else-if="typeof result === 'string'">{{ result }}</pre>
    <div v-else-if="isFileResult" class="file-result">
      <p>已生成文件：{{ result.filename }}</p>
      <p>文件类型：{{ result.contentType }}</p>
    </div>
  </section>
</template>
