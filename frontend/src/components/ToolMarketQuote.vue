<script setup>
import { computed, reactive, ref } from "vue";

import { executeTextTool } from "../api/tools.js";
import { showToast, updateToast } from "../utils/toast.js";
import GlassSelect from "./GlassSelect.vue";
import ResultPanel from "./ResultPanel.vue";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const marketOptions = [
  { label: "自动识别", value: "auto" },
  { label: "A 股/指数/ETF", value: "cn" },
  { label: "场外基金", value: "fund" },
  { label: "港股", value: "hk" },
  { label: "美股", value: "us" },
  { label: "东方财富 secid", value: "secid" },
];

const examples = [
  { label: "中文名称", value: "中证白酒 贵州茅台" },
  { label: "基金", value: "110022 易方达消费行业股票" },
  { label: "港美股", value: "HK00700 AAPL BABA MSFT" },
];

const form = reactive({
  text: "",
  market: "auto",
});
const loading = ref(false);
const payload = ref(null);
const outputMode = ref("card");

const cards = computed(() => payload.value?.cards || []);
const failures = computed(() => payload.value?.failures || []);
const robotText = computed(() => payload.value?.robot_text || "");
const jsonText = computed(() => (payload.value ? JSON.stringify(payload.value.json || payload.value.cards || [], null, 2) : ""));

function setExample(value) {
  form.text = value;
}

function toneClass(card) {
  const percent = Number(card?.change_percent);
  if (percent > 0) {
    return "up";
  }
  if (percent < 0) {
    return "down";
  }
  return "flat";
}

function formatPrice(value, suffix = "") {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "--";
  }
  return `${number.toFixed(4).replace(/\.?0+$/, "")}${suffix}`;
}

function formatPercent(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "--";
  }
  return `${number > 0 ? "+" : ""}${number.toFixed(2)}%`;
}

function formatAmount(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return "--";
  }
  if (Math.abs(number) >= 100000000) {
    return `${(number / 100000000).toFixed(2)} 亿`;
  }
  if (Math.abs(number) >= 10000) {
    return `${(number / 10000).toFixed(2)} 万`;
  }
  return number.toFixed(0);
}

async function submit() {
  if (!form.text.trim()) {
    showToast({
      type: "error",
      title: "请输入代码",
      message: "至少输入一个股票、指数或基金代码。",
      duration: 2800,
    });
    return;
  }
  if (loading.value) {
    return;
  }

  loading.value = true;
  const toastId = showToast({
    type: "loading",
    title: "正在查询",
    message: "正在请求公开行情端点...",
    duration: 0,
  });
  try {
    const data = await executeTextTool(props.tool.slug, {
      text: form.text,
      params: { market: form.market },
    });
    payload.value = JSON.parse(data.result);
    outputMode.value = "card";
    updateToast(toastId, {
      type: "success",
      title: "查询完成",
      message: "行情卡片已更新。",
      duration: 2200,
    });
  } catch (err) {
    updateToast(toastId, {
      type: "error",
      title: "查询失败",
      message: err.message || "行情查询失败",
      duration: 3800,
    });
  } finally {
    loading.value = false;
  }
}

function clearOutput() {
  payload.value = null;
}
</script>

