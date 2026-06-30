<script setup>
// 文件说明：定义 ToolPieChartMaker 前端组件。
import { computed, ref } from "vue";

import { showToast } from "../utils/toast.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

void props.tool;

const TAU = Math.PI * 2;
const previewWidth = 760;
const previewHeight = 470;
const chartCenterX = 252;
const chartCenterY = 208;
const chartRadius = 118;

const palettes = [
  {
    name: "清风蓝绿",
    colors: ["#4f7cff", "#63c172", "#f6c453", "#ef7d57", "#7f96ff", "#43b7c8"],
  },
  {
    name: "珊瑚暖色",
    colors: ["#ff7a59", "#ffb457", "#ffd166", "#7cc576", "#5aa9ff", "#9b7cff"],
  },
  {
    name: "森林薄荷",
    colors: ["#147a6e", "#27ae60", "#6fcf97", "#a8e6cf", "#f3d46b", "#f28c64"],
  },
];

let rowSeed = 1;
const svgRef = ref(null);
const chartTitle = ref("浏览器市场份额");
const chartSubtitle = ref("基础版图表工具，先从饼图开始");
const showLegend = ref(true);
const showLabels = ref(true);
const donutMode = ref(false);
const donutRatio = ref(58);
const activePaletteIndex = ref(0);
const rows = ref([
  createRow("Chrome", 70, palettes[0].colors[0]),
  createRow("Firefox", 15, palettes[0].colors[1]),
  createRow("Edge", 10, palettes[0].colors[2]),
  createRow("Safari", 5, palettes[0].colors[3]),
]);

function createRow(label = "", value = "", color = palettes[0].colors[0]) {
  const row = {
    id: rowSeed,
    label,
    value,
    color,
  };
  rowSeed += 1;
  return row;
}

function polarToCartesian(cx, cy, radius, angle) {
  return {
    x: cx + Math.cos(angle) * radius,
    y: cy + Math.sin(angle) * radius,
  };
}

function buildSlicePath(cx, cy, radius, startAngle, endAngle, innerRadius = 0) {
  const sweep = Math.max(0, endAngle - startAngle);
  if (sweep <= 0) {
    return "";
  }

  if (sweep >= TAU - 0.0001) {
    if (innerRadius > 0) {
      return [
        `M ${cx} ${cy - radius}`,
        `A ${radius} ${radius} 0 1 1 ${cx - 0.01} ${cy - radius}`,
        `A ${radius} ${radius} 0 1 1 ${cx} ${cy - radius}`,
        `L ${cx} ${cy - innerRadius}`,
        `A ${innerRadius} ${innerRadius} 0 1 0 ${cx - 0.01} ${cy - innerRadius}`,
        `A ${innerRadius} ${innerRadius} 0 1 0 ${cx} ${cy - innerRadius}`,
        "Z",
      ].join(" ");
    }

    return [
      `M ${cx} ${cy - radius}`,
      `A ${radius} ${radius} 0 1 1 ${cx - 0.01} ${cy - radius}`,
      `A ${radius} ${radius} 0 1 1 ${cx} ${cy - radius}`,
      "Z",
    ].join(" ");
  }

  const startOuter = polarToCartesian(cx, cy, radius, startAngle);
  const endOuter = polarToCartesian(cx, cy, radius, endAngle);
  const largeArcFlag = sweep > Math.PI ? 1 : 0;

  if (innerRadius > 0) {
    const endInner = polarToCartesian(cx, cy, innerRadius, endAngle);
    const startInner = polarToCartesian(cx, cy, innerRadius, startAngle);
    return [
      `M ${startOuter.x} ${startOuter.y}`,
      `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${endOuter.x} ${endOuter.y}`,
      `L ${endInner.x} ${endInner.y}`,
      `A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${startInner.x} ${startInner.y}`,
      "Z",
    ].join(" ");
  }

  return [
    `M ${cx} ${cy}`,
    `L ${startOuter.x} ${startOuter.y}`,
    `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${endOuter.x} ${endOuter.y}`,
    "Z",
  ].join(" ");
}

