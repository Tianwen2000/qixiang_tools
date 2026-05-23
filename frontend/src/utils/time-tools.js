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
