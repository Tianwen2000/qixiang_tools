export function prettyJson(input) {
  return JSON.stringify(JSON.parse(input), null, 2);
}