const normalizedRows = computed(() =>
  rows.value
    .map((row) => ({
      ...row,
      label: row.label.trim(),
      numericValue: Number(row.value),
    }))
    .filter((row) => row.label && Number.isFinite(row.numericValue) && row.numericValue > 0),
);

const totalValue = computed(() => normalizedRows.value.reduce((sum, row) => sum + row.numericValue, 0));

function distributeLabelPositions(segments, minY, maxY, gap) {
  if (!segments.length) {
    return [];
  }

  const arranged = segments.map((segment) => ({ ...segment })).sort((left, right) => left.baseLabelY - right.baseLabelY);

  let cursor = minY;
  arranged.forEach((segment) => {
    segment.labelY = Math.max(segment.baseLabelY, cursor);
    cursor = segment.labelY + gap;
  });

  if (arranged[arranged.length - 1].labelY > maxY) {
    cursor = maxY;
    for (let index = arranged.length - 1; index >= 0; index -= 1) {
      arranged[index].labelY = Math.min(arranged[index].labelY, cursor);
      cursor = arranged[index].labelY - gap;
    }
  }

  return arranged.sort((left, right) => left.originalIndex - right.originalIndex);
}

const visibleSegments = computed(() => {
  if (!normalizedRows.value.length || !totalValue.value) {
    return [];
  }

  let cursor = -Math.PI / 2;
  const innerRadius = donutMode.value ? chartRadius * (donutRatio.value / 100) : 0;
  const rawSegments = normalizedRows.value.map((row, index) => {
    const percentage = row.numericValue / totalValue.value;
    const sweep = percentage * TAU;
    const startAngle = cursor;
    const endAngle = cursor + sweep;
    cursor = endAngle;

    const middleAngle = startAngle + sweep / 2;
    const lineStart = polarToCartesian(chartCenterX, chartCenterY, chartRadius + 4, middleAngle);
    const lineBreak = polarToCartesian(chartCenterX, chartCenterY, chartRadius + 24, middleAngle);
    const lineEndX = lineBreak.x + (Math.cos(middleAngle) >= 0 ? 26 : -26);
    const labelText = `${row.label} ${Math.round(percentage * 100)}%`;
    const onRightSide = Math.cos(middleAngle) >= 0;

    return {
      ...row,
      originalIndex: index,
      percentage,
      path: buildSlicePath(chartCenterX, chartCenterY, chartRadius, startAngle, endAngle, innerRadius),
      lineStart,
      lineBreak,
      lineEndX,
      baseLabelY: lineBreak.y + 4,
      labelY: lineBreak.y + 4,
      textAnchor: onRightSide ? "start" : "end",
      labelX: lineEndX + (onRightSide ? 6 : -6),
      side: onRightSide ? "right" : "left",
      showLabel: showLabels.value,
      labelText,
    };
  });

  if (!showLabels.value) {
    return rawSegments;
  }

  const labelMinY = 110;
  const labelMaxY = showLegend.value ? previewHeight - 126 : previewHeight - 34;
  const minGap = 22;

  const rightSegments = distributeLabelPositions(
    rawSegments.filter((segment) => segment.side === "right"),
    labelMinY,
    labelMaxY,
    minGap,
  );
  const leftSegments = distributeLabelPositions(
    rawSegments.filter((segment) => segment.side === "left"),
    labelMinY,
    labelMaxY,
    minGap,
  );

  const labelMap = new Map([...rightSegments, ...leftSegments].map((segment) => [segment.id, segment]));
  return rawSegments.map((segment) => {
    const adjusted = labelMap.get(segment.id);
    if (!adjusted) {
      return segment;
    }
    return {
      ...segment,
      labelY: adjusted.labelY,
      lineBreak: {
        x: segment.lineBreak.x,
        y: adjusted.labelY - 4,
      },
    };
  });
});

const legendLayout = computed(() => {
  if (!showLegend.value || !visibleSegments.value.length) {
    return [];
  }

  const itemCount = visibleSegments.value.length;
  const columns = itemCount <= 4 ? itemCount : itemCount <= 6 ? 2 : 3;
  const rowsPerColumn = Math.ceil(itemCount / columns);
  const startX = 92;
  const startY = previewHeight - 86;
  const columnWidth = (previewWidth - 184) / columns;

  return visibleSegments.value.map((item, index) => {
    const columnIndex = Math.floor(index / rowsPerColumn);
    const rowIndex = index % rowsPerColumn;
    return {
      ...item,
      x: startX + columnWidth * columnIndex,
      y: startY + rowIndex * 28,
    };
  });
});

