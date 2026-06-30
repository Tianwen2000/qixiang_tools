<script setup>
// 文件说明：定义 ToolChartStudio 前端组件。
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";

import { showToast } from "../utils/toast.js";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const route = useRoute();
const TAU = Math.PI * 2;
const previewWidth = 900;
const previewHeight = 560;
const svgRef = ref(null);
const activePaletteIndex = ref(0);
const chartTitle = ref("");
const chartSubtitle = ref("");
const dataText = ref("");
const showLegend = ref(true);
const showLabels = ref(true);
const showGrid = ref(true);
const donutRatio = ref(58);
const rotateWords = ref(true);

const palettes = [
  {
    name: "清风蓝绿",
    colors: ["#4f7cff", "#63c172", "#f6c453", "#ef7d57", "#7f96ff", "#43b7c8", "#f08cb3", "#6a84ff"],
  },
  {
    name: "珊瑚暖色",
    colors: ["#ff7a59", "#ffb457", "#ffd166", "#7cc576", "#5aa9ff", "#9b7cff", "#ec6f93", "#5cc9a7"],
  },
  {
    name: "森林薄荷",
    colors: ["#147a6e", "#27ae60", "#6fcf97", "#a8e6cf", "#f3d46b", "#f28c64", "#5c7cfa", "#4dabf7"],
  },
];

const chartDefinitions = [
  {
    slug: "pie-chart-maker",
    name: "饼图制作",
    kind: "pie",
    title: "浏览器市场份额",
    subtitle: "用最直接的方式查看占比关系",
    dataHint: "格式：名称,数值",
    sampleData: "名称,数值\nChrome,70\nFirefox,15\nEdge,10\nSafari,5",
    defaults: { legend: true, labels: true, grid: false },
  },
  {
    slug: "donut-chart-maker",
    name: "环形图制作",
    kind: "donut",
    title: "渠道转化占比",
    subtitle: "适合展示结构和总量汇总",
    dataHint: "格式：名称,数值",
    sampleData: "名称,数值\n自然搜索,44\n广告投放,28\n社媒内容,18\n其它,10",
    defaults: { legend: true, labels: true, grid: false },
  },
  {
    slug: "bar-chart-maker",
    name: "柱状图制作",
    kind: "bar",
    title: "季度销售额对比",
    subtitle: "快速对比多个分类的数值高低",
    dataHint: "格式：名称,数值",
    sampleData: "季度,数值\nQ1,120\nQ2,168\nQ3,146\nQ4,202",
    defaults: { legend: false, labels: true, grid: true },
  },
  {
    slug: "horizontal-bar-chart-maker",
    name: "条形图制作",
    kind: "horizontal-bar",
    title: "城市访问量排行",
    subtitle: "适合名称较长的分类比较",
    dataHint: "格式：名称,数值",
    sampleData: "城市,访问量\n上海,268\n北京,236\n深圳,208\n杭州,184\n成都,153",
    defaults: { legend: false, labels: true, grid: true },
  },
  {
    slug: "stacked-bar-chart-maker",
    name: "堆叠柱状图制作",
    kind: "stacked-bar",
    title: "季度渠道构成",
    subtitle: "看总量也看内部占比",
    dataHint: "格式：分类,系列 A,系列 B,系列 C",
    sampleData: "季度,线上,门店,渠道\nQ1,60,38,22\nQ2,82,46,40\nQ3,74,44,28\nQ4,96,58,48",
    defaults: { legend: true, labels: false, grid: true },
  },
  {
    slug: "combo-chart-maker",
    name: "折柱图制作",
    kind: "combo",
    title: "销售额与转化率",
    subtitle: "用柱形和折线组合看两组相关指标",
    dataHint: "格式：分类,柱状值,折线值",
    sampleData: "月份,销售额,转化率\n1月,120,3.8\n2月,148,4.2\n3月,176,4.6\n4月,158,4.1\n5月,204,5.0",
    defaults: { legend: true, labels: false, grid: true },
  },
  {
    slug: "line-chart-maker",
    name: "折线图制作",
    kind: "line",
    title: "近七日访问趋势",
    subtitle: "适合观察阶段变化和波动",
    dataHint: "格式：分类,数值",
    sampleData: "日期,访问量\n周一,68\n周二,92\n周三,86\n周四,110\n周五,124\n周六,118\n周日,136",
    defaults: { legend: false, labels: true, grid: true },
  },
  {
    slug: "area-chart-maker",
    name: "面积图制作",
    kind: "area",
    title: "活跃用户走势",
    subtitle: "强化体量感的趋势图",
    dataHint: "格式：分类,数值",
    sampleData: "日期,活跃用户\n周一,32\n周二,46\n周三,52\n周四,64\n周五,60\n周六,72\n周日,78",
    defaults: { legend: false, labels: false, grid: true },
  },
  {
    slug: "stacked-area-chart-maker",
    name: "堆叠面积图制作",
    kind: "stacked-area",
    title: "流量来源变化",
    subtitle: "同时看整体走势和各部分贡献",
    dataHint: "格式：分类,系列 A,系列 B,系列 C",
    sampleData: "月份,自然流量,广告流量,社交流量\n1月,18,12,6\n2月,22,14,7\n3月,26,17,8\n4月,30,20,10\n5月,32,22,11",
    defaults: { legend: true, labels: false, grid: true },
  },
  {
    slug: "scatter-chart-maker",
    name: "散点图制作",
    kind: "scatter",
    title: "转化与客单价分布",
    subtitle: "适合看相关性和聚类分布",
    dataHint: "格式：名称,X,Y,大小",
    sampleData: "名称,转化率,客单价,流量\nA 渠道,2.2,68,10\nB 渠道,3.1,82,16\nC 渠道,4.4,95,22\nD 渠道,3.8,72,14\nE 渠道,5.1,118,26",
    defaults: { legend: false, labels: true, grid: true },
  },
  {
    slug: "radar-chart-maker",
    name: "雷达图制作",
    kind: "radar",
    title: "产品能力画像",
    subtitle: "适合多维评分和综合能力展示",
    dataHint: "格式：名称,数值",
    sampleData: "维度,评分\n性能,86\n稳定性,92\n易用性,78\n拓展性,83\n成本控制,74\n生态适配,88",
    defaults: { legend: false, labels: true, grid: true },
  },
  {
    slug: "funnel-chart-maker",
    name: "漏斗图制作",
    kind: "funnel",
    title: "注册转化漏斗",
    subtitle: "查看逐层转化与流失情况",
    dataHint: "格式：名称,数值",
    sampleData: "阶段,人数\n浏览首页,1200\n点击注册,680\n完成注册,340\n完成首单,126",
    defaults: { legend: false, labels: true, grid: false },
  },
  {
    slug: "rose-chart-maker",
    name: "南丁格尔玫瑰图制作",
    kind: "rose",
    title: "主题热度分布",
    subtitle: "用极坐标半径强化排序差异",
    dataHint: "格式：名称,数值",
    sampleData: "主题,热度\n前端,86\n后端,72\nAI,96\n设计,58\n数据分析,64\n测试,42",
    defaults: { legend: true, labels: true, grid: false },
  },
  {
    slug: "heatmap-chart-maker",
    name: "热力图制作",
    kind: "heatmap",
    title: "星期与时段热度",
    subtitle: "适合做二维强度分布图",
    dataHint: "格式：横轴,纵轴,值",
    sampleData:
      "星期,时段,值\n周一,上午,12\n周一,下午,18\n周一,晚上,26\n周二,上午,16\n周二,下午,20\n周二,晚上,30\n周三,上午,14\n周三,下午,24\n周三,晚上,28\n周四,上午,18\n周四,下午,26\n周四,晚上,34",
    defaults: { legend: true, labels: true, grid: false },
  },
  {
    slug: "treemap-chart-maker",
    name: "矩形树图制作",
    kind: "treemap",
    title: "业务模块流量占比",
    subtitle: "在一个平面里看面积大小关系",
    dataHint: "格式：名称,数值",
    sampleData: "模块,流量\n首页,360\n搜索,240\n商品详情,190\n购物车,120\n订单中心,96\n会员中心,84\n营销活动,70",
    defaults: { legend: true, labels: true, grid: false },
  },
  {
    slug: "tree-chart-maker",
    name: "树形图制作",
    kind: "tree",
    title: "业务结构树",
    subtitle: "适合看层级结构和分支关系",
    dataHint: "格式：父级,子级,值",
    sampleData:
      "父级,子级,值\n平台,产品中心,48\n平台,运营中心,32\n产品中心,网页端,18\n产品中心,移动端,22\n运营中心,广告投放,14\n运营中心,内容社区,18",
    defaults: { legend: false, labels: true, grid: false },
  },
  {
    slug: "sankey-chart-maker",
    name: "桑基图制作",
    kind: "sankey",
    title: "流量路径分配",
    subtitle: "适合看多阶段来源去向和分配宽度",
    dataHint: "格式：来源,去向,值",
    sampleData:
      "来源,去向,值\n访问首页,搜索,420\n访问首页,分类页,260\n搜索,商品详情,210\n分类页,商品详情,154\n商品详情,加购物车,118\n加购物车,提交订单,72\n提交订单,支付成功,54",
    defaults: { legend: false, labels: true, grid: false },
  },
  {
    slug: "word-cloud-maker",
    name: "词云图制作",
    kind: "word-cloud",
    title: "评论高频词",
    subtitle: "按频次大小生成词云布局",
    dataHint: "格式：词语,权重",
    sampleData: "词语,权重\n稳定,88\n顺滑,80\n清晰,76\n效率,70\n轻量,66\n好用,62\n专业,56\n快速,52\n柔和,48\n可靠,44\n图表,40\n工具,36",
    defaults: { legend: false, labels: true, grid: false },
  },
  {
    slug: "kline-chart-maker",
    name: "K 线图制作",
    kind: "kline",
    title: "近七日价格区间",
    subtitle: "适合展示开高低收数据",
    dataHint: "格式：日期,开盘,最高,最低,收盘",
    sampleData: "日期,开盘,最高,最低,收盘\n04-01,102,108,98,106\n04-02,106,112,104,109\n04-03,109,114,103,105\n04-04,105,110,101,108\n04-05,108,116,107,114\n04-06,114,118,111,112",
    defaults: { legend: false, labels: false, grid: true },
  },
];

const definitionMap = new Map(chartDefinitions.map((definition) => [definition.slug, definition]));
const currentDefinition = computed(() => definitionMap.get(props.tool.slug) || chartDefinitions[0]);
const quickSwitchLinks = computed(() =>
  chartDefinitions.map((definition) => ({
    ...definition,
    to: {
      name: "tool",
      params: { slug: definition.slug },
      query: route.query,
    },
  })),
);

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function isNumeric(value) {
  return value !== "" && Number.isFinite(Number(value));
}

