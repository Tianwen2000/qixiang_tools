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
const cardItems = computed(() => cards.value.map((card) => ({ card, chart: buildChartModel(card) })));

const chartBox = {
  width: 560,
  height: 238,
  left: 52,
  right: 14,
  priceTop: 26,
  priceHeight: 124,
  volumeTop: 174,
  volumeHeight: 44,
};

const chartInnerWidth = chartBox.width - chartBox.left - chartBox.right;

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
  if (value === null || value === undefined || value === "" || value === "-") {
    return "--";
  }
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

function finiteNumber(value) {
  if (value === null || value === undefined || value === "" || value === "-") {
    return null;
  }
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function trimNumber(value, digits = 2) {
  const number = finiteNumber(value);
  if (number === null) {
    return "--";
  }
  return number.toFixed(digits).replace(/\.?0+$/, "");
}

function formatChartPrice(value) {
  const number = finiteNumber(value);
  if (number === null) {
    return "--";
  }
  const abs = Math.abs(number);
  if (abs >= 100) {
    return trimNumber(number, 2);
  }
  if (abs >= 1) {
    return trimNumber(number, 3);
  }
  return trimNumber(number, 4);
}

function formatChartVolume(value) {
  const number = finiteNumber(value);
  if (number === null) {
    return "--";
  }
  if (Math.abs(number) >= 100000000) {
    return `${trimNumber(number / 100000000, 1)}亿`;
  }
  if (Math.abs(number) >= 10000) {
    return `${trimNumber(number / 10000, 1)}万`;
  }
  return trimNumber(number, 0);
}

function chartCurrencyUnit(card) {
  const currency = String(card?.currency || "").toUpperCase();
  if (currency === "CNY") {
    return "元";
  }
  if (currency === "HKD") {
    return "港元";
  }
  if (currency === "USD") {
    return "美元";
  }
  return "";
}

function padTime(value) {
  return String(value).padStart(2, "0");
}

function dateToDayNumber(dateText) {
  const matched = String(dateText || "").match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!matched) {
    return null;
  }
  const [, year, month, day] = matched;
  return Math.floor(Date.UTC(Number(year), Number(month) - 1, Number(day)) / 86400000);
}

function dayNumberToDateText(dayNumber) {
  const date = new Date(Math.round(dayNumber) * 86400000);
  const year = date.getUTCFullYear();
  const month = padTime(date.getUTCMonth() + 1);
  const day = padTime(date.getUTCDate());
  return `${year}-${month}-${day}`;
}

function formatDateLabel(dateText) {
  const matched = String(dateText || "").match(/^\d{4}-(\d{2})-(\d{2})$/);
  return matched ? `${matched[1]}/${matched[2]}` : dateText || "--";
}

function clockToMinute(value) {
  const matched = String(value || "").match(/^(\d{1,2}):(\d{2})$/);
  if (!matched) {
    return null;
  }
  const hour = Number(matched[1]);
  const minute = Number(matched[2]);
  if (!Number.isFinite(hour) || !Number.isFinite(minute) || hour > 23 || minute > 59) {
    return null;
  }
  return hour * 60 + minute;
}

function absoluteMinute(dateText, timeText) {
  const day = dateToDayNumber(dateText);
  const minute = clockToMinute(timeText);
  if (day === null || minute === null) {
    return null;
  }
  return day * 1440 + minute;
}

function formatAbsoluteMinute(value) {
  const minute = ((Math.round(value) % 1440) + 1440) % 1440;
  return `${padTime(Math.floor(minute / 60))}:${padTime(minute % 60)}`;
}