const stats = computed(() => {
  const maxItem = normalizedRows.value.reduce((current, next) => {
    if (!current || next.numericValue > current.numericValue) {
      return next;
    }
    return current;
  }, null);

  return {
    count: normalizedRows.value.length,
    total: totalValue.value,
    largest: maxItem ? `${maxItem.label} · ${maxItem.numericValue}` : "暂无数据",
  };
});

function addRow() {
  const palette = palettes[activePaletteIndex.value];
  rows.value.push(createRow("", "", palette.colors[rows.value.length % palette.colors.length]));
}

function removeRow(id) {
  if (rows.value.length <= 1) {
    showToast({
      type: "info",
      title: "至少保留一行",
      message: "你可以先修改当前行内容。",
      duration: 1800,
    });
    return;
  }
  rows.value = rows.value.filter((row) => row.id !== id);
}

function applyPalette(index) {
  activePaletteIndex.value = index;
  const colors = palettes[index].colors;
  rows.value = rows.value.map((row, rowIndex) => ({
    ...row,
    color: colors[rowIndex % colors.length],
  }));
}

function resetSampleData() {
  applyPalette(0);
  chartTitle.value = "浏览器市场份额";
  chartSubtitle.value = "基础版图表工具，先从饼图开始";
  showLegend.value = true;
  showLabels.value = true;
  donutMode.value = false;
  donutRatio.value = 58;
  rows.value = [
    createRow("Chrome", 70, palettes[0].colors[0]),
    createRow("Firefox", 15, palettes[0].colors[1]),
    createRow("Edge", 10, palettes[0].colors[2]),
    createRow("Safari", 5, palettes[0].colors[3]),
  ];
  showToast({
    type: "success",
    title: "示例数据已恢复",
    message: "可以直接修改名称、数值和颜色继续使用。",
    duration: 1800,
  });
}

function chartFilename(extension) {
  const base = (chartTitle.value || "pie-chart")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/gi, "-")
    .replace(/^-+|-+$/g, "");
  return `${base || "pie-chart"}.${extension}`;
}

function serializeChartSvg() {
  if (!svgRef.value || !visibleSegments.value.length) {
    return "";
  }
  const serialized = new XMLSerializer().serializeToString(svgRef.value);
  return `<?xml version="1.0" encoding="UTF-8"?>\n${serialized}`;
}

function ensureChartReady() {
  if (!visibleSegments.value.length) {
    showToast({
      type: "error",
      title: "暂无可绘制数据",
      message: "请至少填写一条名称和大于 0 的数值。",
      duration: 2200,
    });
    return false;
  }
  return true;
}

