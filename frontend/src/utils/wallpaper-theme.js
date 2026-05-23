const beijingFormatter = new Intl.DateTimeFormat("en-CA", {
  timeZone: "Asia/Shanghai",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

export const SOLAR_TERM_BOUNDARIES = {
  2024: { spring: "2024-03-20", summer: "2024-06-21", autumn: "2024-09-22", winter: "2024-12-21" },
  2025: { spring: "2025-03-20", summer: "2025-06-21", autumn: "2025-09-23", winter: "2025-12-21" },
  2026: { spring: "2026-03-20", summer: "2026-06-21", autumn: "2026-09-23", winter: "2026-12-22" },
  2027: { spring: "2027-03-21", summer: "2027-06-21", autumn: "2027-09-23", winter: "2027-12-22" },
  2028: { spring: "2028-03-20", summer: "2028-06-21", autumn: "2028-09-22", winter: "2028-12-21" },
  2029: { spring: "2029-03-20", summer: "2029-06-21", autumn: "2029-09-23", winter: "2029-12-21" },
  2030: { spring: "2030-03-20", summer: "2030-06-21", autumn: "2030-09-23", winter: "2030-12-22" },
  2031: { spring: "2031-03-21", summer: "2031-06-21", autumn: "2031-09-23", winter: "2031-12-22" },
  2032: { spring: "2032-03-20", summer: "2032-06-21", autumn: "2032-09-22", winter: "2032-12-21" },
  2033: { spring: "2033-03-20", summer: "2033-06-21", autumn: "2033-09-23", winter: "2033-12-21" },
  2034: { spring: "2034-03-20", summer: "2034-06-21", autumn: "2034-09-23", winter: "2034-12-22" },
  2035: { spring: "2035-03-21", summer: "2035-06-21", autumn: "2035-09-23", winter: "2035-12-22" },
  2036: { spring: "2036-03-20", summer: "2036-06-21", autumn: "2036-09-22", winter: "2036-12-21" },
  2037: { spring: "2037-03-20", summer: "2037-06-21", autumn: "2037-09-23", winter: "2037-12-21" },
  2038: { spring: "2038-03-20", summer: "2038-06-21", autumn: "2038-09-23", winter: "2038-12-22" },
  2039: { spring: "2039-03-21", summer: "2039-06-21", autumn: "2039-09-23", winter: "2039-12-22" },
  2040: { spring: "2040-03-20", summer: "2040-06-21", autumn: "2040-09-22", winter: "2040-12-21" },
  2041: { spring: "2041-03-20", summer: "2041-06-21", autumn: "2041-09-22", winter: "2041-12-21" },
  2042: { spring: "2042-03-20", summer: "2042-06-21", autumn: "2042-09-23", winter: "2042-12-22" },
  2043: { spring: "2043-03-21", summer: "2043-06-21", autumn: "2043-09-23", winter: "2043-12-22" },
  2044: { spring: "2044-03-20", summer: "2044-06-21", autumn: "2044-09-22", winter: "2044-12-21" },
  2045: { spring: "2045-03-20", summer: "2045-06-21", autumn: "2045-09-22", winter: "2045-12-21" },
  2046: { spring: "2046-03-20", summer: "2046-06-21", autumn: "2046-09-23", winter: "2046-12-22" },
  2047: { spring: "2047-03-21", summer: "2047-06-21", autumn: "2047-09-23", winter: "2047-12-22" },
  2048: { spring: "2048-03-20", summer: "2048-06-20", autumn: "2048-09-22", winter: "2048-12-21" },
  2049: { spring: "2049-03-20", summer: "2049-06-21", autumn: "2049-09-22", winter: "2049-12-21" },
  2050: { spring: "2050-03-20", summer: "2050-06-21", autumn: "2050-09-23", winter: "2050-12-22" },
};

function buildFallbackBoundary(year) {
  return {
    spring: `${year}-03-20`,
    summer: `${year}-06-21`,
    autumn: `${year}-09-23`,
    winter: `${year}-12-21`,
  };
}

export function getBeijingDateInfo(date = new Date()) {
  const parts = Object.fromEntries(
    beijingFormatter.formatToParts(date).map((part) => [part.type, part.value]),
  );

  const year = Number(parts.year);
  const month = Number(parts.month);
  const day = Number(parts.day);
  const hour = Number(parts.hour);
  const minute = Number(parts.minute);
  const second = Number(parts.second);

  return {
    year,
    month,
    day,
    hour,
    minute,
    second,
    dateKey: `${parts.year}-${parts.month}-${parts.day}`,
  };
}

export function getSeasonalWallpaperKey(date = new Date()) {
  const info = getBeijingDateInfo(date);
  const boundaries = SOLAR_TERM_BOUNDARIES[info.year] || buildFallbackBoundary(info.year);

  if (info.dateKey >= boundaries.winter || info.dateKey < boundaries.spring) {
    return "winter";
  }
  if (info.dateKey >= boundaries.autumn) {
    return "autumn";
  }
  if (info.dateKey >= boundaries.summer) {
    return "summer";
  }
  return "spring";
}

export function getMsUntilNextBeijingMidnight(date = new Date()) {
  const info = getBeijingDateInfo(date);
  const nowUtc = Date.UTC(info.year, info.month - 1, info.day, info.hour - 8, info.minute, info.second);
  const nextMidnightUtc = Date.UTC(info.year, info.month - 1, info.day + 1, -8, 0, 1);
  return Math.max(1000, nextMidnightUtc - nowUtc);
}