function normalizeChartTime(value) {
  const raw = String(value || "");
  const matched = raw.match(/^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})/);
  if (!matched) {
    const dateOnlyMatched = raw.match(/^(\d{4}-\d{2}-\d{2})$/);
    if (dateOnlyMatched) {
      const day = dateToDayNumber(dateOnlyMatched[1]);
      return {
        raw,
        date: dateOnlyMatched[1],
        axis: formatDateLabel(dateOnlyMatched[1]),
        compact: raw,
        absolute: day === null ? null : day * 1440,
      };
    }
    return {
      raw,
      date: "",
      axis: raw.slice(0, 5) || "--:--",
      compact: raw || "--",
      absolute: null,
    };
  }
  const absolute = absoluteMinute(matched[1], matched[2]);
  return {
    raw: `${matched[1]} ${matched[2]}`,
    date: matched[1],
    axis: matched[2],
    compact: `${matched[1]} ${matched[2]}`,
    absolute,
  };
}

function shortChartTime(value) {
  return normalizeChartTime(value).axis;
}

function compactChartTime(value) {
  return normalizeChartTime(value).compact;
}

function buildLinePath(points, key) {
  const usable = points.filter((point) => finiteNumber(point[key]) !== null);
  if (usable.length < 2) {
    return "";
  }
  return usable
    .map((point, index) => {
      const previous = usable[index - 1];
      // 同一交易日内（含午休）连续连线，仅跨交易日才断开
      const crossDay = !point.isDaily && previous && previous.date && point.date && point.date !== previous.date;
      const command = index === 0 || crossDay ? "M" : "L";
      return `${command}${point.x.toFixed(1)},${point[key].toFixed(1)}`;
    })
    .join(" ");
}

// 把交易时段拼接成连续 X 轴：午休等非交易段不占宽度，跨段处两侧映射到同一 x（视觉无缝衔接）
function finalizeAxis(segments, ticks, firstPoint, lastPoint) {
  const segs = segments.map((seg) => ({ start: seg.start, end: seg.end }));
  // 扩展首末段以覆盖实际数据点（防盘前集合竞价/数据越界）
  segs[0].start = Math.min(segs[0].start, firstPoint.absolute);
  const tail = segs[segs.length - 1];
  tail.end = Math.max(tail.end, lastPoint.absolute, tail.start + 1);

  let total = 0;
  const spans = segs.map((seg) => {
    const before = total;
    total += Math.max(0, seg.end - seg.start);
    return { start: seg.start, end: seg.end, before };
  });
  total = Math.max(total, 1);

  // 绝对分钟 -> 累计交易分钟（午休不计入长度）
  const tradingIndex = (absolute) => {
    let acc = 0;
    for (const seg of spans) {
      if (absolute <= seg.start) {
        return seg.before;
      }
      if (absolute <= seg.end) {
        return seg.before + (absolute - seg.start);
      }
      acc = seg.before + (seg.end - seg.start);
    }
    return acc;
  };

  const projectX = (absolute) => chartBox.left + (tradingIndex(absolute) / total) * chartInnerWidth;

  return {
    start: spans[0].start,
    end: spans[spans.length - 1].end,
    segments: spans,
    totalTradingMinutes: total,
    projectX,
    ticks: ticks
      .filter((tick) => tick && tick.absolute !== null && tick.absolute !== undefined)
      .map((tick) => ({ ...tick, x: projectX(tick.absolute) })),
  };
}

