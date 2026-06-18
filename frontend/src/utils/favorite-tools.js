import { computed, reactive, readonly } from "vue";

import { writeJsonCache } from "./page-cache.js";

const FAVORITES_STORAGE_KEY = "tw-favorite-tools-v2";
const FAVORITES_BACKUP_STORAGE_KEY = "tw-favorite-tools-v2-backup";
const FAVORITES_LEGACY_STORAGE_KEYS = ["tw-favorite-tools-v1", "tw-favorite-tools"];
const FAVORITES_MARKER_COOKIE_KEY = "tw_has_favorites";
const FAVORITES_BACKUP_COOKIE_KEY = "tw_favorite_tools_v2";
const FAVORITES_EVENT = "tw-favorites-change";
const COOKIE_MAX_AGE = 60 * 60 * 24 * 365;
const COOKIE_VALUE_MAX_LENGTH = 3500;

const initialFavoriteStorage = readFavoriteSlugsFromStorage();

const state = reactive({
  slugs: initialFavoriteStorage.slugs,
});

let syncBound = false;

if (initialFavoriteStorage.recovered) {
  writeFavoriteSlugsToStorage(initialFavoriteStorage.slugs);
}

function normalizeFavoriteSlugs(slugs) {
  return [...new Set(slugs.filter((slug) => typeof slug === "string" && slug.trim()).map((slug) => slug.trim()))];
}

function readStoredFavoriteSlugs(key) {
  if (typeof window === "undefined") {
    return { key, status: "missing", slugs: [] };
  }

  try {
    const raw = window.localStorage.getItem(key);
    if (raw === null) {
      return { key, status: "missing", slugs: [] };
    }

    const value = JSON.parse(raw);
    if (!Array.isArray(value)) {
      return { key, status: "invalid", slugs: [] };
    }

    return { key, status: "valid", slugs: normalizeFavoriteSlugs(value) };
  } catch {
    return { key, status: "invalid", slugs: [] };
  }
}

function readFallbackFavoriteSlugs() {
  const fallbackSources = [
    () => readStoredFavoriteSlugs(FAVORITES_BACKUP_STORAGE_KEY),
    readFavoriteSlugsFromBackupCookie,
    ...FAVORITES_LEGACY_STORAGE_KEYS.map((key) => () => readStoredFavoriteSlugs(key)),
  ];

  for (const readFallback of fallbackSources) {
    const result = readFallback();
    if (result.status === "valid" && result.slugs.length > 0) {
      return result;
    }
  }
  return null;
}

function readFavoriteSlugsFromStorage(currentSlugs = []) {
  const primary = readStoredFavoriteSlugs(FAVORITES_STORAGE_KEY);
  if (primary.status === "valid") {
    return { slugs: primary.slugs, healthy: true, recovered: false };
  }

  const fallback = readFallbackFavoriteSlugs();
  if (fallback) {
    return { slugs: fallback.slugs, healthy: true, recovered: true };
  }

  if (primary.status === "invalid") {
    return { slugs: normalizeFavoriteSlugs(currentSlugs), healthy: false, recovered: false };
  }

  return { slugs: [], healthy: true, recovered: false };
}

function writeFavoriteSlugsToStorage(slugs) {
  writeJsonCache(FAVORITES_STORAGE_KEY, slugs);
  writeJsonCache(FAVORITES_BACKUP_STORAGE_KEY, slugs);
  writeFavoriteSlugsBackupCookie(slugs);
}

function writeFavoriteMarkerCookie(hasFavorites) {
  if (typeof document === "undefined") {
    return;
  }
  document.cookie = `${FAVORITES_MARKER_COOKIE_KEY}=${hasFavorites ? "1" : "0"}; path=/; max-age=${COOKIE_MAX_AGE}; SameSite=Lax`;
}

function readCookieValue(name) {
  if (typeof document === "undefined") {
    return "";
  }

  const prefix = `${name}=`;
  const matched = document.cookie
    .split(";")
    .map((item) => item.trim())
    .find((item) => item.startsWith(prefix));

  return matched ? matched.slice(prefix.length) : "";
}

function readFavoriteSlugsFromBackupCookie() {
  const raw = readCookieValue(FAVORITES_BACKUP_COOKIE_KEY);
  if (!raw) {
    return { key: FAVORITES_BACKUP_COOKIE_KEY, status: "missing", slugs: [] };
  }

  try {
    const value = JSON.parse(decodeURIComponent(raw));
    if (!Array.isArray(value)) {
      return { key: FAVORITES_BACKUP_COOKIE_KEY, status: "invalid", slugs: [] };
    }
    return { key: FAVORITES_BACKUP_COOKIE_KEY, status: "valid", slugs: normalizeFavoriteSlugs(value) };
  } catch {
    return { key: FAVORITES_BACKUP_COOKIE_KEY, status: "invalid", slugs: [] };
  }
}

