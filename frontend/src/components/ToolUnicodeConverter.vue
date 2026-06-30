<script setup>
// 文件说明：定义 ToolUnicodeConverter 前端组件。
import { computed, ref, watch } from "vue";

import { executeTextTool } from "../api/tools.js";
import { writeClipboardText } from "../utils/clipboard.js";
import { downloadText } from "../utils/download.js";
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
  { value: "to_standard", label: "字符转 Unicode 标准写法" },
];

const text = ref("");
const result = ref("");
const loading = ref(false);
const action = ref("to_text");
const includeDetailTable = ref(false);
const detailRows = ref([]);
const copied = ref(false);

const copyableResult = computed(() => {
  if (!result.value) {
    return "";
  }
  if (!detailRows.value.length) {
    return result.value;
  }
  const tableText = [
    "输入字符进制详情表",
    "字符\t二进制\t八进制\t十进制\t十六进制\tUnicode",
    ...detailRows.value.map((row) =>
      [row.char, row.binary, row.octal, row.decimal, row.hex, row.unicode].join("\t"),
    ),
  ].join("\n");
  return `${result.value}\n\n${tableText}`;
});

watch(
  () => props.tool,
  () => {
    text.value = "";
    result.value = "";
    loading.value = false;
    action.value = "to_text";
    includeDetailTable.value = false;
    detailRows.value = [];
  },
);

function toUnicodeEscape(char) {
  const codepoint = char.codePointAt(0);
  return `U+${codepoint.toString(16).toUpperCase().padStart(4, "0")}`;
}

function displayChar(char) {
  const displayMap = {
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
    " ": "空格",
  };
  return displayMap[char] || char;
}

function buildDetailRows(value) {
  return Array.from(value).map((char) => {
    const codepoint = char.codePointAt(0);
    return {
      char: displayChar(char),
      binary: codepoint.toString(2),
      octal: codepoint.toString(8),
      decimal: String(codepoint),
      hex: codepoint.toString(16).toUpperCase(),
      unicode: toUnicodeEscape(char),
    };
  });
}

async function submit() {
  if (loading.value) {
    return;
  }
  loading.value = true;
  const activeAction = actions.find((item) => item.value === action.value);
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
        action: action.value,
      },
    });
    result.value = data.result;
    detailRows.value = includeDetailTable.value ? buildDetailRows(text.value) : [];
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
    loading.value = false;
  }
}

function clearOutput() {
  result.value = "";
  detailRows.value = [];
}

async function copyResult() {
  if (!copyableResult.value) {
    return;
  }
  try {
    await writeClipboardText(copyableResult.value);
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
  if (!copyableResult.value) {
    return;
  }
  downloadText("结果.txt", copyableResult.value);
  showToast({
    type: "success",
    title: "已开始下载",
    message: "文本结果正在下载。",
    duration: 1800,
  });
}
</script>

<template>
  <section class="tool-form unicode-converter-tool">
    <textarea v-model="text" rows="14" :placeholder="tool.description"></textarea>

    <div class="unicode-converter-actions">
      <span class="unicode-converter-label">转换方式</span>
      <div class="unicode-converter-action-row">
        <label
          v-for="item in actions"
          :key="item.value"
          class="radio-item"
          :class="{ active: action === item.value }"
        >
          <input v-model="action" type="radio" name="unicode-converter-action" :value="item.value" />
          <span>{{ item.label }}</span>
        </label>
      </div>
    </div>

    <div class="unicode-detail-option">
      <label>
        <input v-model="includeDetailTable" type="checkbox" />
        <span>输入字符进制详情表打印</span>
      </label>
    </div>

    <div class="tool-actions">
      <button type="button" :disabled="loading" @click="submit">
        {{ loading ? "处理中..." : "立即执行" }}
      </button>
      <button type="button" class="secondary-button" @click="text = ''">清空输入</button>
    </div>

    <section v-if="result" class="result-panel unicode-result-panel">
      <div class="result-panel-head">
        <h3>结果</h3>
        <div class="result-actions">
          <button type="button" @click="copyResult">{{ copied ? "已复制" : "复制结果" }}</button>
          <button type="button" @click="downloadResult">下载结果</button>
          <button type="button" class="secondary-button" @click="clearOutput">清空输出</button>
        </div>
      </div>

      <div class="unicode-result-text">{{ result }}</div>

      <div v-if="detailRows.length" class="unicode-detail-table-wrap">
        <h4>输入字符进制详情表</h4>
        <table class="unicode-detail-table">
          <thead>
            <tr>
              <th>字符</th>
              <th>二进制</th>
              <th>八进制</th>
              <th>十进制</th>
              <th>十六进制</th>
              <th>Unicode</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in detailRows" :key="`${row.unicode}-${index}`">
              <td>{{ row.char }}</td>
              <td>{{ row.binary }}</td>
              <td>{{ row.octal }}</td>
              <td>{{ row.decimal }}</td>
              <td>{{ row.hex }}</td>
              <td>{{ row.unicode }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>