function makeMarketAxis(card, points, chart) {
  const firstPoint = points[0];
  const lastPoint = points[points.length - 1];
  if (chart?.kind === "daily_kline") {
    const fallbackEnd = Math.max(lastPoint.absolute, firstPoint.absolute + 1440);
    const ticks = [0, 0.25, 0.5, 0.75, 1].map((position) => {
      const index = Math.round((points.length - 1) * position);
      const point = points[index];
      const absolute = point?.absolute ?? firstPoint.absolute + (fallbackEnd - firstPoint.absolute) * position;
      return { absolute, label: formatDateLabel(point?.date || dayNumberToDateText(absolute / 1440)) };
    });
    return finalizeAxis([{ start: firstPoint.absolute, end: fallbackEnd }], ticks, firstPoint, lastPoint);
  }

  const baseDate = chart?.trade_date || firstPoint.date || lastPoint.date;
  const region = String(card?.market_region || "").toUpperCase();
  const marketText = `${card?.market || ""}${card?.asset_type || ""}`;
  const abs = (clock) => absoluteMinute(baseDate, clock);

  // 美股：连续无午休
  if (region === "US" || marketText.includes("美股") || marketText.includes("纳斯达克") || marketText.includes("纽交所")) {
    const start = firstPoint.absolute;
    const end = start + 390;
    const ticks = [0, 90, 195, 300, 390].map((offset) => ({ absolute: start + offset, label: formatAbsoluteMinute(start + offset) }));
    return finalizeAxis([{ start, end }], ticks, firstPoint, lastPoint);
  }

  // 港股 / A 股：午休在 X 轴上不占宽度，分界处用合并刻度
  let spec = null;
  if (region === "HK" || marketText.includes("港股")) {
    spec = {
      segments: [["09:30", "12:00"], ["13:00", "16:00"]],
      ticks: [
        { clock: "09:30" },
        { clock: "10:45" },
        { clock: "12:00", label: "12:00 / 13:00" },
        { clock: "14:30" },
        { clock: "16:00" },
      ],
    };
  } else if (
    region === "CN" ||
    marketText.includes("沪市") ||
    marketText.includes("深市") ||
    marketText.includes("北交所") ||
    marketText.includes("指数") ||
    marketText.includes("基金")
  ) {
    spec = {
      segments: [["09:30", "11:30"], ["13:00", "15:00"]],
      ticks: [
        { clock: "09:30" },
        { clock: "10:30" },
        { clock: "11:30", label: "11:30 / 13:00" },
        { clock: "14:00" },
        { clock: "15:00" },
      ],
    };
  }

  if (spec) {
    const segments = spec.segments
      .map(([s, e]) => ({ start: abs(s), end: abs(e) }))
      .filter((seg) => seg.start !== null && seg.end !== null);
    if (segments.length === spec.segments.length) {
      const ticks = spec.ticks
        .map((t) => {
          const absolute = abs(t.clock);
          return absolute === null ? null : { absolute, label: t.label || t.clock };
        })
        .filter(Boolean);
      return finalizeAxis(segments, ticks, firstPoint, lastPoint);
    }
  }

  // 兜底：单段按首末点
  const fallbackEnd = Math.max(lastPoint.absolute, firstPoint.absolute + 1);
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((position) => {
    const absolute = firstPoint.absolute + (fallbackEnd - firstPoint.absolute) * position;
    return { absolute, label: formatAbsoluteMinute(absolute) };
  });
  return finalizeAxis([{ start: firstPoint.absolute, end: fallbackEnd }], ticks, firstPoint, lastPoint);
}

function buildChartTimeText(chart, points, axis) {
  const start = chart?.start_time || points[0]?.fullTime || "";
  const end = chart?.end_time || points[points.length - 1]?.fullTime || "";
  if (chart?.kind === "daily_kline") {
    return start && end ? `${compactChartTime(start)} - ${compactChartTime(end)}` : chart?.updated_at ? `更新 ${chart.updated_at}` : "";
  }
  const axisRange = `${formatAbsoluteMinute(axis.start)}-${formatAbsoluteMinute(axis.end)}`;
  if (start && end) {
    const startInfo = normalizeChartTime(start);
    const endInfo = normalizeChartTime(end);
    if (startInfo.date && startInfo.date === endInfo.date) {
      return `${startInfo.date} ${startInfo.axis}-${endInfo.axis} / 全时段 ${axisRange}`;
    }
    return `${compactChartTime(start)} - ${compactChartTime(end)} / 全时段 ${axisRange}`;
  }
  return chart?.updated_at ? `更新 ${chart.updated_at} / 全时段 ${axisRange}` : `全时段 ${axisRange}`;
}

function withUnit(value, unit) {
  if (!unit || value === "--") {
    return value;
  }
  return `${value} ${unit}`;
}