function downloadSvg() {
  if (!ensureChartReady()) {
    return;
  }

  const blob = new Blob([serializeChartSvg()], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = chartFilename("svg");
  link.click();
  URL.revokeObjectURL(url);

  showToast({
    type: "success",
    title: "SVG 已导出",
    message: "矢量图已经开始下载。",
    duration: 1800,
  });
}

async function downloadPng() {
  if (!ensureChartReady()) {
    return;
  }

  const svgBlob = new Blob([serializeChartSvg()], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(svgBlob);
  const image = new Image();

  image.onload = () => {
    const canvas = document.createElement("canvas");
    const ratio = window.devicePixelRatio || 1;
    canvas.width = previewWidth * ratio;
    canvas.height = previewHeight * ratio;
    canvas.style.width = `${previewWidth}px`;
    canvas.style.height = `${previewHeight}px`;

    const context = canvas.getContext("2d");
    if (!context) {
      URL.revokeObjectURL(url);
      return;
    }

    context.scale(ratio, ratio);
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, previewWidth, previewHeight);
    context.drawImage(image, 0, 0, previewWidth, previewHeight);
    URL.revokeObjectURL(url);

    const link = document.createElement("a");
    link.href = canvas.toDataURL("image/png");
    link.download = chartFilename("png");
    link.click();

    showToast({
      type: "success",
      title: "PNG 已导出",
      message: "位图版本已经开始下载。",
      duration: 1800,
    });
  };

  image.onerror = () => {
    URL.revokeObjectURL(url);
    showToast({
      type: "error",
      title: "导出失败",
      message: "当前浏览器没有成功生成 PNG，请先尝试下载 SVG。",
      duration: 2200,
    });
  };

  image.src = url;
}
</script>

<template>
  <section class="tool-form local-tool-panel pie-chart-tool">
    <div class="local-tool-header pie-chart-header">
      <div class="local-tool-header-bar">
        <div>
          <h3>饼图制作</h3>
          <p>第一版先从最常用的饼图开始，支持实时预览、图例、标签、配色和 SVG/PNG 下载。</p>
        </div>
        <div class="pie-chart-stats">
          <div class="pie-chart-stat-card">
            <span>有效数据项</span>
            <strong>{{ stats.count }}</strong>
          </div>
          <div class="pie-chart-stat-card">
            <span>总数值</span>
            <strong>{{ stats.total || 0 }}</strong>
          </div>
          <div class="pie-chart-stat-card wide">
            <span>最大项</span>
            <strong>{{ stats.largest }}</strong>
          </div>
        </div>
      </div>
    </div>

    <div class="pie-chart-layout">
      <section class="pie-chart-panel controls">
        <div class="pie-chart-section">
          <div class="pie-chart-section-head">
            <h4>基础配置</h4>
            <p>先把标题和展示方式定下来，预览会实时更新。</p>
          </div>

          <label class="pie-chart-field">
            <span>图表标题</span>
            <input v-model="chartTitle" type="text" placeholder="例如：浏览器市场份额" />
          </label>

          <label class="pie-chart-field">
            <span>副标题</span>
            <input v-model="chartSubtitle" type="text" placeholder="例如：2026 年 4 月统计" />
          </label>

          <div class="pie-chart-toggle-row">
            <label class="pie-chart-toggle">
              <input v-model="showLegend" type="checkbox" />
              <span>显示图例</span>
            </label>
            <label class="pie-chart-toggle">
              <input v-model="showLabels" type="checkbox" />
              <span>显示标签</span>
            </label>
            <label class="pie-chart-toggle">
              <input v-model="donutMode" type="checkbox" />
              <span>切换为环形图</span>
            </label>
          </div>

          <label v-if="donutMode" class="pie-chart-field">
            <span>环形内径</span>
            <input v-model="donutRatio" type="range" min="30" max="72" />
            <small>{{ donutRatio }}%</small>
          </label>
        </div>

        <div class="pie-chart-section">
          <div class="pie-chart-section-head">
            <h4>颜色方案</h4>
            <p>先提供几套清爽配色，后面每个数据项也可以单独改色。</p>
          </div>

          <div class="pie-chart-palette-grid">
            <button
              v-for="(palette, index) in palettes"
              :key="palette.name"
              type="button"
              class="pie-chart-palette"
              :class="{ active: activePaletteIndex === index }"
              @click="applyPalette(index)"
            >
              <strong>{{ palette.name }}</strong>
              <span class="pie-chart-palette-swatches">
                <i v-for="color in palette.colors" :key="color" :style="{ background: color }"></i>
              </span>
            </button>
          </div>
        </div>

        <div class="pie-chart-section">
          <div class="pie-chart-section-head">
            <h4>数据配置</h4>
            <p>这版先用最直接的名称 + 数值方式录入，适合先把基础图表跑起来。</p>
          </div>

          <div class="pie-chart-data-table">
            <div class="pie-chart-data-head">
              <span>名称</span>
              <span>数值</span>
              <span>颜色</span>
              <span>操作</span>
            </div>

            <div v-for="row in rows" :key="row.id" class="pie-chart-data-row">
              <input v-model="row.label" type="text" placeholder="项目名称" />
              <input v-model="row.value" type="number" min="0" step="any" placeholder="0" />
              <input v-model="row.color" type="color" />
              <button type="button" class="pie-chart-icon-button" @click="removeRow(row.id)">删除</button>
            </div>
          </div>

          <div class="pie-chart-actions">
            <button type="button" class="secondary-button" @click="addRow">新增数据项</button>
            <button type="button" class="secondary-button" @click="resetSampleData">恢复示例</button>
          </div>
        </div>
      </section>

      <section class="pie-chart-panel preview">
        <div class="pie-chart-preview-head">
          <div>
            <p class="section-kicker">实时预览</p>
            <h4>{{ chartTitle || "饼图预览" }}</h4>
            <p>{{ chartSubtitle || "支持实时查看数据占比关系。" }}</p>
          </div>
          <div class="pie-chart-actions">
            <button type="button" class="secondary-button" @click="downloadSvg">下载 SVG</button>
            <button type="button" @click="downloadPng">下载 PNG</button>
          </div>
        </div>

        <div class="pie-chart-preview-stage">
          <svg
            ref="svgRef"
            class="pie-chart-svg"
            xmlns="http://www.w3.org/2000/svg"
            :viewBox="`0 0 ${previewWidth} ${previewHeight}`"
            :width="previewWidth"
            :height="previewHeight"
            role="img"
            :aria-label="chartTitle || '饼图预览'"
          >
            <rect width="100%" height="100%" fill="#ffffff" rx="28" />
            <text x="56" y="54" class="pie-chart-svg-title">{{ chartTitle || "饼图预览" }}</text>
            <text x="56" y="82" class="pie-chart-svg-subtitle">
              {{ chartSubtitle || "输入数据后会自动更新图表" }}
            </text>

            <template v-if="visibleSegments.length">
              <path
                v-for="segment in visibleSegments"
                :key="segment.id"
                :d="segment.path"
                :fill="segment.color"
                stroke="#ffffff"
                stroke-width="3"
              />

              <template v-if="showLabels">
                <g v-for="segment in visibleSegments.filter((item) => item.showLabel)" :key="`label-${segment.id}`">
                  <path
                    :d="`M ${segment.lineStart.x} ${segment.lineStart.y} L ${segment.lineBreak.x} ${segment.lineBreak.y} L ${segment.lineEndX} ${segment.lineBreak.y}`"
                    fill="none"
                    stroke="#8aa2b2"
                    stroke-width="1.5"
                  />
                  <text
                    :x="segment.labelX"
                    :y="segment.labelY"
                    :text-anchor="segment.textAnchor"
                    class="pie-chart-svg-label"
                  >
                    {{ segment.labelText }}
                  </text>
                </g>
              </template>

              <template v-if="showLegend">
                <g v-for="legend in legendLayout" :key="`legend-${legend.id}`">
                  <rect :x="legend.x" :y="legend.y - 11" width="14" height="14" rx="4" :fill="legend.color" />
                  <text :x="legend.x + 22" :y="legend.y" class="pie-chart-svg-legend">
                    {{ legend.label }} · {{ legend.numericValue }}
                  </text>
                </g>
              </template>

              <g v-if="donutMode">
                <text x="252" y="198" text-anchor="middle" class="pie-chart-svg-total-label">总计</text>
                <text x="252" y="226" text-anchor="middle" class="pie-chart-svg-total-value">{{ totalValue }}</text>
              </g>
            </template>

            <g v-else>
              <circle cx="252" cy="208" r="96" fill="#f5f8fb" stroke="#d9e5ec" stroke-dasharray="8 8" />
              <text x="252" y="202" text-anchor="middle" class="pie-chart-svg-empty-title">等待有效数据</text>
              <text x="252" y="228" text-anchor="middle" class="pie-chart-svg-empty-subtitle">
                请填写名称和大于 0 的数值
              </text>
            </g>
          </svg>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.pie-chart-tool {
  display: grid;
  gap: 22px;
}

.pie-chart-header {
  margin-bottom: 0;
}

.pie-chart-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.pie-chart-stat-card {
  min-width: 128px;
  padding: 12px 14px;
  border-radius: 18px;
  border: 1px solid rgba(31, 157, 139, 0.18);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(240, 250, 248, 0.82));
}