function formatNumber(value) {
  if (!Number.isFinite(value)) {
    return "0";
  }
  if (Math.abs(value) >= 100 || Number.isInteger(value)) {
    return String(Math.round(value * 100) / 100).replace(/\.00$/, "");
  }
  return String(Math.round(value * 100) / 100).replace(/0+$/, "").replace(/\.$/, "");
}

function niceMax(value) {
  if (!Number.isFinite(value) || value <= 0) {
    return 1;
  }
  const magnitude = 10 ** Math.floor(Math.log10(value));
  const residual = value / magnitude;
  let nice = 10;
  if (residual <= 1) {
    nice = 1;
  } else if (residual <= 2) {
    nice = 2;
  } else if (residual <= 5) {
    nice = 5;
  }
  return nice * magnitude;
}

function buildTicks(maxValue, count = 5) {
  const top = niceMax(maxValue);
  return Array.from({ length: count + 1 }, (_, index) => (top / count) * index);
}

function splitRow(line) {
  const delimiter = line.includes("\t") ? "\t" : line.includes(",") ? "," : line.includes("，") ? "，" : /\s{2,}/.test(line) ? /\s{2,}/ : null;
  if (!delimiter) {
    return [line.trim()];
  }
  return line
    .split(delimiter)
    .map((item) => item.trim())
    .filter((item, index, array) => !(item === "" && index === array.length - 1));
}

function parseTable(text) {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map(splitRow)
    .filter((row) => row.length);
}

function withPaletteColor(items, colors) {
  return items.map((item, index) => ({
    ...item,
    color: item.color || colors[index % colors.length],
  }));
}

function parseCategoryRows(rows, colors) {
  if (!rows.length) {
    return { error: "请先输入数据" };
  }

  const hasHeader = rows[0].length > 1 && !isNumeric(rows[0][1]);
  const dataRows = hasHeader ? rows.slice(1) : rows;
  const items = withPaletteColor(
    dataRows
      .map((row) => ({
        label: row[0] || "",
        value: Number(row[1]),
      }))
      .filter((row) => row.label && Number.isFinite(row.value) && row.value > 0),
    colors,
  );

  if (!items.length) {
    return { error: "请至少提供一条有效的 名称,数值 数据" };
  }
  return { items };
}

function parseMatrixRows(rows, colors) {
  if (rows.length < 2) {
    return { error: "请至少提供表头和一行数据" };
  }

  const hasHeader = rows[0].slice(1).some((value) => !isNumeric(value));
  const header = hasHeader ? rows[0] : ["分类", ...rows[0].slice(1).map((_, index) => `系列 ${index + 1}`)];
  const dataRows = hasHeader ? rows.slice(1) : rows;
  const series = header.slice(1).map((name, index) => ({
    name: name || `系列 ${index + 1}`,
    color: colors[index % colors.length],
  }));
  const items = dataRows
    .map((row) => ({
      label: row[0] || "",
      values: row.slice(1, series.length + 1).map((value) => Number(value)),
    }))
    .filter((row) => row.label && row.values.some((value) => Number.isFinite(value)));

  if (!items.length || !series.length) {
    return { error: "矩阵数据格式不正确，请检查表头和数值列" };
  }

  return { header, series, items };
}

function parseScatterRows(rows, colors) {
  if (!rows.length) {
    return { error: "请先输入数据" };
  }
  const hasHeader = rows[0].length > 2 && (!isNumeric(rows[0][1]) || !isNumeric(rows[0][2]));
  const dataRows = hasHeader ? rows.slice(1) : rows;
  const items = withPaletteColor(
    dataRows
      .map((row) => ({
        label: row[0] || "",
        x: Number(row[1]),
        y: Number(row[2]),
        size: row[3] !== undefined && row[3] !== "" ? Number(row[3]) : 12,
      }))
      .filter((row) => row.label && Number.isFinite(row.x) && Number.isFinite(row.y)),
    colors,
  );

  if (!items.length) {
    return { error: "请至少提供一条有效的 名称,X,Y,大小 数据" };
  }

  return { items };
}

function parseHeatmapRows(rows) {
  if (!rows.length) {
    return { error: "请先输入数据" };
  }

  const hasHeader = rows[0].length > 2 && !isNumeric(rows[0][2]);
  const dataRows = hasHeader ? rows.slice(1) : rows;
  const items = dataRows
    .map((row) => ({
      x: row[0] || "",
      y: row[1] || "",
      value: Number(row[2]),
    }))
    .filter((row) => row.x && row.y && Number.isFinite(row.value));

  if (!items.length) {
    return { error: "请至少提供一条有效的 横轴,纵轴,值 数据" };
  }

  return { items };
}

function parseKlineRows(rows) {
  if (!rows.length) {
    return { error: "请先输入数据" };
  }

  const hasHeader = rows[0].length > 4 && !isNumeric(rows[0][1]);
  const dataRows = hasHeader ? rows.slice(1) : rows;
  const items = dataRows
    .map((row) => ({
      label: row[0] || "",
      open: Number(row[1]),
      high: Number(row[2]),
      low: Number(row[3]),
      close: Number(row[4]),
    }))
    .filter(
      (row) =>
        row.label &&
        Number.isFinite(row.open) &&
        Number.isFinite(row.high) &&
        Number.isFinite(row.low) &&
        Number.isFinite(row.close),
    );

  if (!items.length) {
    return { error: "请至少提供一条有效的 日期,开盘,最高,最低,收盘 数据" };
  }

  return { items };
}