function volumeBarWidth(axis, pointCount) {
  if (axis.kind === "daily") {
    return Math.max(1, Math.min(4, (chartInnerWidth / Math.max(pointCount, 1)) * 0.58));
  }
  const duration = Math.max(axis.totalTradingMinutes || (axis.end - axis.start), pointCount, 1);
  return Math.max(1, Math.min(4, (chartInnerWidth / duration) * 0.7));
}

function visiblePoint(point, axis) {
  return point.absolute >= axis.start && point.absolute <= axis.end;
}

function buildChartPoints(rawPoints, chartKind = "") {
  return rawPoints
    .map((item) => {
      const timeInfo = normalizeChartTime(item?.[0]);
      return {
        time: timeInfo.axis,
        date: timeInfo.date,
        fullTime: timeInfo.raw,
        absolute: timeInfo.absolute,
        price: finiteNumber(item?.[1]),
        avg: finiteNumber(item?.[2]),
        volume: finiteNumber(item?.[3]) || 0,
        isDaily: chartKind === "daily_kline",
      };
    })
    .filter((point) => point.time && point.absolute !== null && point.price !== null)
    .sort((a, b) => a.absolute - b.absolute);
}

function buildChartModel(card) {
  const chart = card?.chart;
  const rawPoints = Array.isArray(chart?.points) ? chart.points : [];
  const points = buildChartPoints(rawPoints, chart?.kind || "");

  if (points.length < 2) {
    return null;
  }

  const axis = makeMarketAxis(card, points, chart);
  if (chart?.kind === "daily_kline") {
    axis.kind = "daily";
  }
  const visiblePoints = points.filter((point) => visiblePoint(point, axis));
  if (visiblePoints.length < 2) {
    return null;
  }

  const priceUnit = chartCurrencyUnit(card);
  const preClose = finiteNumber(chart?.pre_close ?? card?.previous_close);
  const priceValues = visiblePoints.flatMap((point) => [point.price, point.avg]).filter((value) => value !== null);
  if (preClose !== null) {
    priceValues.push(preClose);
  }

  let minPrice = Math.min(...priceValues);
  let maxPrice = Math.max(...priceValues);
  if (minPrice === maxPrice) {
    const padding = Math.max(Math.abs(minPrice) * 0.01, 0.01);
    minPrice -= padding;
    maxPrice += padding;
  } else {
    const padding = (maxPrice - minPrice) * 0.08;
    minPrice -= padding;
    maxPrice += padding;
  }

  const maxVolume = Math.max(...visiblePoints.map((point) => point.volume), 1);
  const xFor = axis.projectX;
  const yForPrice = (value) => chartBox.priceTop + ((maxPrice - value) / (maxPrice - minPrice)) * chartBox.priceHeight;
  const yForVolume = (value) => chartBox.volumeTop + (1 - value / maxVolume) * chartBox.volumeHeight;
  const barWidth = volumeBarWidth(axis, visiblePoints.length);

  const drawPoints = visiblePoints.map((point) => ({
    ...point,
    x: xFor(point.absolute),
    priceY: yForPrice(point.price),
    avgY: point.avg === null ? null : yForPrice(point.avg),
    volumeY: yForVolume(point.volume),
    volumeHeight: Math.max(1, chartBox.volumeTop + chartBox.volumeHeight - yForVolume(point.volume)),
    barWidth,
  }));

  const priceTicks = Array.from({ length: 5 }, (_, index) => {
    const value = maxPrice - ((maxPrice - minPrice) / 4) * index;
    return {
      y: yForPrice(value),
      label: formatChartPrice(value),
    };
  });

  const lastPoint = visiblePoints[visiblePoints.length - 1];
  const isDailyKline = chart?.kind === "daily_kline";
  const isIntradayKline = chart?.kind === "intraday_kline";
  const chartTitle = isDailyKline
    ? "日 K 走势"
    : isIntradayKline
      ? "5 分钟 K 线"
      : chart?.kind === "quote_snapshot"
        ? "报价快照"
        : "分时走势";
  const avgPath = buildLinePath(drawPoints, "avgY");

  return {
    ...chartBox,
    title: `${card.name} ${chartTitle}`,
    subtitle: `${card.symbol} · ${chart?.source || "公开分时"}${chart?.sampled ? " · 已抽样" : ""}`,
    timeText: buildChartTimeText(chart, visiblePoints, axis),
    updatedAt: chart?.updated_at || card.updated_at || "",
    pricePath: buildLinePath(drawPoints, "priceY"),
    avgPath,
    preCloseY: preClose === null ? null : yForPrice(preClose),
    preCloseLabel: preClose === null ? "--" : withUnit(formatChartPrice(preClose), priceUnit),
    priceUnit,
    priceTicks,
    volumeTicks: [
      { y: chartBox.volumeTop, label: formatChartVolume(maxVolume) },
      { y: chartBox.volumeTop + chartBox.volumeHeight, label: "0" },
    ],
    gridX: axis.ticks,
    points: drawPoints,
    lastPrice: withUnit(formatChartPrice(lastPoint.price), priceUnit),
    lastTime: shortChartTime(lastPoint.fullTime || lastPoint.time),
    avgLabel: isDailyKline || isIntradayKline ? "MA5" : "均线",
  };
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
      <button type="button" :disabled="loading" @click="submit">{{ loading ? "查询中..." : "查询实时行情" }}</button>
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
        <article v-for="{ card, chart } in cardItems" :key="`${card.provider}-${card.symbol}`" class="market-card" :class="toneClass(card)">
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

          <section
            v-if="chart"
            class="market-mini-chart"
            :aria-label="`${chart.title}，${chart.timeText || chart.updatedAt}`"
          >
            <div class="market-chart-head">
              <div>
                <strong>{{ chart.title }}</strong>
                <span>{{ chart.subtitle }}</span>
              </div>
              <span>{{ chart.timeText || chart.updatedAt || "时间未知" }}</span>
            </div>
            <svg
              class="market-chart-canvas"
              :viewBox="`0 0 ${chart.width} ${chart.height}`"
              preserveAspectRatio="xMidYMid meet"
              role="img"
            >
              <rect class="market-chart-bg" x="0" y="0" :width="chart.width" :height="chart.height" rx="8" />
              <g class="market-chart-grid">
                <line
                  v-for="(tick, index) in chart.priceTicks"
                  :key="`py-${index}`"
                  :x1="chart.left"
                  :x2="chart.width - chart.right"
                  :y1="tick.y"
                  :y2="tick.y"
                />
                <line
                  v-for="(tick, index) in chart.gridX"
                  :key="`gx-${index}`"
                  :x1="tick.x"
                  :x2="tick.x"
                  :y1="chart.priceTop"
                  :y2="chart.volumeTop + chart.volumeHeight"
                />
                <line
                  :x1="chart.left"
                  :x2="chart.width - chart.right"
                  :y1="chart.volumeTop"
                  :y2="chart.volumeTop"
                />
              </g>
              <g class="market-chart-axis">
                <text
                  v-if="chart.priceUnit"
                  class="market-chart-unit"
                  :x="chart.left"
                  y="15"
                >
                  价格({{ chart.priceUnit }})
                </text>
                <text
                  v-for="(tick, index) in chart.priceTicks"
                  :key="`price-label-${index}`"
                  :x="chart.left - 7"
                  :y="tick.y + 4"
                  text-anchor="end"
                >
                  {{ tick.label }}
                </text>
                <text
                  v-for="(tick, index) in chart.volumeTicks"
                  :key="`volume-label-${index}`"
                  :x="chart.left - 7"
                  :y="tick.y + 4"
                  text-anchor="end"
                >
                  {{ tick.label }}
                </text>
                <text
                  v-for="(tick, index) in chart.gridX"
                  :key="`time-label-${index}`"
                  :x="tick.x"
                  :y="chart.priceTop + chart.priceHeight + 17"
                  text-anchor="middle"
                >
                  {{ tick.label }}
                </text>
              </g>
              <line
                v-if="chart.preCloseY !== null"
                class="market-chart-preclose"
                :x1="chart.left"
                :x2="chart.width - chart.right"
                :y1="chart.preCloseY"
                :y2="chart.preCloseY"
              />
              <g>
                <rect
                  v-for="(point, index) in chart.points"
                  :key="`volume-${index}`"
                  class="market-chart-volume"
                  :x="point.x - point.barWidth / 2"
                  :y="point.volumeY"
                  :width="point.barWidth"
                  :height="point.volumeHeight"
                />
              </g>
              <path v-if="chart.avgPath" class="market-chart-avg" :d="chart.avgPath" />
              <path class="market-chart-price" :d="chart.pricePath" />
            </svg>
            <div class="market-chart-legend">
              <span><i class="price"></i>价格 {{ chart.lastPrice }}</span>
              <span v-if="chart.avgPath"><i class="avg"></i>{{ chart.avgLabel }}</span>
              <span><i class="preclose"></i>昨收 {{ chart.preCloseLabel }}</span>
              <span>{{ chart.lastTime }}</span>
            </div>
          </section>
          <p v-else class="market-chart-empty">图表：当前公开端点暂无可绘制分时数据。</p>

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

.market-mini-chart {
  display: grid;
  gap: 8px;
  overflow: hidden;
  border-radius: 8px;
  padding: 10px;
  background: #12171d;
  color: #d7e5f2;
}

.market-chart-head,
.market-chart-legend {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.market-chart-head {
  align-items: flex-start;
}

.market-chart-head > div {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.market-chart-head strong {
  color: #eff7ff;
  font-size: 13px;
  line-height: 1.2;
}

.market-chart-head span,
.market-chart-legend,
.market-chart-empty {
  color: #8da0b2;
  font-size: 11px;
  line-height: 1.35;
}

.market-chart-head > span {
  flex: 0 0 auto;
  max-width: 45%;
  text-align: right;
}

.market-chart-canvas {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 560 / 238;
}

.market-chart-bg {
  fill: #11161c;
}

.market-chart-grid line {
  stroke: rgba(204, 220, 234, 0.24);
  stroke-dasharray: 2 3;
  stroke-width: 1;
  vector-effect: non-scaling-stroke;
}

.market-chart-axis text {
  fill: #92a7b7;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 10px;
}

.market-chart-axis .market-chart-unit {
  fill: #b8c8d8;
  font-family: inherit;
  font-size: 10px;
  font-weight: 700;
}

.market-chart-price,
.market-chart-avg,
.market-chart-preclose {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
  vector-effect: non-scaling-stroke;
}

.market-chart-price {
  stroke: #17a9ff;
  stroke-width: 1.8;
}

.market-chart-avg {
  stroke: rgba(231, 237, 243, 0.62);
  stroke-width: 1.1;
}

.market-chart-preclose {
  stroke: rgba(255, 255, 255, 0.38);
  stroke-dasharray: 5 5;
  stroke-width: 1;
}

.market-chart-volume {
  fill: rgba(156, 166, 181, 0.68);
}

.market-chart-legend {
  flex-wrap: wrap;
  align-items: center;
}

.market-chart-legend span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
}

.market-chart-legend i {
  width: 14px;
  height: 2px;
  border-radius: 999px;
}

.market-chart-legend .price {
  background: #17a9ff;
}

.market-chart-legend .avg {
  background: rgba(231, 237, 243, 0.7);
}

.market-chart-legend .preclose {
  background: repeating-linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.5) 0 4px,
    transparent 4px 7px
  );
}

.market-chart-empty {
  margin: -2px 0 0;
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

  .market-chart-head {
    display: grid;
  }

  .market-chart-head > span {
    max-width: none;
    text-align: left;
  }

  .market-mini-chart {
    padding: 8px;
  }
}
</style>