.pie-chart-stat-card.wide {
  min-width: 196px;
}

.pie-chart-stat-card span {
  display: block;
  color: var(--muted);
  font-size: 13px;
}

.pie-chart-stat-card strong {
  display: block;
  margin-top: 6px;
  color: #175f56;
  font-size: 20px;
}

.pie-chart-layout {
  display: grid;
  grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.pie-chart-panel {
  border-radius: 24px;
  border: 1px solid rgba(197, 216, 235, 0.78);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(246, 251, 255, 0.8));
  box-shadow: 0 22px 44px rgba(99, 135, 173, 0.08);
}

.pie-chart-panel.controls {
  padding: 18px;
  display: grid;
  gap: 18px;
}

.pie-chart-panel.preview {
  padding: 18px;
  display: grid;
  gap: 16px;
}

.pie-chart-section {
  display: grid;
  gap: 14px;
}

.pie-chart-section-head h4,
.pie-chart-preview-head h4 {
  margin: 0 0 6px;
  font-size: 18px;
}

.pie-chart-section-head p,
.pie-chart-preview-head p {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}

.pie-chart-field {
  display: grid;
  gap: 8px;
}

.pie-chart-field span {
  color: var(--ink);
  font-weight: 600;
}

.pie-chart-field small {
  color: var(--muted);
}