function parseRelationRows(rows) {
  if (!rows.length) {
    return { error: "请先输入数据" };
  }

  const hasHeader = rows[0].length > 2 && !isNumeric(rows[0][2]);
  const dataRows = hasHeader ? rows.slice(1) : rows;
  const links = dataRows
    .map((row) => ({
      source: row[0] || "",
      target: row[1] || "",
      value: row[2] !== undefined && row[2] !== "" ? Number(row[2]) : 1,
    }))
    .filter((row) => row.source && row.target && Number.isFinite(row.value) && row.value > 0);

  if (!links.length) {
    return { error: "请至少提供一条有效的 来源,去向,值 数据" };
  }

  return { links };
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

function interpolateColor(from, to, progress) {
  const parseHex = (hex) => {
    const normalized = hex.replace("#", "");
    return [
      Number.parseInt(normalized.slice(0, 2), 16),
      Number.parseInt(normalized.slice(2, 4), 16),
      Number.parseInt(normalized.slice(4, 6), 16),
    ];
  };
  const [fr, fg, fb] = parseHex(from);
  const [tr, tg, tb] = parseHex(to);
  const value = clamp(progress, 0, 1);
  const r = Math.round(fr + (tr - fr) * value);
  const g = Math.round(fg + (tg - fg) * value);
  const b = Math.round(fb + (tb - fb) * value);
  return `rgb(${r}, ${g}, ${b})`;
}

function sliceTreemap(items, x, y, width, height, vertical = width >= height) {
  if (!items.length) {
    return [];
  }
  if (items.length === 1) {
    return [{ ...items[0], x, y, width, height }];
  }

  const total = items.reduce((sum, item) => sum + item.value, 0);
  let accumulator = 0;
  let splitIndex = 1;
  for (let index = 0; index < items.length; index += 1) {
    accumulator += items[index].value;
    if (accumulator >= total / 2) {
      splitIndex = index + 1;
      break;
    }
  }

  const firstGroup = items.slice(0, splitIndex);
  const secondGroup = items.slice(splitIndex);
  const firstTotal = firstGroup.reduce((sum, item) => sum + item.value, 0);
  const ratio = total ? firstTotal / total : 0.5;

  if (vertical) {
    const firstWidth = width * ratio;
    return [
      ...sliceTreemap(firstGroup, x, y, firstWidth, height, !vertical),
      ...sliceTreemap(secondGroup, x + firstWidth, y, width - firstWidth, height, !vertical),
    ];
  }

  const firstHeight = height * ratio;
  return [
    ...sliceTreemap(firstGroup, x, y, width, firstHeight, !vertical),
    ...sliceTreemap(secondGroup, x, y + firstHeight, width, height - firstHeight, !vertical),
  ];
}

function buildPieLikeModel(items, kind) {
  const centerX = 280;
  const centerY = 232;
  const radius = 150;
  const innerRadius = kind === "donut" ? radius * (donutRatio.value / 100) : 0;
  const total = items.reduce((sum, item) => sum + item.value, 0);
  let cursor = -Math.PI / 2;

  const rawSegments = items.map((item, index) => {
    const percentage = item.value / total;
    const sweep = kind === "rose" ? TAU / items.length : percentage * TAU;
    const startAngle = cursor;
    const endAngle = cursor + sweep;
    cursor = endAngle;
    const middleAngle = startAngle + sweep / 2;
    const outerRadius = kind === "rose" ? 60 + (item.value / Math.max(...items.map((entry) => entry.value))) * (radius - 60) : radius;
    const lineStart = polarToCartesian(centerX, centerY, outerRadius + 4, middleAngle);
    const lineBreak = polarToCartesian(centerX, centerY, outerRadius + 28, middleAngle);
    const lineEndX = lineBreak.x + (Math.cos(middleAngle) >= 0 ? 28 : -28);
    return {
      ...item,
      originalIndex: index,
      percentage,
      path: buildSlicePath(centerX, centerY, outerRadius, startAngle, endAngle, kind === "donut" ? innerRadius : 0),
      lineStart,
      lineBreak,
      lineEndX,
      baseLabelY: lineBreak.y + 4,
      labelY: lineBreak.y + 4,
      textAnchor: Math.cos(middleAngle) >= 0 ? "start" : "end",
      labelX: lineEndX + (Math.cos(middleAngle) >= 0 ? 6 : -6),
      side: Math.cos(middleAngle) >= 0 ? "right" : "left",
      labelText: `${item.label} ${Math.round(percentage * 100)}%`,
    };
  });

  if (showLabels.value) {
    const minY = 118;
    const maxY = showLegend.value ? previewHeight - 138 : previewHeight - 40;
    const rightLabels = distributeLabelPositions(rawSegments.filter((segment) => segment.side === "right"), minY, maxY, 22);
    const leftLabels = distributeLabelPositions(rawSegments.filter((segment) => segment.side === "left"), minY, maxY, 22);
    const labelMap = new Map([...rightLabels, ...leftLabels].map((segment) => [segment.labelText, segment]));
    rawSegments.forEach((segment) => {
      const adjusted = labelMap.get(segment.labelText);
      if (adjusted) {
        segment.labelY = adjusted.labelY;
        segment.lineBreak = { x: segment.lineBreak.x, y: adjusted.labelY - 4 };
      }
    });
  }

  return {
    kind,
    total,
    segments: rawSegments,
    legendEntries: items.map((item) => ({ color: item.color, label: item.label, value: item.value })),
    centerX,
    centerY,
  };
}

function buildPlotArea(hasBottomLegend = false) {
  return {
    x: 84,
    y: 118,
    width: previewWidth - 160,
    height: hasBottomLegend ? 280 : 340,
    bottomY: hasBottomLegend ? 398 : 458,
  };
}

function buildBarModel(items) {
  const plot = buildPlotArea(false);
  const maxValue = Math.max(...items.map((item) => item.value));
  const topValue = niceMax(maxValue);
  const ticks = buildTicks(topValue);
  const bandWidth = plot.width / items.length;
  const barWidth = Math.min(52, bandWidth * 0.56);

  return {
    kind: "bar",
    plot,
    ticks,
    bars: items.map((item, index) => {
      const height = (item.value / topValue) * plot.height;
      return {
        ...item,
        x: plot.x + bandWidth * index + (bandWidth - barWidth) / 2,
        y: plot.y + plot.height - height,
        width: barWidth,
        height,
        labelX: plot.x + bandWidth * index + bandWidth / 2,
      };
    }),
  };
}

function buildHorizontalBarModel(items) {
  const plot = buildPlotArea(false);
  const maxValue = Math.max(...items.map((item) => item.value));
  const topValue = niceMax(maxValue);
  const ticks = buildTicks(topValue);
  const bandHeight = plot.height / items.length;
  const barHeight = Math.min(36, bandHeight * 0.62);

  return {
    kind: "horizontal-bar",
    plot,
    ticks,
    bars: items.map((item, index) => {
      const width = (item.value / topValue) * plot.width;
      return {
        ...item,
        x: plot.x,
        y: plot.y + bandHeight * index + (bandHeight - barHeight) / 2,
        width,
        height: barHeight,
        labelY: plot.y + bandHeight * index + bandHeight / 2 + 4,
      };
    }),
  };
}

function buildLineLikeModel(items, kind) {
  const plot = buildPlotArea(false);
  const maxValue = Math.max(...items.map((item) => item.value));
  const topValue = niceMax(maxValue);
  const ticks = buildTicks(topValue);
  const stepX = items.length === 1 ? 0 : plot.width / (items.length - 1);
  const points = items.map((item, index) => ({
    ...item,
    x: plot.x + stepX * index,
    y: plot.y + plot.height - (item.value / topValue) * plot.height,
  }));
  const linePath = points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
  const areaPath =
    kind === "area"
      ? `${linePath} L ${points[points.length - 1].x} ${plot.y + plot.height} L ${points[0].x} ${plot.y + plot.height} Z`
      : "";

  return {
    kind,
    plot,
    ticks,
    points,
    linePath,
    areaPath,
  };
}

function buildStackedBarModel(matrix) {
  const plot = buildPlotArea(true);
  const totals = matrix.items.map((item) => item.values.reduce((sum, value) => sum + (Number.isFinite(value) ? value : 0), 0));
  const topValue = niceMax(Math.max(...totals, 1));
  const ticks = buildTicks(topValue);
  const bandWidth = plot.width / matrix.items.length;
  const barWidth = Math.min(52, bandWidth * 0.56);
  const bars = [];

  matrix.items.forEach((item, itemIndex) => {
    let cursor = 0;
    item.values.forEach((value, seriesIndex) => {
      const safeValue = Number.isFinite(value) ? value : 0;
      const height = (safeValue / topValue) * plot.height;
      bars.push({
        x: plot.x + bandWidth * itemIndex + (bandWidth - barWidth) / 2,
        y: plot.y + plot.height - height - cursor,
        width: barWidth,
        height,
        color: matrix.series[seriesIndex]?.color || palettes[activePaletteIndex.value].colors[seriesIndex % palettes[activePaletteIndex.value].colors.length],
        label: item.label,
      });
      cursor += height;
    });
  });

  return {
    kind: "stacked-bar",
    plot,
    ticks,
    bars,
    categories: matrix.items.map((item, index) => ({
      label: item.label,
      x: plot.x + bandWidth * index + bandWidth / 2,
    })),
    legendEntries: matrix.series.map((series) => ({ color: series.color, label: series.name })),
  };
}

function buildComboModel(matrix) {
  const plot = buildPlotArea(true);
  const barValues = matrix.items.map((item) => Number(item.values[0] || 0));
  const lineValues = matrix.items.map((item) => Number(item.values[1] || 0));
  const leftTop = niceMax(Math.max(...barValues, 1));
  const rightTop = niceMax(Math.max(...lineValues, 1));
  const leftTicks = buildTicks(leftTop);
  const rightTicks = buildTicks(rightTop);
  const bandWidth = plot.width / matrix.items.length;
  const barWidth = Math.min(42, bandWidth * 0.42);

  const bars = matrix.items.map((item, index) => {
    const value = Number(item.values[0] || 0);
    const height = (value / leftTop) * plot.height;
    return {
      x: plot.x + bandWidth * index + (bandWidth - barWidth) / 2,
      y: plot.y + plot.height - height,
      width: barWidth,
      height,
      labelX: plot.x + bandWidth * index + bandWidth / 2,
      value,
    };
  });

  const linePoints = matrix.items.map((item, index) => {
    const value = Number(item.values[1] || 0);
    return {
      label: item.label,
      x: plot.x + bandWidth * index + bandWidth / 2,
      y: plot.y + plot.height - (value / rightTop) * plot.height,
      value,
    };
  });

  return {
    kind: "combo",
    plot,
    bars,
    leftTicks,
    rightTicks,
    linePoints,
    linePath: linePoints.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" "),
    legendEntries: [
      { color: palettes[activePaletteIndex.value].colors[0], label: matrix.series[0]?.name || "柱状值" },
      { color: palettes[activePaletteIndex.value].colors[1], label: matrix.series[1]?.name || "折线值" },
    ],
  };
}

function buildStackedAreaModel(matrix) {
  const plot = buildPlotArea(true);
  const totals = matrix.items.map((item) => item.values.reduce((sum, value) => sum + (Number.isFinite(value) ? value : 0), 0));
  const topValue = niceMax(Math.max(...totals, 1));
  const ticks = buildTicks(topValue);
  const stepX = matrix.items.length === 1 ? 0 : plot.width / (matrix.items.length - 1);
  const cumulative = matrix.items.map(() => 0);
  const areas = matrix.series.map((series, seriesIndex) => {
    const topPoints = matrix.items.map((item, itemIndex) => {
      cumulative[itemIndex] += Number(item.values[seriesIndex] || 0);
      return {
        x: plot.x + stepX * itemIndex,
        y: plot.y + plot.height - (cumulative[itemIndex] / topValue) * plot.height,
      };
    });
    const bottomPoints = matrix.items
      .map((item, itemIndex) => {
        const lowerValue = cumulative[itemIndex] - Number(item.values[seriesIndex] || 0);
        return {
          x: plot.x + stepX * itemIndex,
          y: plot.y + plot.height - (lowerValue / topValue) * plot.height,
        };
      })
      .reverse();

    return {
      color: series.color,
      label: series.name,
      path: [
        topPoints.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" "),
        bottomPoints.map((point) => `L ${point.x} ${point.y}`).join(" "),
        "Z",
      ].join(" "),
    };
  });

  return {
    kind: "stacked-area",
    plot,
    ticks,
    areas,
    categories: matrix.items.map((item, index) => ({
      label: item.label,
      x: plot.x + stepX * index,
    })),
    legendEntries: matrix.series.map((series) => ({ color: series.color, label: series.name })),
  };
}

function buildScatterModel(items) {
  const plot = buildPlotArea(false);
  const xValues = items.map((item) => item.x);
  const yValues = items.map((item) => item.y);
  let xMin = Math.min(...xValues);
  let xMax = Math.max(...xValues);
  let yMin = Math.min(...yValues);
  let yMax = Math.max(...yValues);
  if (xMin === xMax) {
    xMin -= 1;
    xMax += 1;
  }
  if (yMin === yMax) {
    yMin -= 1;
    yMax += 1;
  }
  const xPadding = (xMax - xMin) * 0.1;
  const yPadding = (yMax - yMin) * 0.1;
  xMin -= xPadding;
  xMax += xPadding;
  yMin -= yPadding;
  yMax += yPadding;
  const maxSize = Math.max(...items.map((item) => item.size || 12), 12);
  const xTicks = Array.from({ length: 5 }, (_, index) => xMin + ((xMax - xMin) / 4) * index);
  const yTicks = Array.from({ length: 5 }, (_, index) => yMin + ((yMax - yMin) / 4) * index);

  return {
    kind: "scatter",
    plot,
    xTicks,
    yTicks,
    points: items.map((item) => ({
      ...item,
      cx: plot.x + ((item.x - xMin) / (xMax - xMin)) * plot.width,
      cy: plot.y + plot.height - ((item.y - yMin) / (yMax - yMin)) * plot.height,
      r: 6 + ((item.size || 12) / maxSize) * 14,
    })),
  };
}

function buildRadarModel(items) {
  const centerX = 452;
  const centerY = 250;
  const radius = 160;
  const maxValue = niceMax(Math.max(...items.map((item) => item.value), 1));
  const levels = 5;
  const axisCount = items.length;
  const points = items.map((item, index) => {
    const angle = -Math.PI / 2 + (TAU / axisCount) * index;
    const point = polarToCartesian(centerX, centerY, radius * (item.value / maxValue), angle);
    const labelPoint = polarToCartesian(centerX, centerY, radius + 34, angle);
    return {
      ...item,
      angle,
      x: point.x,
      y: point.y,
      labelX: labelPoint.x,
      labelY: labelPoint.y,
      anchor: Math.cos(angle) > 0.2 ? "start" : Math.cos(angle) < -0.2 ? "end" : "middle",
    };
  });

  const gridPolygons = Array.from({ length: levels }, (_, levelIndex) => {
    const r = radius * ((levelIndex + 1) / levels);
    return items
      .map((_, index) => {
        const angle = -Math.PI / 2 + (TAU / axisCount) * index;
        const point = polarToCartesian(centerX, centerY, r, angle);
        return `${point.x},${point.y}`;
      })
      .join(" ");
  });

  return {
    kind: "radar",
    centerX,
    centerY,
    points,
    gridPolygons,
    polygonPoints: points.map((point) => `${point.x},${point.y}`).join(" "),
  };
}

