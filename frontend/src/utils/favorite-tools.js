import { computed, reactive, readonly } from "vue";

import { readJsonCache, writeJsonCache } from "./page-cache.js";

const FAVORITES_STORAGE_KEY = "tw-favorite-tools-v2";
const FAVORITES_MARKER_COOKIE_KEY = "tw_has_favorites";
const FAVORITES_EVENT = "tw-favorites-change";
const COOKIE_MAX_AGE = 60 * 60 * 24 * 365;

const state = reactive({
  slugs: readFavoriteSlugsFromStorage(),
});

let syncBound = false;

function readFavoriteSlugsFromStorage() {
  const value = readJsonCache(FAVORITES_STORAGE_KEY, []);
  return Array.isArray(value) ? [...new Set(value.filter(Boolean))] : [];
}

function writeFavoriteMarkerCookie(hasFavorites) {
  if (typeof document === "undefined") {
    return;
  }
  document.cookie = `${FAVORITES_MARKER_COOKIE_KEY}=${hasFavorites ? "1" : "0"}; path=/; max-age=${COOKIE_MAX_AGE}; SameSite=Lax`;
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

function syncFavoriteState(slugs, emit = true) {
  state.slugs = [...new Set(slugs.filter(Boolean))];
  writeJsonCache(FAVORITES_STORAGE_KEY, state.slugs);
  writeFavoriteMarkerCookie(state.slugs.length > 0);
  if (emit) {
    emitFavoriteChange();
  }
}

function ensureFavoriteSyncBinding() {
  if (syncBound || typeof window === "undefined") {
    return;
  }

  const handleStorage = (event) => {
    if (!event.key || event.key === FAVORITES_STORAGE_KEY) {
      syncFavoriteState(readFavoriteSlugsFromStorage(), false);
    }
  };

  const handleFavoriteEvent = (event) => {
    const nextSlugs = Array.isArray(event.detail?.slugs) ? event.detail.slugs : readFavoriteSlugsFromStorage();
    syncFavoriteState(nextSlugs, false);
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
