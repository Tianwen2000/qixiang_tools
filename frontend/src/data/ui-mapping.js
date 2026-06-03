export const toolComponentMapping = {
  text: "ToolTextForm",
  file: "ToolFileForm",
  mixed: "ToolTextForm",
  form: "ToolTextForm",
  local: "ToolDinoRunner",
};

const categoryThemeMap = {
  dev: {
    label: "开发",
    accent: "#2db36a",
    soft: "rgba(45, 179, 106, 0.16)",
  },
  ops: {
    label: "测试运维",
    accent: "#327a8f",
    soft: "rgba(50, 122, 143, 0.16)",
  },
  format: {
    label: "格式转换",
    accent: "#f46b45",
    soft: "rgba(244, 107, 69, 0.14)",
  },
  text: {
    label: "文本",
    accent: "#08b6c7",
    soft: "rgba(8, 182, 199, 0.16)",
  },
  encode: {
    label: "编码",
    accent: "#287bff",
    soft: "rgba(40, 123, 255, 0.16)",
  },
  image: {
    label: "图片",
    accent: "#ff9d2d",
    soft: "rgba(255, 157, 45, 0.16)",
  },
  chart: {
    label: "图表",
    accent: "#1f9d8b",
    soft: "rgba(31, 157, 139, 0.16)",
  },
  time: {
    label: "时间",
    accent: "#2aa6c5",
    soft: "rgba(42, 166, 197, 0.16)",
  },
  other: {
    label: "其他",
    accent: "#6077c8",
    soft: "rgba(96, 119, 200, 0.16)",
  },
  game: {
    label: "益智游戏",
    accent: "#d97706",
    soft: "rgba(217, 119, 6, 0.16)",
  },
  default: {
    label: "工具",
    accent: "#6d7a86",
    soft: "rgba(109, 122, 134, 0.16)",
  },
};

export function resolveToolComponent(tool) {
  if (!tool) {
    return "ToolTextForm";
  }
  return tool.component || toolComponentMapping[tool.input_mode] || "ToolTextForm";
}

export function getToolModeLabel(tool) {
  if (tool?.input_mode === "local" && tool?.category === "game") {
    return "本地游戏";
  }
  if (tool?.input_mode === "local" && tool?.category === "chart") {
    return "本地图表";
  }
  if (tool?.input_mode === "local" && tool?.category === "time") {
    return "时间工具";
  }
  if (tool?.input_mode === "local" && tool?.category === "other") {
    if (tool?.component === "ToolAbstractAppliance") {
      return "本地趣味";
    }
    return "本地测试";
  }
  if (tool?.input_mode === "local" && tool?.category === "ops") {
    return "命令速查";
  }
  if (tool?.input_mode === "form" && tool?.category === "ops") {
    return "网络检测";
  }
  const modeMap = {
    text: "文本输入",
    file: "文件上传",
    mixed: "混合输入",
    form: "表单输入",
    local: "本地工具",
  };
  return modeMap[tool?.input_mode] || "通用工具";
}

export function getCategoryTheme(slug) {
  return categoryThemeMap[slug] || categoryThemeMap.default;
}