function buildFunnelModel(items) {
  const topX = previewWidth / 2;
  const topY = 132;
  const totalHeight = showLegend.value ? 276 : 336;
  const stageHeight = totalHeight / items.length;
  const maxValue = Math.max(...items.map((item) => item.value));
  const maxWidth = 360;
  return {
    kind: "funnel",
    stages: items.map((item, index) => {
      const nextValue = items[index + 1]?.value || item.value * 0.68;
      const topWidth = maxWidth * (item.value / maxValue);
      const bottomWidth = maxWidth * (nextValue / maxValue);
      const y = topY + stageHeight * index;
      const points = [
        `${topX - topWidth / 2},${y}`,
        `${topX + topWidth / 2},${y}`,
        `${topX + bottomWidth / 2},${y + stageHeight - 6}`,
        `${topX - bottomWidth / 2},${y + stageHeight - 6}`,
      ].join(" ");
      return {
        ...item,
        points,
        centerX: topX,
        centerY: y + stageHeight / 2,
      };
    }),
    legendEntries: items.map((item) => ({ color: item.color, label: item.label, value: item.value })),
  };
}

function buildHeatmapModel(items) {
  const plot = buildPlotArea(false);
  const xLabels = [...new Set(items.map((item) => item.x))];
  const yLabels = [...new Set(items.map((item) => item.y))];
  const maxValue = Math.max(...items.map((item) => item.value), 1);
  const minValue = Math.min(...items.map((item) => item.value), 0);
  const cellWidth = plot.width / xLabels.length;
  const cellHeight = plot.height / yLabels.length;
  const cells = items.map((item) => {
    const xIndex = xLabels.indexOf(item.x);
    const yIndex = yLabels.indexOf(item.y);
    const progress = maxValue === minValue ? 0.5 : (item.value - minValue) / (maxValue - minValue);
    return {
      ...item,
      x: plot.x + xIndex * cellWidth,
      y: plot.y + yIndex * cellHeight,
      width: cellWidth,
      height: cellHeight,
      color: interpolateColor("#e8f7f3", palettes[activePaletteIndex.value].colors[0], progress),
      textColor: progress > 0.58 ? "#ffffff" : "#335766",
    };
  });

  return {
    kind: "heatmap",
    plot,
    xLabels,
    yLabels,
    cells,
    legendEntries: [
      { color: "#e8f7f3", label: "低" },
      { color: palettes[activePaletteIndex.value].colors[0], label: "高" },
    ],
  };
}

function buildTreemapModel(items) {
  const area = { x: 72, y: 118, width: previewWidth - 144, height: 320 };
  const blocks = sliceTreemap(items, area.x, area.y, area.width, area.height).map((block, index) => ({
    ...block,
    color: palettes[activePaletteIndex.value].colors[index % palettes[activePaletteIndex.value].colors.length],
  }));
  return {
    kind: "treemap",
    blocks,
    legendEntries: items.map((item) => ({ color: item.color, label: item.label, value: item.value })),
  };
}

function buildTreeModel(links) {
  const plot = { x: 92, y: 128, width: previewWidth - 184, height: 300 };
  const nodeMap = new Map();

  function ensureNode(id) {
    if (!nodeMap.has(id)) {
      nodeMap.set(id, { id, label: id, children: [], parent: null, incoming: 0, outgoing: 0 });
    }
    return nodeMap.get(id);
  }

  links.forEach((link) => {
    const source = ensureNode(link.source);
    const target = ensureNode(link.target);
    if (!source.children.includes(target.id)) {
      source.children.push(target.id);
    }
    if (!target.parent) {
      target.parent = source.id;
    }
    source.outgoing += link.value;
    target.incoming += link.value;
  });

  const rootIds = [...nodeMap.values()].filter((node) => !node.parent).map((node) => node.id);
  if (!rootIds.length) {
    return { kind: "tree", error: "树形图需要至少一个根节点" };
  }

  let rootId = rootIds[0];
  if (rootIds.length > 1) {
    const syntheticId = "__root__";
    nodeMap.set(syntheticId, {
      id: syntheticId,
      label: "总览",
      children: rootIds,
      parent: null,
      incoming: 0,
      outgoing: rootIds.length,
    });
    rootId = syntheticId;
    rootIds.forEach((id) => {
      const node = nodeMap.get(id);
      if (node) {
        node.parent = syntheticId;
      }
    });
  }

  const depths = new Map();
  const queue = [{ id: rootId, depth: 0 }];
  while (queue.length) {
    const current = queue.shift();
    if (!current || depths.has(current.id)) {
      continue;
    }
    depths.set(current.id, current.depth);
    const node = nodeMap.get(current.id);
    (node?.children || []).forEach((childId) => {
      queue.push({ id: childId, depth: current.depth + 1 });
    });
  }

  const maxDepth = Math.max(...depths.values(), 0);
  const leafIds = [];

  function collectLeaves(id) {
    const node = nodeMap.get(id);
    if (!node) {
      return;
    }
    if (!node.children.length) {
      leafIds.push(id);
      return;
    }
    node.children.forEach((childId) => collectLeaves(childId));
  }

  collectLeaves(rootId);
  const leafStepY = leafIds.length > 1 ? plot.height / (leafIds.length - 1) : 0;
  const positions = new Map();

  leafIds.forEach((id, index) => {
    positions.set(id, { y: plot.y + leafStepY * index });
  });

  function assignY(id) {
    const node = nodeMap.get(id);
    if (!node) {
      return plot.y;
    }
    if (positions.has(id)) {
      return positions.get(id).y;
    }
    const childYs = node.children.map((childId) => assignY(childId));
    const y = childYs.reduce((sum, value) => sum + value, 0) / (childYs.length || 1);
    positions.set(id, { y });
    return y;
  }

  assignY(rootId);
  const depthStepX = maxDepth ? plot.width / maxDepth : 0;
  const nodes = [...nodeMap.values()]
    .filter((node) => depths.has(node.id))
    .map((node, index) => {
      const depth = depths.get(node.id) || 0;
      const x = plot.x + depth * depthStepX;
      const y = positions.get(node.id)?.y ?? plot.y + plot.height / 2;
      const color = palettes[activePaletteIndex.value].colors[index % palettes[activePaletteIndex.value].colors.length];
      return {
        ...node,
        depth,
        x,
        y,
        radius: node.id === rootId ? 18 : 14,
        color,
        labelX: depth === maxDepth ? x - 22 : x + 24,
        labelAnchor: depth === maxDepth ? "end" : "start",
      };
    });
  const nodeLookup = new Map(nodes.map((node) => [node.id, node]));
  const edges = [];

  links.forEach((link, index) => {
    const source = nodeLookup.get(link.source);
    const target = nodeLookup.get(link.target);
    if (!source || !target) {
      return;
    }
    const controlOffset = Math.max(42, (target.x - source.x) * 0.48);
    edges.push({
      id: `${link.source}-${link.target}-${index}`,
      path: `M ${source.x} ${source.y} C ${source.x + controlOffset} ${source.y}, ${target.x - controlOffset} ${target.y}, ${target.x} ${target.y}`,
      value: link.value,
    });
  });

  return {
    kind: "tree",
    nodes,
    edges,
  };
}

function buildSankeyModel(links) {
  const plot = { x: 80, y: 118, width: previewWidth - 160, height: 320 };
  const nodeMap = new Map();

  function ensureNode(id) {
    if (!nodeMap.has(id)) {
      nodeMap.set(id, {
        id,
        label: id,
        incoming: [],
        outgoing: [],
        level: 0,
        value: 0,
      });
    }
    return nodeMap.get(id);
  }

  links.forEach((link) => {
    const source = ensureNode(link.source);
    const target = ensureNode(link.target);
    source.outgoing.push(link);
    target.incoming.push(link);
  });

  const roots = [...nodeMap.values()].filter((node) => !node.incoming.length);
  const queue = roots.length ? roots.map((node) => node.id) : [...nodeMap.keys()];
  const visited = new Set();

  while (queue.length) {
    const nodeId = queue.shift();
    const node = nodeMap.get(nodeId);
    if (!node) {
      continue;
    }
    visited.add(nodeId);
    node.outgoing.forEach((link) => {
      const target = nodeMap.get(link.target);
      if (!target) {
        return;
      }
      target.level = Math.max(target.level, node.level + 1);
      if (!visited.has(target.id)) {
        queue.push(target.id);
      }
    });
  }

  [...nodeMap.values()].forEach((node) => {
    const totalIn = node.incoming.reduce((sum, link) => sum + link.value, 0);
    const totalOut = node.outgoing.reduce((sum, link) => sum + link.value, 0);
    node.value = Math.max(totalIn, totalOut, 1);
  });

  const maxLevel = Math.max(...[...nodeMap.values()].map((node) => node.level), 0);
  const levelGroups = Array.from({ length: maxLevel + 1 }, () => []);
  [...nodeMap.values()].forEach((node) => {
    levelGroups[node.level].push(node);
  });
  levelGroups.forEach((group) => group.sort((left, right) => right.value - left.value));

  const gap = 18;
  const maxColumnValue = Math.max(
    ...levelGroups.map((group) => group.reduce((sum, node) => sum + node.value, 0)),
    1,
  );
  const maxColumnCount = Math.max(...levelGroups.map((group) => group.length), 1);
  const scale = (plot.height - gap * Math.max(maxColumnCount - 1, 0)) / maxColumnValue;
  const stepX = maxLevel ? plot.width / maxLevel : 0;

  levelGroups.forEach((group, level) => {
    const columnHeight = group.reduce((sum, node) => sum + node.value * scale, 0) + gap * Math.max(group.length - 1, 0);
    let cursorY = plot.y + (plot.height - columnHeight) / 2;
    group.forEach((node, index) => {
      node.x = plot.x + level * stepX;
      node.y = cursorY;
      node.width = 20;
      node.height = node.value * scale;
      node.color = palettes[activePaletteIndex.value].colors[index % palettes[activePaletteIndex.value].colors.length];
      node.outCursor = 0;
      node.inCursor = 0;
      node.labelX = level === maxLevel ? node.x - 12 : node.x + node.width + 12;
      node.labelAnchor = level === maxLevel ? "end" : "start";
      cursorY += node.height + gap;
    });
  });

  const flows = links.map((link, index) => {
    const source = nodeMap.get(link.source);
    const target = nodeMap.get(link.target);
    if (!source || !target) {
      return null;
    }
    const width = Math.max(link.value * scale, 6);
    const startX = source.x + source.width;
    const endX = target.x;
    const startY = source.y + source.outCursor + width / 2;
    const endY = target.y + target.inCursor + width / 2;
    source.outCursor += width;
    target.inCursor += width;
    const controlOffset = Math.max(40, (endX - startX) * 0.46);
    return {
      id: `flow-${index}`,
      path: `M ${startX} ${startY} C ${startX + controlOffset} ${startY}, ${endX - controlOffset} ${endY}, ${endX} ${endY}`,
      width,
      color: source.color,
      value: link.value,
    };
  }).filter(Boolean);

  return {
    kind: "sankey",
    flows,
    nodes: [...nodeMap.values()],
  };
}

