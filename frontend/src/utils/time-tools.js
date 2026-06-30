// 文件说明：提供 time tools 前端工具函数。
export const worldClockZones = [
  { city: "北京", note: "中国标准时间", zone: "Asia/Shanghai" },
  { city: "东京", note: "亚洲协作", zone: "Asia/Tokyo" },
  { city: "新加坡", note: "东南亚", zone: "Asia/Singapore" },
  { city: "迪拜", note: "中东", zone: "Asia/Dubai" },
  { city: "伦敦", note: "欧洲", zone: "Europe/London" },
  { city: "巴黎", note: "欧洲中部", zone: "Europe/Paris" },
  { city: "纽约", note: "美东", zone: "America/New_York" },
  { city: "洛杉矶", note: "美西", zone: "America/Los_Angeles" },
];

const lunarDayLabels = [
  "",
  "初一",
  "初二",
  "初三",
  "初四",
  "初五",
  "初六",
  "初七",
  "初八",
  "初九",
  "初十",
  "十一",
  "十二",
  "十三",
  "十四",
  "十五",
  "十六",
  "十七",
  "十八",
  "十九",
  "二十",
  "廿一",
  "廿二",
  "廿三",
  "廿四",
  "廿五",
  "廿六",
  "廿七",
  "廿八",
  "廿九",
  "三十",
  "三一",
];

const lunarMonthLabels = ["", "正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"];
const lunarCalendarData = [
  0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,
  0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
  0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
  0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
  0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
  0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,
  0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
  0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,
  0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
  0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x055c0, 0x0ab60, 0x096d5, 0x092e0,
  0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
  0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
  0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
  0x05aa0, 0x076a3, 0x096d0, 0x04bd7, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
  0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,
  0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06b20, 0x1a6c4, 0x0aae0,
  0x0a2e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4,
  0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,
  0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160,
  0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a2d0, 0x0d150, 0x0f252,
  0x0d520,
];
const lunarMinYear = 1900;
const lunarMaxYear = lunarMinYear + lunarCalendarData.length - 1;
const lunarBaseUtc = Date.UTC(1900, 0, 31);
const heavenlyStems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
const earthlyBranches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];

const zodiacAnimals = {
  子: "鼠",
  丑: "牛",
  寅: "虎",
  卯: "兔",
  辰: "龙",
  巳: "蛇",
  午: "马",
  未: "羊",
  申: "猴",
  酉: "鸡",
  戌: "狗",
  亥: "猪",
};

export const dateFormatter = new Intl.DateTimeFormat("zh-CN", {
  year: "numeric",
  month: "long",
  day: "numeric",
  weekday: "long",
});

export const beijingDateFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "Asia/Shanghai",
  year: "numeric",
  month: "long",
  day: "numeric",
  weekday: "long",
});

export const beijingTimeFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "Asia/Shanghai",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

export const beijingDateTimeFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "Asia/Shanghai",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

export const utcDateTimeFormatter = new Intl.DateTimeFormat("zh-CN", {
  timeZone: "UTC",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
});

