<script setup>
// 文件说明：定义 ToolScheduleMemo 前端组件。
import { computed, ref, watch } from "vue";

import { readJsonCache, writeJsonCache } from "../utils/page-cache.js";
import { showToast } from "../utils/toast.js";
import { toDateInputValue } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const STORAGE_KEY = "tw-time-schedule-memo-v1";
const draftDate = ref(toDateInputValue(new Date()));
const draftTitle = ref("");
const draftNote = ref("");
const records = ref(readJsonCache(STORAGE_KEY, []));

const sortedRecords = computed(() =>
  [...records.value].sort((left, right) => {
    if (left.date === right.date) {
      return right.createdAt - left.createdAt;
    }
    return left.date.localeCompare(right.date);
  }),
);

watch(
  records,
  (value) => {
    writeJsonCache(STORAGE_KEY, value);
  },
  { deep: true },
);

function addRecord() {
  if (!draftTitle.value.trim()) {
    showToast({
      type: "error",
      title: "请先写标题",
      message: "备忘录至少需要一个标题。",
      duration: 2200,
    });
    return;
  }
  records.value.unshift({
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    date: draftDate.value,
    title: draftTitle.value.trim(),
    note: draftNote.value.trim(),
    createdAt: Date.now(),
  });
  draftTitle.value = "";
  draftNote.value = "";
  showToast({
    type: "success",
    title: "已加入备忘录",
    message: "内容已经保存在当前浏览器。",
    duration: 1800,
  });
}

function removeRecord(id) {
  records.value = records.value.filter((item) => item.id !== id);
}
</script>

<template>
  <section class="tool-form time-tool-shell">
    <label class="time-tool-label">
      <span>日期</span>
      <input v-model="draftDate" type="date" />
    </label>

    <label class="time-tool-label">
      <span>标题</span>
      <input v-model="draftTitle" type="text" placeholder="例如 复盘会议、交稿、体检" />
    </label>

    <label class="time-tool-label">
      <span>备注</span>
      <textarea v-model="draftNote" rows="5" placeholder="写一点提醒内容、地点或待办事项"></textarea>
    </label>

    <div class="time-tool-actions">
      <button type="button" @click="addRecord">加入备忘录</button>
    </div>

    <section v-if="!sortedRecords.length" class="time-tool-empty">当前还没有备忘录，先加一条试试。</section>
    <section v-else class="time-tool-list">
      <article v-for="item in sortedRecords" :key="item.id" class="time-tool-list-item">
        <div class="time-tool-list-head">
          <strong>{{ item.title }}</strong>
          <button type="button" class="secondary-button" @click="removeRecord(item.id)">删除</button>
        </div>
        <small>{{ item.date }}</small>
        <small v-if="item.note">{{ item.note }}</small>
      </article>
    </section>
  </section>
</template>