function buildWordCloudModel(items) {
  const plot = { x: 78, y: 118, width: previewWidth - 156, height: 340 };
  const maxValue = Math.max(...items.map((item) => item.value), 1);
  const minValue = Math.min(...items.map((item) => item.value), 0);
  const placed = [];
  const centerX = plot.x + plot.width / 2;
  const centerY = plot.y + plot.height / 2;
  const words = items
    .slice()
    .sort((left, right) => right.value - left.value)
    .map((item, index) => {
      const progress = maxValue === minValue ? 0.5 : (item.value - minValue) / (maxValue - minValue);
      const fontSize = 18 + progress * 34;
      const rotation = rotateWords.value && index % 5 === 0 ? -24 : rotateWords.value && index % 7 === 0 ? 24 : 0;
      let chosen = null;

      for (let step = 0; step < 420; step += 1) {
        const angle = step * 0.48;
        const radius = step * 1.8;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        const estimatedWidth = fontSize * item.label.length * (rotation ? 0.4 : 0.58);
        const estimatedHeight = fontSize * (rotation ? 1.8 : 0.92);
        const rect = {
          x: x - estimatedWidth / 2,
          y: y - estimatedHeight / 2,
          width: estimatedWidth,
          height: estimatedHeight,
        };
        const fits =
          rect.x >= plot.x &&
          rect.x + rect.width <= plot.x + plot.width &&
          rect.y >= plot.y &&
          rect.y + rect.height <= plot.y + plot.height;
        const overlaps = placed.some(
          (word) =>
            rect.x < word.rect.x + word.rect.width &&
            rect.x + rect.width > word.rect.x &&
            rect.y < word.rect.y + word.rect.height &&
            rect.y + rect.height > word.rect.y,
        );

        if (fits && !overlaps) {
          chosen = {
            ...item,
            x,
            y,
            fontSize,
            rotation,
            color: palettes[activePaletteIndex.value].colors[index % palettes[activePaletteIndex.value].colors.length],
            rect,
          };
          break;
        }
      }

      if (!chosen) {
        chosen = {
          ...item,
          x: plot.x + 36 + (index % 4) * 160,
          y: plot.y + 42 + Math.floor(index / 4) * 58,
          fontSize,
          rotation: 0,
          color: palettes[activePaletteIndex.value].colors[index % palettes[activePaletteIndex.value].colors.length],
          rect: { x: 0, y: 0, width: 0, height: 0 },
        };
      }

      placed.push(chosen);
      return chosen;
    });

  return {
    kind: "word-cloud",
    words,
  };
}

function buildKlineModel(items) {
  const plot = buildPlotArea(false);
  const minValue = Math.min(...items.map((item) => item.low));
  const maxValue = Math.max(...items.map((item) => item.high));
  const topValue = niceMax(maxValue);
  const bottomValue = Math.floor(minValue * 0.98);
  const ticks = Array.from({ length: 5 }, (_, index) => bottomValue + ((topValue - bottomValue) / 4) * index);
  const bandWidth = plot.width / items.length;
  const candleWidth = Math.min(22, bandWidth * 0.44);
  const scaleY = (value) => plot.y + plot.height - ((value - bottomValue) / (topValue - bottomValue || 1)) * plot.height;

  return {
    kind: "kline",
    plot,
    ticks,
    candles: items.map((item, index) => {
      const x = plot.x + bandWidth * index + bandWidth / 2;
      const openY = scaleY(item.open);
      const closeY = scaleY(item.close);
      return {
        ...item,
        x,
        wickTop: scaleY(item.high),
        wickBottom: scaleY(item.low),
        bodyY: Math.min(openY, closeY),
        bodyHeight: Math.max(Math.abs(closeY - openY), 2),
        candleWidth,
        color: item.close >= item.open ? "#e45454" : "#35a672",
      };
    }),
  };
}

function parseDataForDefinition(definition, text, colors) {
  const rows = parseTable(text);
  if (!rows.length) {
    return { error: "请先输入数据内容" };
  }

  switch (definition.kind) {
    case "pie":
    case "donut":
    case "bar":
    case "horizontal-bar":
    case "line":
    case "area":
    case "radar":
    case "funnel":
    case "rose":
    case "treemap":
    case "word-cloud":
      return parseCategoryRows(rows, colors);
    case "tree":
    case "sankey":
      return parseRelationRows(rows);
    case "stacked-bar":
    case "stacked-area":
    case "combo":
      return parseMatrixRows(rows, colors);
    case "scatter":
      return parseScatterRows(rows, colors);
    case "heatmap":
      return parseHeatmapRows(rows);
    case "kline":
      return parseKlineRows(rows);
    default:
      return { error: "当前图表类型暂不可用" };
  }
}

const parsedData = computed(() => parseDataForDefinition(currentDefinition.value, dataText.value, palettes[activePaletteIndex.value].colors));

const chartModel = computed(() => {
  const definition = currentDefinition.value;
  if (parsedData.value.error) {
    return { kind: definition.kind, error: parsedData.value.error };
  }

  switch (definition.kind) {
    case "pie":
    case "donut":
    case "rose":
      return buildPieLikeModel(parsedData.value.items, definition.kind);
    case "bar":
      return buildBarModel(parsedData.value.items);
    case "horizontal-bar":
      return buildHorizontalBarModel(parsedData.value.items);
    case "line":
    case "area":
      return buildLineLikeModel(parsedData.value.items, definition.kind);
    case "stacked-bar":
      return buildStackedBarModel(parsedData.value);
    case "combo":
      return buildComboModel(parsedData.value);
    case "stacked-area":
      return buildStackedAreaModel(parsedData.value);
    case "scatter":
      return buildScatterModel(parsedData.value.items);
    case "radar":
      return buildRadarModel(parsedData.value.items);
    case "funnel":
      return buildFunnelModel(parsedData.value.items);
    case "heatmap":
      return buildHeatmapModel(parsedData.value.items);
    case "treemap":
      return buildTreemapModel(parsedData.value.items);
    case "tree":
      return buildTreeModel(parsedData.value.links);
    case "sankey":
      return buildSankeyModel(parsedData.value.links);
    case "word-cloud":
      return buildWordCloudModel(parsedData.value.items);
    case "kline":
      return buildKlineModel(parsedData.value.items);
    default:
      return { kind: definition.kind, error: "当前图表类型暂不可用" };
  }
});

const stats = computed(() => {
  const definition = currentDefinition.value;
  if (parsedData.value.error) {
    return {
      count: 0,
      summary: "等待有效数据",
      detail: parsedData.value.error,
    };
  }

  if (parsedData.value.links) {
    const nodeCount = new Set(parsedData.value.links.flatMap((link) => [link.source, link.target])).size;
    return {
      count: parsedData.value.links.length,
      summary: `${nodeCount} 个节点`,
      detail: `${parsedData.value.links.length} 条连接`,
    };
  }

  if (parsedData.value.series && parsedData.value.items) {
    return {
      count: parsedData.value.items.length,
      summary: `${parsedData.value.series.length} 个系列`,
      detail: `${parsedData.value.items.length} 个分类`,
    };
  }

  if (parsedData.value.items && ["scatter"].includes(definition.kind)) {
    const maxPoint = parsedData.value.items.reduce((current, next) => {
      if (!current || next.y > current.y) {
        return next;
      }
      return current;
    }, null);
    return {
      count: parsedData.value.items.length,
      summary: maxPoint ? `${maxPoint.label} · ${formatNumber(maxPoint.y)}` : "暂无数据",
      detail: `X 范围 ${formatNumber(Math.min(...parsedData.value.items.map((item) => item.x)))} - ${formatNumber(
        Math.max(...parsedData.value.items.map((item) => item.x)),
      )}`,
    };
  }

  if (parsedData.value.items && definition.kind === "kline") {
    const highest = Math.max(...parsedData.value.items.map((item) => item.high));
    const lowest = Math.min(...parsedData.value.items.map((item) => item.low));
    const last = parsedData.value.items[parsedData.value.items.length - 1];
    return {
      count: parsedData.value.items.length,
      summary: last ? `${last.label} 收于 ${formatNumber(last.close)}` : "暂无数据",
      detail: `区间 ${formatNumber(lowest)} - ${formatNumber(highest)}`,
    };
  }

  if (parsedData.value.items) {
    const largest = parsedData.value.items.reduce((current, next) => {
      if (!current || next.value > current.value) {
        return next;
      }
      return current;
    }, null);
    return {
      count: parsedData.value.items.length,
      summary: largest ? `${largest.label} · ${formatNumber(largest.value)}` : "暂无数据",
      detail: `总计 ${formatNumber(parsedData.value.items.reduce((sum, item) => sum + item.value, 0))}`,
    };
  }

  return {
    count: 0,
    summary: "等待有效数据",
    detail: "请完善数据表格",
  };
});

function resetFromCurrentTool() {
  const definition = currentDefinition.value;
  chartTitle.value = definition.title;
  chartSubtitle.value = definition.subtitle;
  dataText.value = definition.sampleData;
  showLegend.value = definition.defaults.legend;
  showLabels.value = definition.defaults.labels;
  showGrid.value = definition.defaults.grid;
  activePaletteIndex.value = 0;
  donutRatio.value = 58;
  rotateWords.value = true;
}

watch(
  () => props.tool.slug,
  () => {
    resetFromCurrentTool();
  },
  { immediate: true },
);

function applyPalette(index) {
  activePaletteIndex.value = index;
}

function restoreSample() {
  resetFromCurrentTool();
  showToast({
    type: "success",
    title: "示例数据已恢复",
    message: "当前图表已经回到默认示例。",
    duration: 1800,
  });
}

function chartFilename(extension) {
  const fallback = currentDefinition.value.slug;
  const normalized = (chartTitle.value || fallback)
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/gi, "-")
    .replace(/^-+|-+$/g, "");
  return `${normalized || fallback}.${extension}`;
}

