import rawCategories from "../../../backend/app/configs/categories.json";
import rawTools from "../../../backend/app/configs/tools.json";

function sortByOrder(items) {
  return [...items].sort((left, right) => (right.sort_order || 0) - (left.sort_order || 0));
}

export const fallbackCategories = sortByOrder(rawCategories).filter((item) => item.enabled !== false);
export const fallbackTools = rawTools.filter((item) => item.enabled !== false && item.visible !== false);

export function getFallbackTool(slug) {
  return rawTools.find((tool) => tool.enabled !== false && tool.slug === slug) || null;
}
