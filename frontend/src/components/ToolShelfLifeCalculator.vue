<script setup>
import { computed, ref } from "vue";

import GlassSelect from "./GlassSelect.vue";
import { addDays, addYears, formatReadableDate, parseDateInputValue, toDateInputValue } from "../utils/time-tools.js";

defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const manufactureDate = ref(toDateInputValue(new Date()));
const shelfValue = ref(30);
const shelfUnit = ref("days");

const shelfUnitOptions = [
  { value: "days", label: "天" },
  { value: "months", label: "月" },
  { value: "years", label: "年" },
];

function addMonths(date, amount) {
  const next = new Date(date);
  next.setMonth(next.getMonth() + amount);
  return next;
}

const result = computed(() => {
  const madeAt = parseDateInputValue(manufactureDate.value);
  const amount = Number(shelfValue.value);
  if (!madeAt) {
    return { error: "请选择生产日期" };
  }
  if (!Number.isFinite(amount) || amount <= 0) {
    return { error: "请填写有效的保质期数值" };
  }
  let expiryDate = madeAt;
  if (shelfUnit.value === "days") {
    expiryDate = addDays(madeAt, amount);
  } else if (shelfUnit.value === "months") {
    expiryDate = addMonths(madeAt, amount);
  } else {
    expiryDate = addYears(madeAt, amount);
  }
  const remainDays = Math.round((expiryDate - new Date()) / 86400000);
  return {
    manufacture: formatReadableDate(madeAt),
    expiry: formatReadableDate(expiryDate),
    remainDays,
    status: remainDays >= 0 ? "仍在保质期内" : "已经过期",
  };
});
</script>

<template>
  <section class="tool-form time-tool-shell">
    <label class="time-tool-label">
      <span>生产日期</span>
      <input v-model="manufactureDate" type="date" />
    </label>

    <label class="time-tool-label">
      <span>保质期数值</span>
      <input v-model="shelfValue" type="number" min="1" />
    </label>

    <label class="time-tool-label">
      <span>单位</span>
      <GlassSelect v-model="shelfUnit" :options="shelfUnitOptions" placeholder="请选择单位" />
    </label>

    <section v-if="result.error" class="time-tool-empty">{{ result.error }}</section>
    <section v-else class="time-tool-grid">
      <article class="time-tool-card">
        <span>生产日期</span>
        <strong>{{ result.manufacture }}</strong>
      </article>
      <article class="time-tool-card">
        <span>到期日期</span>
        <strong>{{ result.expiry }}</strong>
      </article>
      <article class="time-tool-card wide">
        <span>状态</span>
        <strong>{{ result.status }}</strong>
        <small>{{ result.remainDays >= 0 ? `距离到期还有 ${result.remainDays} 天` : `已过期 ${Math.abs(result.remainDays)} 天` }}</small>
      </article>
    </section>
  </section>
</template>