function serializeSvg() {
  if (!svgRef.value || chartModel.value.error) {
    return "";
  }
  const serialized = new XMLSerializer().serializeToString(svgRef.value);
  return `<?xml version="1.0" encoding="UTF-8"?>\n${serialized}`;
}

function ensureDownloadable() {
  if (chartModel.value.error) {
    showToast({
      type: "error",
      title: "当前还不能导出",
      message: chartModel.value.error,
      duration: 2200,
    });
    return false;
  }
  return true;
}

function downloadSvg() {
  if (!ensureDownloadable()) {
    return;
  }
  const blob = new Blob([serializeSvg()], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = chartFilename("svg");
  link.click();
  URL.revokeObjectURL(url);
  showToast({
    type: "success",
    title: "SVG 已导出",
    message: "图表矢量版本已经开始下载。",
    duration: 1800,
  });
}

function downloadPng() {
  if (!ensureDownloadable()) {
    return;
  }

  const svgBlob = new Blob([serializeSvg()], { type: "image/svg+xml;charset=utf-8" });
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
      message: "图表位图版本已经开始下载。",
      duration: 1800,
    });
  };

  image.onerror = () => {
    URL.revokeObjectURL(url);
    showToast({
      type: "error",
      title: "PNG 导出失败",
      message: "建议先下载 SVG，或稍后再试一次。",
      duration: 2200,
    });
  };

  image.src = url;
}
</script>