function writeFavoriteSlugsBackupCookie(slugs) {
  if (typeof document === "undefined") {
    return;
  }

  const value = encodeURIComponent(JSON.stringify(slugs));
  if (value.length > COOKIE_VALUE_MAX_LENGTH) {
    document.cookie = `${FAVORITES_BACKUP_COOKIE_KEY}=; path=/; max-age=0; SameSite=Lax`;
    return;
  }

  document.cookie = `${FAVORITES_BACKUP_COOKIE_KEY}=${value}; path=/; max-age=${COOKIE_MAX_AGE}; SameSite=Lax`;
}

function emitFavoriteChange() {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(
    new CustomEvent(FAVORITES_EVENT, {
      detail: {
        slugs: [...state.slugs],
      },
    }),
  );
}

function setFavoriteState(slugs) {
  state.slugs = normalizeFavoriteSlugs(slugs);
}

function syncFavoriteState(slugs, emit = true) {
  setFavoriteState(slugs);
  writeFavoriteSlugsToStorage(state.slugs);
  writeFavoriteMarkerCookie(state.slugs.length > 0);
  if (emit) {
    emitFavoriteChange();
  }
}

function loadFavoriteStateFromStorage() {
  const result = readFavoriteSlugsFromStorage(state.slugs);
  if (!result.healthy && !result.recovered) {
    writeFavoriteMarkerCookie(state.slugs.length > 0);
    return;
  }

  setFavoriteState(result.slugs);
  if (result.recovered) {
    writeFavoriteSlugsToStorage(state.slugs);
  }
  writeFavoriteMarkerCookie(state.slugs.length > 0);
}

function ensureFavoriteSyncBinding() {
  if (syncBound || typeof window === "undefined") {
    return;
  }

  const handleStorage = (event) => {
    if (!event.key || event.key === FAVORITES_STORAGE_KEY) {
      loadFavoriteStateFromStorage();
    }
  };

  const handleFavoriteEvent = (event) => {
    if (Array.isArray(event.detail?.slugs)) {
      syncFavoriteState(event.detail.slugs, false);
      return;
    }
    loadFavoriteStateFromStorage();
  };

  window.addEventListener("storage", handleStorage);
  window.addEventListener(FAVORITES_EVENT, handleFavoriteEvent);
  syncBound = true;
}

export function readFavoriteSlugs() {
  ensureFavoriteSyncBinding();
  return [...state.slugs];
}

export function writeFavoriteSlugs(slugs) {
  ensureFavoriteSyncBinding();
  syncFavoriteState(slugs);
}

export function isFavoriteTool(slug) {
  ensureFavoriteSyncBinding();
  return state.slugs.includes(slug);
}

export function toggleFavoriteTool(slug) {
  ensureFavoriteSyncBinding();
  const next = state.slugs.includes(slug) ? state.slugs.filter((item) => item !== slug) : [...state.slugs, slug];
  syncFavoriteState(next);
  return next.includes(slug);
}

export function removeFavoriteTool(slug) {
  ensureFavoriteSyncBinding();
  syncFavoriteState(state.slugs.filter((item) => item !== slug));
}

export function clearFavoriteTools() {
  ensureFavoriteSyncBinding();
  syncFavoriteState([]);
}

export function moveFavoriteTool(slug, direction) {
  ensureFavoriteSyncBinding();
  const currentIndex = state.slugs.indexOf(slug);
  if (currentIndex === -1) {
    return [...state.slugs];
  }

  const targetIndex =
    direction === "up" ? Math.max(0, currentIndex - 1) : Math.min(state.slugs.length - 1, currentIndex + 1);

  if (currentIndex === targetIndex) {
    return [...state.slugs];
  }

  const next = [...state.slugs];
  const [item] = next.splice(currentIndex, 1);
  next.splice(targetIndex, 0, item);
  syncFavoriteState(next);
  return [...next];
}

export function useFavoriteTools() {
  ensureFavoriteSyncBinding();
  return {
    favoriteSlugs: computed(() => [...state.slugs]),
    favoriteCount: computed(() => state.slugs.length),
    state: readonly(state),
    isFavoriteTool,
    toggleFavoriteTool,
    removeFavoriteTool,
    clearFavoriteTools,
    moveFavoriteTool,
  };
}