.pie-chart-toggle-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pie-chart-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(197, 216, 235, 0.82);
  background: rgba(255, 255, 255, 0.78);
  color: var(--ink);
}

.pie-chart-palette-grid {
  display: grid;
  gap: 10px;
}

.pie-chart-palette {
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(197, 216, 235, 0.78);
  background: rgba(255, 255, 255, 0.82);
  text-align: left;
}

.pie-chart-palette.active {
  border-color: rgba(31, 157, 139, 0.42);
  box-shadow: 0 0 0 4px rgba(31, 157, 139, 0.08);
}

.pie-chart-palette strong {
  color: var(--ink);
}

.pie-chart-palette-swatches {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pie-chart-palette-swatches i {
  display: inline-block;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.8);
}

.pie-chart-data-table {
  display: grid;
  gap: 8px;
}

.pie-chart-data-head,
.pie-chart-data-row {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(100px, 0.8fr) 68px 72px;
  gap: 10px;
  align-items: center;
}

.pie-chart-data-head {
  padding: 0 4px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
}

.pie-chart-data-row input[type="color"] {
  width: 100%;
  min-height: 48px;
  padding: 6px;
  border-radius: 14px;
  cursor: pointer;
}

.pie-chart-icon-button {
  min-width: 0;
  min-height: 46px;
  border: 1px solid #dbe3eb;
  border-radius: 14px;
  background: #fff;
  color: #7b8794;
}

.pie-chart-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pie-chart-preview-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.pie-chart-preview-stage {
  overflow: auto;
  border-radius: 24px;
  border: 1px solid rgba(216, 229, 236, 0.9);
  background: #ffffff;
}

.pie-chart-svg {
  display: block;
  width: 100%;
  min-width: 680px;
  height: auto;
}

.pie-chart-svg-title {
  fill: #243647;
  font-size: 28px;
  font-weight: 700;
}

.pie-chart-svg-subtitle,
.pie-chart-svg-label,
.pie-chart-svg-legend,
.pie-chart-svg-total-label,
.pie-chart-svg-empty-subtitle {
  fill: #6d7a86;
  font-size: 14px;
}

.pie-chart-svg-label {
  font-size: 13px;
}

.pie-chart-svg-total-label,
.pie-chart-svg-empty-title {
  fill: #4f6474;
  font-size: 15px;
  font-weight: 600;
}

.pie-chart-svg-total-value {
  fill: #1d3b49;
  font-size: 28px;
  font-weight: 700;
}

.pie-chart-svg-empty-subtitle {
  font-size: 13px;
}

@media (max-width: 1080px) {
  .pie-chart-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .pie-chart-stat-card,
  .pie-chart-stat-card.wide {
    min-width: calc(50% - 6px);
  }

  .pie-chart-data-head,
  .pie-chart-data-row {
    grid-template-columns: minmax(0, 1.4fr) minmax(86px, 0.8fr) 60px 64px;
    gap: 8px;
  }

  .pie-chart-svg {
    min-width: 620px;
  }
}
</style>