<template>
  <section class="tool-form local-tool-panel chart-studio-tool">
    <div class="local-tool-header chart-studio-header">
      <div class="local-tool-header-bar">
        <div>
          <h3>{{ currentDefinition.name }}</h3>
          <p>{{ tool.description }}</p>
        </div>
        <div class="chart-studio-stats">
          <div class="chart-stat-card">
            <span>图表类型</span>
            <strong>{{ currentDefinition.name }}</strong>
          </div>
          <div class="chart-stat-card">
            <span>有效项数</span>
            <strong>{{ stats.count }}</strong>
          </div>
          <div class="chart-stat-card wide">
            <span>数据摘要</span>
            <strong>{{ stats.summary }}</strong>
            <small>{{ stats.detail }}</small>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-studio-switches">
      <router-link
        v-for="item in quickSwitchLinks"
        :key="item.slug"
        class="chart-switch-chip"
        :class="{ active: item.slug === tool.slug }"
        :to="item.to"
      >
        {{ item.name }}
      </router-link>
    </div>

    <div class="chart-studio-layout">
      <section class="chart-studio-panel controls">
        <div class="chart-panel-section">
          <div class="chart-section-head">
            <h4>基础配置</h4>
            <p>标题、图例、标签和网格都会立即影响右侧预览。</p>
          </div>

          <label class="chart-field">
            <span>图表标题</span>
            <input v-model="chartTitle" type="text" placeholder="请输入图表标题" />
          </label>

          <label class="chart-field">
            <span>副标题</span>
            <input v-model="chartSubtitle" type="text" placeholder="请输入图表说明" />
          </label>

          <div class="chart-toggle-row">
            <label class="chart-toggle">
              <input v-model="showLegend" type="checkbox" />
              <span>显示图例</span>
            </label>
            <label class="chart-toggle">
              <input v-model="showLabels" type="checkbox" />
              <span>显示标签</span>
            </label>
            <label class="chart-toggle">
              <input v-model="showGrid" type="checkbox" />
              <span>显示网格</span>
            </label>
            <label v-if="currentDefinition.kind === 'word-cloud'" class="chart-toggle">
              <input v-model="rotateWords" type="checkbox" />
              <span>词云旋转</span>
            </label>
          </div>

          <label v-if="currentDefinition.kind === 'donut'" class="chart-field">
            <span>环形内径</span>
            <input v-model="donutRatio" type="range" min="36" max="72" />
            <small>{{ donutRatio }}%</small>
          </label>
        </div>

        <div class="chart-panel-section">
          <div class="chart-section-head">
            <h4>颜色方案</h4>
            <p>同一套颜色会自动同步到当前图表的系列或数据项里。</p>
          </div>

          <div class="chart-palette-grid">
            <button
              v-for="(palette, index) in palettes"
              :key="palette.name"
              type="button"
              class="chart-palette-card"
              :class="{ active: activePaletteIndex === index }"
              @click="applyPalette(index)"
            >
              <strong>{{ palette.name }}</strong>
              <span class="chart-palette-swatches">
                <i v-for="color in palette.colors" :key="color" :style="{ background: color }"></i>
              </span>
            </button>
          </div>
        </div>

        <div class="chart-panel-section">
          <div class="chart-section-head">
            <h4>数据配置</h4>
            <p>{{ currentDefinition.dataHint }}。支持英文逗号或制表符分隔。</p>
          </div>

          <label class="chart-field">
            <span>数据表格</span>
            <textarea v-model="dataText" class="chart-data-textarea" :placeholder="currentDefinition.dataHint"></textarea>
          </label>

          <div class="chart-actions">
            <button type="button" class="secondary-button" @click="restoreSample">恢复示例</button>
          </div>
        </div>
      </section>

      <section class="chart-studio-panel preview">
        <div class="chart-preview-head">
          <div>
            <p class="section-kicker">实时预览</p>
            <h4>{{ chartTitle || currentDefinition.name }}</h4>
            <p>{{ chartSubtitle || currentDefinition.subtitle }}</p>
          </div>
          <div class="chart-actions">
            <button type="button" class="secondary-button" @click="downloadSvg">下载 SVG</button>
            <button type="button" @click="downloadPng">下载 PNG</button>
          </div>
        </div>

        <div class="chart-preview-stage">
          <svg
            ref="svgRef"
            class="chart-svg"
            xmlns="http://www.w3.org/2000/svg"
            :viewBox="`0 0 ${previewWidth} ${previewHeight}`"
            :width="previewWidth"
            :height="previewHeight"
          >
            <rect width="100%" height="100%" rx="30" fill="#ffffff" />
            <text x="54" y="58" class="chart-svg-title">{{ chartTitle || currentDefinition.name }}</text>
            <text x="54" y="86" class="chart-svg-subtitle">
              {{ chartSubtitle || currentDefinition.subtitle }}
            </text>

            <g v-if="chartModel.error">
              <rect x="120" y="160" width="660" height="220" rx="28" fill="#f6fafc" stroke="#d9e5ec" stroke-dasharray="8 8" />
              <text x="450" y="252" text-anchor="middle" class="chart-svg-empty-title">等待有效数据</text>
              <text x="450" y="284" text-anchor="middle" class="chart-svg-empty-subtitle">{{ chartModel.error }}</text>
            </g>

            <template v-else>
              <template v-if="['bar', 'line', 'area', 'horizontal-bar', 'scatter', 'combo', 'stacked-bar', 'stacked-area', 'kline'].includes(chartModel.kind)">
                <template v-if="showGrid">
                  <line
                    v-for="tick in chartModel.ticks || chartModel.leftTicks || chartModel.yTicks"
                    :key="`grid-${tick}`"
                    :x1="chartModel.plot.x"
                    :x2="chartModel.plot.x + chartModel.plot.width"
                    :y1="chartModel.kind === 'horizontal-bar' ? 0 : chartModel.plot.y + chartModel.plot.height - ((tick - (chartModel.yTicks ? chartModel.yTicks[0] : 0)) / ((chartModel.ticks ? chartModel.ticks[chartModel.ticks.length - 1] : chartModel.leftTicks ? chartModel.leftTicks[chartModel.leftTicks.length - 1] : chartModel.yTicks[chartModel.yTicks.length - 1]) - (chartModel.yTicks ? chartModel.yTicks[0] : 0) || 1)) * chartModel.plot.height"
                    :y2="chartModel.kind === 'horizontal-bar' ? 0 : chartModel.plot.y + chartModel.plot.height - ((tick - (chartModel.yTicks ? chartModel.yTicks[0] : 0)) / ((chartModel.ticks ? chartModel.ticks[chartModel.ticks.length - 1] : chartModel.leftTicks ? chartModel.leftTicks[chartModel.leftTicks.length - 1] : chartModel.yTicks[chartModel.yTicks.length - 1]) - (chartModel.yTicks ? chartModel.yTicks[0] : 0) || 1)) * chartModel.plot.height"
                    stroke="#edf3f6"
                  />
                </template>

                <template v-if="chartModel.kind !== 'horizontal-bar'">
                  <line
                    :x1="chartModel.plot.x"
                    :y1="chartModel.plot.y + chartModel.plot.height"
                    :x2="chartModel.plot.x + chartModel.plot.width"
                    :y2="chartModel.plot.y + chartModel.plot.height"
                    stroke="#c8d6df"
                  />
                </template>
              </template>

              <template v-if="chartModel.kind === 'pie' || chartModel.kind === 'donut' || chartModel.kind === 'rose'">
                <path
                  v-for="segment in chartModel.segments"
                  :key="segment.label"
                  :d="segment.path"
                  :fill="segment.color"
                  stroke="#ffffff"
                  stroke-width="3"
                />

                <template v-if="showLabels">
                  <g v-for="segment in chartModel.segments" :key="`label-${segment.label}`">
                    <path
                      :d="`M ${segment.lineStart.x} ${segment.lineStart.y} L ${segment.lineBreak.x} ${segment.lineBreak.y} L ${segment.lineEndX} ${segment.lineBreak.y}`"
                      fill="none"
                      stroke="#89a1b1"
                      stroke-width="1.5"
                    />
                    <text :x="segment.labelX" :y="segment.labelY" :text-anchor="segment.textAnchor" class="chart-svg-label">
                      {{ segment.labelText }}
                    </text>
                  </g>
                </template>

                <g v-if="chartModel.kind === 'donut'">
                  <text :x="chartModel.centerX" :y="chartModel.centerY - 6" text-anchor="middle" class="chart-svg-total-label">总计</text>
                  <text :x="chartModel.centerX" :y="chartModel.centerY + 24" text-anchor="middle" class="chart-svg-total-value">
                    {{ formatNumber(chartModel.total) }}
                  </text>
                </g>
              </template>

              <template v-if="chartModel.kind === 'bar'">
                <g v-for="bar in chartModel.bars" :key="bar.label">
                  <rect :x="bar.x" :y="bar.y" :width="bar.width" :height="bar.height" rx="14" :fill="bar.color" />
                  <text :x="bar.labelX" :y="bar.y - 10" text-anchor="middle" class="chart-svg-data-label">
                    {{ showLabels ? formatNumber(bar.value) : "" }}
                  </text>
                  <text :x="bar.labelX" :y="chartModel.plot.y + chartModel.plot.height + 28" text-anchor="middle" class="chart-svg-axis-label">
                    {{ bar.label }}
                  </text>
                </g>
                <text
                  v-for="tick in chartModel.ticks"
                  :key="`bar-tick-${tick}`"
                  :x="chartModel.plot.x - 12"
                  :y="chartModel.plot.y + chartModel.plot.height - (tick / chartModel.ticks[chartModel.ticks.length - 1]) * chartModel.plot.height + 4"
                  text-anchor="end"
                  class="chart-svg-axis-caption"
                >
                  {{ formatNumber(tick) }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'horizontal-bar'">
                <line
                  :x1="chartModel.plot.x"
                  :y1="chartModel.plot.y + chartModel.plot.height"
                  :x2="chartModel.plot.x"
                  :y2="chartModel.plot.y"
                  stroke="#c8d6df"
                />
                <g v-for="bar in chartModel.bars" :key="bar.label">
                  <rect :x="bar.x" :y="bar.y" :width="bar.width" :height="bar.height" rx="14" :fill="bar.color" />
                  <text :x="chartModel.plot.x - 12" :y="bar.labelY" text-anchor="end" class="chart-svg-axis-label">{{ bar.label }}</text>
                  <text :x="bar.x + bar.width + 8" :y="bar.labelY" class="chart-svg-data-label">
                    {{ showLabels ? formatNumber(bar.value) : "" }}
                  </text>
                </g>
                <text
                  v-for="tick in chartModel.ticks"
                  :key="`hbar-tick-${tick}`"
                  :x="chartModel.plot.x + (tick / chartModel.ticks[chartModel.ticks.length - 1]) * chartModel.plot.width"
                  :y="chartModel.plot.y + chartModel.plot.height + 28"
                  text-anchor="middle"
                  class="chart-svg-axis-caption"
                >
                  {{ formatNumber(tick) }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'line' || chartModel.kind === 'area'">
                <path v-if="chartModel.kind === 'area'" :d="chartModel.areaPath" fill="rgba(79,124,255,0.18)" />
                <path :d="chartModel.linePath" fill="none" stroke="#4f7cff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" />
                <g v-for="point in chartModel.points" :key="point.label">
                  <circle :cx="point.x" :cy="point.y" r="5.5" fill="#4f7cff" stroke="#ffffff" stroke-width="2.5" />
                  <text v-if="showLabels" :x="point.x" :y="point.y - 12" text-anchor="middle" class="chart-svg-data-label">
                    {{ formatNumber(point.value) }}
                  </text>
                  <text :x="point.x" :y="chartModel.plot.y + chartModel.plot.height + 28" text-anchor="middle" class="chart-svg-axis-label">
                    {{ point.label }}
                  </text>
                </g>
                <text
                  v-for="tick in chartModel.ticks"
                  :key="`line-tick-${tick}`"
                  :x="chartModel.plot.x - 12"
                  :y="chartModel.plot.y + chartModel.plot.height - (tick / chartModel.ticks[chartModel.ticks.length - 1]) * chartModel.plot.height + 4"
                  text-anchor="end"
                  class="chart-svg-axis-caption"
                >
                  {{ formatNumber(tick) }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'stacked-bar'">
                <rect
                  v-for="(bar, index) in chartModel.bars"
                  :key="`stack-${index}`"
                  :x="bar.x"
                  :y="bar.y"
                  :width="bar.width"
                  :height="bar.height"
                  :fill="bar.color"
                  rx="10"
                />
                <text
                  v-for="category in chartModel.categories"
                  :key="`stack-cat-${category.label}`"
                  :x="category.x"
                  :y="chartModel.plot.y + chartModel.plot.height + 28"
                  text-anchor="middle"
                  class="chart-svg-axis-label"
                >
                  {{ category.label }}
                </text>
                <text
                  v-for="tick in chartModel.ticks"
                  :key="`stack-tick-${tick}`"
                  :x="chartModel.plot.x - 12"
                  :y="chartModel.plot.y + chartModel.plot.height - (tick / chartModel.ticks[chartModel.ticks.length - 1]) * chartModel.plot.height + 4"
                  text-anchor="end"
                  class="chart-svg-axis-caption"
                >
                  {{ formatNumber(tick) }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'combo'">
                <rect
                  v-for="bar in chartModel.bars"
                  :key="`combo-bar-${bar.labelX}`"
                  :x="bar.x"
                  :y="bar.y"
                  :width="bar.width"
                  :height="bar.height"
                  fill="#4f7cff"
                  rx="10"
                />
                <path :d="chartModel.linePath" fill="none" stroke="#63c172" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" />
                <circle v-for="point in chartModel.linePoints" :key="`combo-point-${point.label}`" :cx="point.x" :cy="point.y" r="5" fill="#63c172" stroke="#ffffff" stroke-width="2.4" />
                <text
                  v-for="bar in chartModel.bars"
                  :key="`combo-x-${bar.labelX}`"
                  :x="bar.labelX"
                  :y="chartModel.plot.y + chartModel.plot.height + 28"
                  text-anchor="middle"
                  class="chart-svg-axis-label"
                >
                  {{ chartModel.linePoints[chartModel.bars.indexOf(bar)].label }}
                </text>
                <text
                  v-for="tick in chartModel.leftTicks"
                  :key="`combo-left-${tick}`"
                  :x="chartModel.plot.x - 12"
                  :y="chartModel.plot.y + chartModel.plot.height - (tick / chartModel.leftTicks[chartModel.leftTicks.length - 1]) * chartModel.plot.height + 4"
                  text-anchor="end"
                  class="chart-svg-axis-caption"
                >
                  {{ formatNumber(tick) }}
                </text>
                <text
                  v-for="tick in chartModel.rightTicks"
                  :key="`combo-right-${tick}`"
                  :x="chartModel.plot.x + chartModel.plot.width + 12"
                  :y="chartModel.plot.y + chartModel.plot.height - (tick / chartModel.rightTicks[chartModel.rightTicks.length - 1]) * chartModel.plot.height + 4"
                  class="chart-svg-axis-caption"
                >
                  {{ formatNumber(tick) }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'stacked-area'">
                <path
                  v-for="(area, index) in chartModel.areas"
                  :key="`area-${index}`"
                  :d="area.path"
                  :fill="area.color"
                  fill-opacity="0.72"
                  stroke="#ffffff"
                  stroke-width="1.8"
                />
                <text
                  v-for="category in chartModel.categories"
                  :key="`area-cat-${category.label}`"
                  :x="category.x"
                  :y="chartModel.plot.y + chartModel.plot.height + 28"
                  text-anchor="middle"
                  class="chart-svg-axis-label"
                >
                  {{ category.label }}
                </text>
                <text
                  v-for="tick in chartModel.ticks"
                  :key="`area-tick-${tick}`"
                  :x="chartModel.plot.x - 12"
                  :y="chartModel.plot.y + chartModel.plot.height - (tick / chartModel.ticks[chartModel.ticks.length - 1]) * chartModel.plot.height + 4"
                  text-anchor="end"
                  class="chart-svg-axis-caption"
                >
                  {{ formatNumber(tick) }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'scatter'">
                <line :x1="chartModel.plot.x" :y1="chartModel.plot.y + chartModel.plot.height" :x2="chartModel.plot.x + chartModel.plot.width" :y2="chartModel.plot.y + chartModel.plot.height" stroke="#c8d6df" />
                <line :x1="chartModel.plot.x" :y1="chartModel.plot.y" :x2="chartModel.plot.x" :y2="chartModel.plot.y + chartModel.plot.height" stroke="#c8d6df" />
                <circle
                  v-for="point in chartModel.points"
                  :key="point.label"
                  :cx="point.cx"
                  :cy="point.cy"
                  :r="point.r"
                  :fill="point.color"
                  fill-opacity="0.68"
                  stroke="#ffffff"
                  stroke-width="2"
                />
                <text v-for="point in chartModel.points" v-if="showLabels" :key="`scatter-label-${point.label}`" :x="point.cx" :y="point.cy - point.r - 8" text-anchor="middle" class="chart-svg-label">
                  {{ point.label }}
                </text>
                <text
                  v-for="tick in chartModel.xTicks"
                  :key="`scatter-x-${tick}`"
                  :x="chartModel.plot.x + ((tick - chartModel.xTicks[0]) / (chartModel.xTicks[chartModel.xTicks.length - 1] - chartModel.xTicks[0])) * chartModel.plot.width"
                  :y="chartModel.plot.y + chartModel.plot.height + 28"
                  text-anchor="middle"
                  class="chart-svg-axis-caption"
                >
                  {{ formatNumber(tick) }}
                </text>
                <text
                  v-for="tick in chartModel.yTicks"
                  :key="`scatter-y-${tick}`"
                  :x="chartModel.plot.x - 12"
                  :y="chartModel.plot.y + chartModel.plot.height - ((tick - chartModel.yTicks[0]) / (chartModel.yTicks[chartModel.yTicks.length - 1] - chartModel.yTicks[0])) * chartModel.plot.height + 4"
                  text-anchor="end"
                  class="chart-svg-axis-caption"
                >
                  {{ formatNumber(tick) }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'radar'">
                <polygon v-for="(polygon, index) in chartModel.gridPolygons" :key="`radar-grid-${index}`" :points="polygon" fill="none" stroke="#e3edf2" />
                <line
                  v-for="point in chartModel.points"
                  :key="`radar-axis-${point.label}`"
                  :x1="chartModel.centerX"
                  :y1="chartModel.centerY"
                  :x2="point.labelX"
                  :y2="point.labelY - 10"
                  stroke="#d3e2ea"
                />
                <polygon :points="chartModel.polygonPoints" fill="rgba(79,124,255,0.24)" stroke="#4f7cff" stroke-width="3" />
                <circle v-for="point in chartModel.points" :key="`radar-point-${point.label}`" :cx="point.x" :cy="point.y" r="5" fill="#4f7cff" />
                <text v-for="point in chartModel.points" :key="`radar-label-${point.label}`" :x="point.labelX" :y="point.labelY" :text-anchor="point.anchor" class="chart-svg-label">
                  {{ point.label }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'funnel'">
                <polygon v-for="stage in chartModel.stages" :key="stage.label" :points="stage.points" :fill="stage.color" />
                <text v-for="stage in chartModel.stages" :key="`funnel-${stage.label}`" :x="stage.centerX" :y="stage.centerY + 5" text-anchor="middle" class="chart-svg-funnel-label">
                  {{ showLabels ? `${stage.label} · ${formatNumber(stage.value)}` : stage.label }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'heatmap'">
                <rect v-for="cell in chartModel.cells" :key="`${cell.x}-${cell.y}`" :x="cell.x" :y="cell.y" :width="cell.width" :height="cell.height" :fill="cell.color" rx="10" />
                <text
                  v-for="cell in chartModel.cells"
                  v-if="showLabels"
                  :key="`heat-text-${cell.x}-${cell.y}`"
                  :x="cell.x + cell.width / 2"
                  :y="cell.y + cell.height / 2 + 5"
                  text-anchor="middle"
                  :fill="cell.textColor"
                  class="chart-svg-heat-value"
                >
                  {{ formatNumber(cell.value) }}
                </text>
                <text
                  v-for="(label, index) in chartModel.xLabels"
                  :key="`heat-x-${label}`"
                  :x="chartModel.plot.x + index * (chartModel.plot.width / chartModel.xLabels.length) + chartModel.plot.width / chartModel.xLabels.length / 2"
                  :y="chartModel.plot.y - 16"
                  text-anchor="middle"
                  class="chart-svg-axis-label"
                >
                  {{ label }}
                </text>
                <text
                  v-for="(label, index) in chartModel.yLabels"
                  :key="`heat-y-${label}`"
                  :x="chartModel.plot.x - 14"
                  :y="chartModel.plot.y + index * (chartModel.plot.height / chartModel.yLabels.length) + chartModel.plot.height / chartModel.yLabels.length / 2 + 4"
                  text-anchor="end"
                  class="chart-svg-axis-label"
                >
                  {{ label }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'treemap'">
                <g v-for="block in chartModel.blocks" :key="block.label">
                  <rect :x="block.x" :y="block.y" :width="block.width" :height="block.height" :fill="block.color" rx="14" />
                  <text :x="block.x + 14" :y="block.y + 24" class="chart-svg-treemap-label">{{ block.label }}</text>
                  <text :x="block.x + 14" :y="block.y + 46" class="chart-svg-treemap-value">{{ formatNumber(block.value) }}</text>
                </g>
              </template>

              <template v-if="chartModel.kind === 'tree'">
                <path
                  v-for="edge in chartModel.edges"
                  :key="edge.id"
                  :d="edge.path"
                  fill="none"
                  stroke="#cfe0e8"
                  stroke-width="2.4"
                />
                <g v-for="node in chartModel.nodes" :key="node.id">
                  <circle :cx="node.x" :cy="node.y" :r="node.radius" :fill="node.color" stroke="#ffffff" stroke-width="3" />
                  <text
                    :x="node.labelX"
                    :y="node.y + 5"
                    :text-anchor="node.labelAnchor"
                    class="chart-svg-label"
                  >
                    {{ showLabels ? node.label : "" }}
                  </text>
                </g>
              </template>

              <template v-if="chartModel.kind === 'sankey'">
                <path
                  v-for="flow in chartModel.flows"
                  :key="flow.id"
                  :d="flow.path"
                  fill="none"
                  :stroke="flow.color"
                  :stroke-width="flow.width"
                  stroke-linecap="round"
                  stroke-opacity="0.28"
                />
                <g v-for="node in chartModel.nodes" :key="node.id">
                  <rect :x="node.x" :y="node.y" :width="node.width" :height="node.height" :fill="node.color" rx="8" />
                  <text
                    :x="node.labelX"
                    :y="node.y + node.height / 2 + 5"
                    :text-anchor="node.labelAnchor"
                    class="chart-svg-label"
                  >
                    {{ showLabels ? node.label : "" }}
                  </text>
                </g>
              </template>

              <template v-if="chartModel.kind === 'word-cloud'">
                <text
                  v-for="word in chartModel.words"
                  :key="word.label"
                  :x="word.x"
                  :y="word.y"
                  :transform="`rotate(${word.rotation} ${word.x} ${word.y})`"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  :fill="word.color"
                  :style="{ fontSize: `${word.fontSize}px`, fontWeight: 700 }"
                >
                  {{ word.label }}
                </text>
              </template>

              <template v-if="chartModel.kind === 'kline'">
                <line :x1="chartModel.plot.x" :y1="chartModel.plot.y + chartModel.plot.height" :x2="chartModel.plot.x + chartModel.plot.width" :y2="chartModel.plot.y + chartModel.plot.height" stroke="#c8d6df" />
                <g v-for="candle in chartModel.candles" :key="candle.label">
                  <line :x1="candle.x" :y1="candle.wickTop" :x2="candle.x" :y2="candle.wickBottom" :stroke="candle.color" stroke-width="2.2" />
                  <rect :x="candle.x - candle.candleWidth / 2" :y="candle.bodyY" :width="candle.candleWidth" :height="candle.bodyHeight" :fill="candle.color" rx="6" />
                  <text :x="candle.x" :y="chartModel.plot.y + chartModel.plot.height + 28" text-anchor="middle" class="chart-svg-axis-label">{{ candle.label }}</text>
                </g>
                <text
                  v-for="tick in chartModel.ticks"
                  :key="`kline-tick-${tick}`"
                  :x="chartModel.plot.x - 12"
                  :y="chartModel.plot.y + chartModel.plot.height - ((tick - chartModel.ticks[0]) / (chartModel.ticks[chartModel.ticks.length - 1] - chartModel.ticks[0] || 1)) * chartModel.plot.height + 4"
                  text-anchor="end"
                  class="chart-svg-axis-caption"
                >
                  {{ formatNumber(tick) }}
                </text>
              </template>

              <template v-if="showLegend && chartModel.legendEntries?.length">
                <g v-for="(entry, index) in chartModel.legendEntries" :key="`legend-${entry.label}-${index}`">
                  <rect
                    :x="84 + (index % 4) * 190"
                    :y="previewHeight - 72 + Math.floor(index / 4) * 26"
                    width="14"
                    height="14"
                    rx="4"
                    :fill="entry.color"
                  />
                  <text
                    :x="106 + (index % 4) * 190"
                    :y="previewHeight - 60 + Math.floor(index / 4) * 26"
                    class="chart-svg-legend"
                  >
                    {{ entry.value !== undefined ? `${entry.label} · ${formatNumber(entry.value)}` : entry.label }}
                  </text>
                </g>
              </template>
            </template>
          </svg>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.chart-studio-tool {
  display: grid;
  gap: 20px;
}

.chart-studio-header {
  margin-bottom: 0;
}

.chart-studio-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-stat-card {
  min-width: 126px;
  padding: 12px 14px;
  border-radius: 18px;
  border: 1px solid rgba(31, 157, 139, 0.18);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(240, 250, 248, 0.82));
}

.chart-stat-card.wide {
  min-width: 208px;
}

.chart-stat-card span,
.chart-stat-card small {
  display: block;
  color: var(--muted);
  font-size: 13px;
}

.chart-stat-card strong {
  display: block;
  margin-top: 6px;
  color: #175f56;
  font-size: 20px;
}

.chart-studio-switches {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chart-switch-chip {
  display: inline-flex;
  align-items: center;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(197, 216, 235, 0.82);
  background: rgba(255, 255, 255, 0.82);
  color: var(--ink);
  text-decoration: none;
}

.chart-switch-chip.active {
  border-color: rgba(31, 157, 139, 0.38);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(231, 248, 244, 0.9));
  color: #167767;
  box-shadow: 0 0 0 4px rgba(31, 157, 139, 0.08);
}

.chart-studio-layout {
  display: grid;
  grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.chart-studio-panel {
  border-radius: 24px;
  border: 1px solid rgba(197, 216, 235, 0.78);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(246, 251, 255, 0.8));
  box-shadow: 0 22px 44px rgba(99, 135, 173, 0.08);
}

.chart-studio-panel.controls,
.chart-studio-panel.preview {
  padding: 18px;
  display: grid;
  gap: 18px;
}

.chart-panel-section {
  display: grid;
  gap: 14px;
}

.chart-section-head h4,
.chart-preview-head h4 {
  margin: 0 0 6px;
  font-size: 18px;
}

.chart-section-head p,
.chart-preview-head p {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}

.chart-field {
  display: grid;
  gap: 8px;
}

.chart-field span {
  color: var(--ink);
  font-weight: 600;
}

.chart-field small {
  color: var(--muted);
}

.chart-data-textarea {
  min-height: 220px;
  font-family: "SFMono-Regular", "Roboto Mono", "Consolas", monospace;
  line-height: 1.6;
}

.chart-toggle-row,
.chart-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chart-toggle {
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

.chart-palette-grid {
  display: grid;
  gap: 10px;
}

.chart-palette-card {
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(197, 216, 235, 0.78);
  background: rgba(255, 255, 255, 0.82);
  text-align: left;
}

.chart-palette-card.active {
  border-color: rgba(31, 157, 139, 0.38);
  box-shadow: 0 0 0 4px rgba(31, 157, 139, 0.08);
}

.chart-palette-swatches {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chart-palette-swatches i {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: inline-block;
}

.chart-preview-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.chart-preview-stage {
  overflow: auto;
  border-radius: 24px;
  border: 1px solid rgba(216, 229, 236, 0.9);
  background: #ffffff;
}

.chart-svg {
  display: block;
  width: 100%;
  min-width: 760px;
  height: auto;
}

.chart-svg-title {
  fill: #243647;
  font-size: 30px;
  font-weight: 700;
}

.chart-svg-subtitle,
.chart-svg-label,
.chart-svg-axis-label,
.chart-svg-axis-caption,
.chart-svg-legend,
.chart-svg-data-label,
.chart-svg-empty-subtitle,
.chart-svg-heat-value,
.chart-svg-total-label,
.chart-svg-funnel-label {
  fill: #6d7a86;
  font-size: 14px;
}

.chart-svg-axis-caption {
  font-size: 13px;
}

.chart-svg-data-label,
.chart-svg-label {
  font-size: 13px;
}

.chart-svg-total-label,
.chart-svg-empty-title,
.chart-svg-treemap-label {
  fill: #39505f;
  font-size: 16px;
  font-weight: 600;
}

.chart-svg-total-value {
  fill: #1d3b49;
  font-size: 30px;
  font-weight: 700;
}

.chart-svg-treemap-value {
  fill: rgba(255, 255, 255, 0.94);
  font-size: 18px;
  font-weight: 700;
}

@media (max-width: 1080px) {
  .chart-studio-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .chart-studio-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }

  .chart-stat-card,
  .chart-stat-card.wide {
    min-width: 0;
  }

  .chart-svg {
    min-width: 700px;
  }
}
</style>
