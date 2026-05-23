import { get, post, postForm } from "./client.js";
import { fallbackCategories, fallbackTools, getFallbackTool } from "../data/fallback-meta.js";

export async function listCategories() {
  try {
    return await get("/categories");
  } catch {
    return fallbackCategories;
  }
}

export async function listTools(params = {}) {
  try {
    return await get("/tools", params);
  } catch {
    if (!params || !Object.keys(params).length) {
      return fallbackTools;
    }

    return fallbackTools.filter((tool) => {
      return Object.entries(params).every(([key, value]) => {
        if (value === undefined || value === null || value === "") {
          return true;
        }
        return String(tool[key]) === String(value);
      });
    });
  }
}

export async function getTool(slug) {
  try {
    return await get(`/tools/${slug}`);
  } catch {
    const fallbackTool = getFallbackTool(slug);
    if (!fallbackTool) {
      throw new Error("工具不存在");
    }
    return fallbackTool;
  }
}

export function getBeijingTime() {
  return get("/time/beijing");
}

export function executeTextTool(slug, payload) {
  return post(`/tools/${slug}/execute`, payload);
}

export function uploadFileTool(slug, file, params = {}) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("params", JSON.stringify(params));
  return postForm(`/tools/${slug}/upload`, formData);
}