const lunarFormatter = (() => {
  try {
    return new Intl.DateTimeFormat("zh-CN-u-ca-chinese", {
      timeZone: "Asia/Shanghai",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch {
    return null;
  }
})();

export function pad(value) {
  return String(value).padStart(2, "0");
}

export function toDateInputValue(date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

export function toDateTimeInputValue(date) {
  return `${toDateInputValue(date)}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function parseDateInputValue(value) {
  if (!value) {
    return null;
  }
  const [year, month, day] = value.split("-").map(Number);
  if (!year || !month || !day) {
    return null;
  }
  return new Date(year, month - 1, day);
}

function parseDateTimeParts(value) {
  if (!value || !value.includes("T")) {
    return null;
  }
  const [datePart, timePart] = value.split("T");
  const [year, month, day] = datePart.split("-").map(Number);
  const [hour = 0, minute = 0] = timePart.split(":").map(Number);
  if (!year || !month || !day) {
    return null;
  }
  return { year, month, day, hour, minute };
}

export function parseDateTimeValue(value, source = "local") {
  const parts = parseDateTimeParts(value);
  if (!parts) {
    return Number.NaN;
  }
  if (source === "utc") {
    return Date.UTC(parts.year, parts.month - 1, parts.day, parts.hour, parts.minute, 0);
  }
  if (source === "beijing") {
    return Date.UTC(parts.year, parts.month - 1, parts.day, parts.hour - 8, parts.minute, 0);
  }
  return new Date(parts.year, parts.month - 1, parts.day, parts.hour, parts.minute, 0).getTime();
}

export function addDays(date, amount) {
  const next = new Date(date);
  next.setDate(next.getDate() + amount);
  return next;
}

export function addYears(date, amount) {
  const next = new Date(date);
  next.setFullYear(next.getFullYear() + amount);
  return next;
}

function getLunarData(year) {
  if (year < lunarMinYear || year > lunarMaxYear) {
    return 0;
  }
  return lunarCalendarData[year - lunarMinYear] || 0;
}

function getLunarYearDays(year) {
  const data = getLunarData(year);
  if (!data) {
    return 0;
  }
  let total = 348;
  for (let mask = 0x8000; mask > 0x8; mask >>= 1) {
    total += data & mask ? 1 : 0;
  }
  return total + getLunarLeapDays(year);
}

function getNormalLunarMonthDays(year, month) {
  const data = getLunarData(year);
  if (!data || month < 1 || month > 12) {
    return 0;
  }
  return data & (0x10000 >> month) ? 30 : 29;
}

function daysFromBaseDate(date) {
  return Math.floor((Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()) - lunarBaseUtc) / 86400000);
}

function dateFromBaseOffset(offset) {
  const utc = new Date(lunarBaseUtc + offset * 86400000);
  return new Date(utc.getUTCFullYear(), utc.getUTCMonth(), utc.getUTCDate());
}

export function getSupportedLunarYearRange() {
  return { min: lunarMinYear, max: lunarMaxYear };
}

export function getLunarLeapMonth(year) {
  return getLunarData(year) & 0xf;
}

export function getLunarLeapDays(year) {
  const leapMonth = getLunarLeapMonth(year);
  if (!leapMonth) {
    return 0;
  }
  return getLunarData(year) & 0x10000 ? 30 : 29;
}

export function getLunarMonthLabel(month, isLeap = false) {
  const monthText = lunarMonthLabels[month] || String(month);
  return `${isLeap ? "闰" : ""}${monthText}月`;
}

export function getLunarDayLabel(day) {
  return lunarDayLabels[day] || String(day);
}

export function getLunarMonthDays(year, month, isLeap = false) {
  if (isLeap) {
    return getLunarLeapMonth(year) === month ? getLunarLeapDays(year) : 0;
  }
  return getNormalLunarMonthDays(year, month);
}

export function getLunarMonthOptions(year) {
  const normalizedYear = Number(year);
  const leapMonth = getLunarLeapMonth(normalizedYear);
  const options = [];
  for (let month = 1; month <= 12; month += 1) {
    options.push({
      value: `${month}:0`,
      label: getLunarMonthLabel(month),
      month,
      isLeap: false,
    });
    if (leapMonth === month) {
      options.push({
        value: `${month}:1`,
        label: getLunarMonthLabel(month, true),
        month,
        isLeap: true,
      });
    }
  }
  return options;
}

export function getStemBranchYear(year) {
  const normalizedYear = Number(year);
  if (!Number.isFinite(normalizedYear)) {
    return "";
  }
  const stem = heavenlyStems[((normalizedYear - 4) % 10 + 10) % 10];
  const branch = earthlyBranches[((normalizedYear - 4) % 12 + 12) % 12];
  return `${stem}${branch}`;
}

export function getZodiacByLunarYear(year) {
  const stemBranch = getStemBranchYear(year);
  return zodiacAnimals[stemBranch.slice(-1)] || "";
}

export function getLunarYearLabel(year) {
  const stemBranch = getStemBranchYear(year);
  const zodiac = getZodiacByLunarYear(year);
  return stemBranch && zodiac ? `${stemBranch}${zodiac}年` : "";
}

export function solarToLunar(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    return null;
  }

  let offset = daysFromBaseDate(date);
  let year = lunarMinYear;
  let yearDays = getLunarYearDays(year);
  while (year <= lunarMaxYear && offset >= yearDays) {
    offset -= yearDays;
    year += 1;
    yearDays = getLunarYearDays(year);
  }
  if (year > lunarMaxYear || offset < 0) {
    return null;
  }

  const leapMonth = getLunarLeapMonth(year);
  let month = 1;
  let isLeap = false;
  let monthDays = 0;
  while (month <= 12) {
    monthDays = isLeap ? getLunarLeapDays(year) : getNormalLunarMonthDays(year, month);
    if (offset < monthDays) {
      break;
    }
    offset -= monthDays;
    if (leapMonth === month && !isLeap) {
      isLeap = true;
    } else {
      isLeap = false;
      month += 1;
    }
  }
  if (month > 12) {
    return null;
  }

  const day = offset + 1;
  const monthText = getLunarMonthLabel(month, isLeap);
  const dayText = getLunarDayLabel(day);
  return {
    year,
    month,
    day,
    isLeap,
    monthText,
    dayText,
    full: `农历${year}年${monthText}${dayText}`,
    stemBranch: getStemBranchYear(year),
    zodiac: getZodiacByLunarYear(year),
    yearLabel: getLunarYearLabel(year),
  };
}

export function lunarToSolar(year, month, day, isLeap = false) {
  const normalizedYear = Number(year);
  const normalizedMonth = Number(month);
  const normalizedDay = Number(day);
  if (
    !Number.isInteger(normalizedYear) ||
    !Number.isInteger(normalizedMonth) ||
    !Number.isInteger(normalizedDay) ||
    normalizedYear < lunarMinYear ||
    normalizedYear > lunarMaxYear
  ) {
    return null;
  }

  const monthDays = getLunarMonthDays(normalizedYear, normalizedMonth, isLeap);
  if (!monthDays || normalizedDay < 1 || normalizedDay > monthDays) {
    return null;
  }

  let offset = 0;
  for (let currentYear = lunarMinYear; currentYear < normalizedYear; currentYear += 1) {
    offset += getLunarYearDays(currentYear);
  }
  const leapMonth = getLunarLeapMonth(normalizedYear);
  for (let currentMonth = 1; currentMonth < normalizedMonth; currentMonth += 1) {
    offset += getNormalLunarMonthDays(normalizedYear, currentMonth);
    if (leapMonth === currentMonth) {
      offset += getLunarLeapDays(normalizedYear);
    }
  }
  if (isLeap) {
    offset += getNormalLunarMonthDays(normalizedYear, normalizedMonth);
  }
  offset += normalizedDay - 1;

  return dateFromBaseOffset(offset);
}

export function startOfMonth(date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

export function formatDurationParts(totalMs, withCentiseconds = false) {
  const clamped = Math.max(0, totalMs);
  const totalSeconds = Math.floor(clamped / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const centiseconds = Math.floor((clamped % 1000) / 10);
  return {
    days,
    hours,
    minutes,
    seconds,
    centiseconds,
    label: withCentiseconds
      ? `${pad(Math.floor(totalSeconds / 3600))}:${pad(minutes)}:${pad(seconds)}.${pad(centiseconds)}`
      : `${days}天 ${pad(hours)}:${pad(minutes)}:${pad(seconds)}`,
  };
}

export function formatReadableDate(date) {
  return dateFormatter.format(date);
}

export function getLunarInfo(date) {
  const lunar = solarToLunar(date);
  if (lunar) {
    return {
      full: `农历${lunar.monthText}${lunar.dayText}`,
      short: lunar.day === 1 ? lunar.monthText : lunar.dayText,
      detail: lunar,
    };
  }
  if (!lunarFormatter) {
    return { full: "农历信息暂不可用", short: "" };
  }
  try {
    const raw = lunarFormatter.format(date);
    const monthMatch = raw.match(/([正一二三四五六七八九十冬腊\d]+月)/);
    const dayMatch = raw.match(/(\d+)(?:日)?$/);
    const monthText = monthMatch?.[1] || "";
    const dayNumber = Number(dayMatch?.[1] || 0);
    const dayText = lunarDayLabels[dayNumber] || "";
    return {
      full: monthText && dayText ? `农历${monthText}${dayText}` : `农历${raw}`,
      short: dayNumber === 1 && monthText ? monthText : dayText || monthText || raw,
    };
  } catch {
    return { full: "农历信息暂不可用", short: "" };
  }
}

export function getChineseYearName(date) {
  const lunar = solarToLunar(date);
  if (lunar?.stemBranch) {
    return lunar.stemBranch;
  }
  if (!lunarFormatter) {
    return "";
  }
  try {
    const raw = lunarFormatter.format(date);
    const match = raw.match(/([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])年/);
    return match?.[1] || "";
  } catch {
    return "";
  }
}

export function getChineseZodiac(date) {
  const lunar = solarToLunar(date);
  if (lunar?.zodiac) {
    return lunar.zodiac;
  }
  const stemBranch = getChineseYearName(date);
  return zodiacAnimals[stemBranch.slice(-1)] || "";
}

export function getWesternZodiac(date) {
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const current = month * 100 + day;
  const ranges = [
    { name: "摩羯座", from: 101, to: 119 },
    { name: "水瓶座", from: 120, to: 218 },
    { name: "双鱼座", from: 219, to: 320 },
    { name: "白羊座", from: 321, to: 419 },
    { name: "金牛座", from: 420, to: 520 },
    { name: "双子座", from: 521, to: 621 },
    { name: "巨蟹座", from: 622, to: 722 },
    { name: "狮子座", from: 723, to: 822 },
    { name: "处女座", from: 823, to: 922 },
    { name: "天秤座", from: 923, to: 1023 },
    { name: "天蝎座", from: 1024, to: 1122 },
    { name: "射手座", from: 1123, to: 1221 },
    { name: "摩羯座", from: 1222, to: 1231 },
  ];
  return ranges.find((item) => current >= item.from && current <= item.to)?.name || "";
}

export function getDayOfYear(date) {
  const start = new Date(date.getFullYear(), 0, 0);
  return Math.floor((date - start) / 86400000);
}

export function getWeekOfYear(date) {
  const target = new Date(date);
  const dayNumber = (target.getDay() + 6) % 7;
  target.setDate(target.getDate() - dayNumber + 3);
  const firstThursday = new Date(target.getFullYear(), 0, 4);
  const firstDayNumber = (firstThursday.getDay() + 6) % 7;
  firstThursday.setDate(firstThursday.getDate() - firstDayNumber + 3);
  return 1 + Math.round((target - firstThursday) / 604800000);
}

export function getZoneOffsetLabel(zone, timestamp) {
  try {
    const formatter = new Intl.DateTimeFormat("zh-CN", {
      timeZone: zone,
      timeZoneName: "shortOffset",
      hour: "2-digit",
      minute: "2-digit",
    });
    return formatter.formatToParts(new Date(timestamp)).find((item) => item.type === "timeZoneName")?.value || zone;
  } catch {
    return zone;
  }
}

export function formatZoneDateTime(timestamp, zone) {
  return new Intl.DateTimeFormat("zh-CN", {
    timeZone: zone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(new Date(timestamp));
}

export function formatZoneTime(timestamp, zone) {
  return new Intl.DateTimeFormat("zh-CN", {
    timeZone: zone,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(new Date(timestamp));
}

export function formatZoneDate(timestamp, zone) {
  return new Intl.DateTimeFormat("zh-CN", {
    timeZone: zone,
    month: "2-digit",
    day: "2-digit",
    weekday: "short",
  }).format(new Date(timestamp));
}

export function computeCalendarDiff(startDate, endDate) {
  let start = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
  let end = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
  if (start > end) {
    [start, end] = [end, start];
  }
  let years = end.getFullYear() - start.getFullYear();
  let months = end.getMonth() - start.getMonth();
  let days = end.getDate() - start.getDate();
  if (days < 0) {
    const previousMonthLastDay = new Date(end.getFullYear(), end.getMonth(), 0).getDate();
    days += previousMonthLastDay;
    months -= 1;
  }
  if (months < 0) {
    months += 12;
    years -= 1;
  }
  return { years, months, days };
}

export function countWeekdays(startDate, endDate, inclusive) {
  let start = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
  let end = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
  if (start > end) {
    [start, end] = [end, start];
  }
  if (inclusive) {
    end = addDays(end, 1);
  }
  let total = 0;
  for (let cursor = new Date(start); cursor < end; cursor = addDays(cursor, 1)) {
    const day = cursor.getDay();
    if (day !== 0 && day !== 6) {
      total += 1;
    }
  }
  return total;
}