<template>
  <section class="tool-form local-tool-panel market-quote-tool">
    <div class="local-tool-header">
      <div class="local-tool-header-bar">
        <div>
          <h3>实时行情查询</h3>
          <p>A 股、ETF/LOF、指数、场外基金、港股和美股会走后端公开端点聚合。</p>
          <p class="market-hint">输入完整代码或者股票/基金名称再点击查询行情，多输入或者少输入都会错误哦！同时不要太频繁请求！</p>
        </div>
        <div class="market-example-row">
          <button v-for="item in examples" :key="item.label" type="button" class="secondary-button" @click="setExample(item.value)">
            {{ item.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="market-query-grid">
      <label>
        <span>代码或完整名称</span>
        <textarea v-model="form.text" rows="1" placeholder="600519 中证白酒 易方达消费行业股票 HK00700 AAPL"></textarea>
      </label>
      <label>
        <span>市场类型</span>
        <GlassSelect v-model="form.market" :options="marketOptions" placeholder="请选择市场" />
      </label>
    </div>

    <div class="tool-actions">
      <button type="button" :disabled="loading" @click="submit">{{ loading ? "查询中..." : "查询行情" }}</button>
      <button type="button" class="secondary-button" @click="form.text = ''">清空输入</button>
      <button v-if="payload" type="button" class="secondary-button" @click="clearOutput">清空输出</button>
    </div>

    <template v-if="payload">
      <div class="market-output-tabs">
        <button type="button" :class="{ active: outputMode === 'card' }" @click="outputMode = 'card'">卡片</button>
        <button type="button" :class="{ active: outputMode === 'json' }" @click="outputMode = 'json'">JSON</button>
        <button type="button" :class="{ active: outputMode === 'robot' }" @click="outputMode = 'robot'">文本</button>
      </div>

      <section v-if="outputMode === 'card'" class="market-card-grid">
        <article v-for="card in cards" :key="`${card.provider}-${card.symbol}`" class="market-card" :class="toneClass(card)">
          <div class="market-card-head">
            <div>
              <span>{{ card.asset_type }}</span>
              <h3>{{ card.name }}</h3>
              <p>{{ card.symbol }} · {{ card.market }}</p>
            </div>
            <strong>{{ card.currency }}</strong>
          </div>

          <div class="market-price-row">
            <strong>{{ formatPrice(card.latest) }}</strong>
            <span>{{ formatPercent(card.change_percent) }}</span>
          </div>

          <div class="market-metric-grid">
            <span>涨跌额 <strong>{{ formatPrice(card.change) }}</strong></span>
            <span>今开 <strong>{{ formatPrice(card.open) }}</strong></span>
            <span>最高 <strong>{{ formatPrice(card.high) }}</strong></span>
            <span>最低 <strong>{{ formatPrice(card.low) }}</strong></span>
            <span>昨收/净值 <strong>{{ formatPrice(card.previous_close) }}</strong></span>
            <span>成交额 <strong>{{ formatAmount(card.amount) }}</strong></span>
          </div>

          <footer>
            <span>{{ card.source }}</span>
            <span>{{ card.updated_at || card.nav_date || "--" }}</span>
          </footer>
        </article>
      </section>

      <ResultPanel v-else-if="outputMode === 'json'" :result="jsonText" result-type="text" @clear="clearOutput" />
      <ResultPanel v-else :result="robotText" result-type="text" @clear="clearOutput" />

      <section v-if="failures.length" class="result-panel">
        <div class="result-panel-head">
          <h3>未完成查询</h3>
        </div>
        <div class="market-failure-list">
          <span v-for="item in failures" :key="item.symbol">{{ item.symbol }}：{{ item.message }}</span>
        </div>
      </section>

      <p class="market-note">公开端点数据仅作信息展示，不构成投资建议。</p>
    </template>
  </section>
</template>

<style scoped>
.market-quote-tool {
  gap: 10px;
  padding: 14px;
}

.market-quote-tool :deep(.local-tool-header) {
  margin-bottom: 0;
}

.market-quote-tool :deep(.local-tool-header p) {
  margin-top: 2px;
  font-size: 13px;
  line-height: 1.4;
}

.market-quote-tool :deep(.local-tool-header .market-hint) {
  margin-top: 4px;
  color: var(--accent-strong);
  font-weight: 600;
}

.market-quote-tool,
.market-quote-tool * {
  box-sizing: border-box;
}

.local-tool-header-bar > div {
  min-width: 0;
}

.local-tool-header h3,
.local-tool-header p {
  overflow-wrap: anywhere;
}

.market-example-row,
.market-output-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.market-example-row button,
.market-output-tabs button {
  min-width: 86px;
  border: 1px solid #dbe3eb;
  border-radius: 14px;
  padding: 9px 11px;
  background: #fff;
  color: var(--ink);
  cursor: pointer;
}

.market-output-tabs button.active {
  border-color: transparent;
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%);
  color: #fff;
}

.market-query-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(190px, 0.7fr);
  gap: 10px;
  align-items: end;
}

.market-query-grid label {
  display: grid;
  gap: 6px;
}

.market-query-grid label span {
  font-size: 13px;
}

.market-query-grid textarea {
  min-height: 42px;
  max-height: 88px;
  resize: vertical;
}

.market-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.market-card {
  display: grid;
  gap: 10px;
  min-width: 0;
  border: 1px solid rgba(203, 214, 225, 0.86);
  border-radius: 8px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 18px 42px rgba(73, 95, 122, 0.12);
}

.market-card.up {
  border-color: rgba(210, 70, 70, 0.26);
}

.market-card.down {
  border-color: rgba(36, 156, 101, 0.26);
}

.market-card-head,
.market-price-row,
.market-card footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.market-card-head h3 {
  margin: 4px 0;
  font-size: 18px;
}

.market-card-head p,
.market-card-head span,
.market-card footer,
.market-note {
  margin: 0;
  color: var(--muted);
}

.market-card-head > strong {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(96, 119, 200, 0.12);
  color: var(--ink);
  font-size: 13px;
}

.market-price-row strong {
  font-size: 26px;
  line-height: 1;
}

.market-price-row span {
  min-width: 78px;
  border-radius: 999px;
  padding: 8px 10px;
  background: rgba(107, 117, 130, 0.12);
  text-align: center;
  font-weight: 700;
}

.market-card.up .market-price-row span {
  background: rgba(210, 70, 70, 0.12);
  color: #b82727;
}

.market-card.down .market-price-row span {
  background: rgba(36, 156, 101, 0.12);
  color: #157c4c;
}

.market-metric-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.market-metric-grid span {
  display: grid;
  gap: 4px;
  min-width: 0;
  border-radius: 8px;
  padding: 8px 10px;
  background: rgba(245, 248, 252, 0.92);
  color: var(--muted);
}

.market-metric-grid strong {
  color: var(--ink);
  overflow-wrap: anywhere;
}

.market-failure-list {
  display: grid;
  gap: 8px;
  color: var(--muted);
}

@media (max-width: 760px) {
  .market-query-grid {
    grid-template-columns: 1fr;
    align-items: stretch;
  }

  .market-price-row strong {
    font-size: 24px;
  }
}
</style>
