// 文件说明：提供 formatter 前端工具函数。
export function prettyJson(input) {
  return JSON.stringify(JSON.parse(input), null, 2);
}
