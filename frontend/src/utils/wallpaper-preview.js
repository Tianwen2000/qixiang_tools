const WALLPAPER_PREVIEW_STORAGE_KEY = "tw-wallpaper-preview-v1";
const WALLPAPER_PREVIEW_EVENT = "tw-wallpaper-preview-change";
const VALID_PREVIEW_MODES = new Set(["auto", "spring", "summer", "autumn", "winter"]);

export function getWallpaperPreviewMode() {
  if (typeof window === "undefined") {
    return "auto";
  }
  try {
    const value = window.sessionStorage.getItem(WALLPAPER_PREVIEW_STORAGE_KEY) || "auto";
    return VALID_PREVIEW_MODES.has(value) ? value : "auto";
  } catch {
    return "auto";
  }
}

export function setWallpaperPreviewMode(mode) {
  if (typeof window === "undefined") {
    return "auto";
  }
  const nextMode = VALID_PREVIEW_MODES.has(mode) ? mode : "auto";
  try {
    window.sessionStorage.setItem(WALLPAPER_PREVIEW_STORAGE_KEY, nextMode);
  } catch {
    // Ignore storage failures on privacy-restricted browsers.
  }
  window.dispatchEvent(
    new CustomEvent(WALLPAPER_PREVIEW_EVENT, {
      detail: { mode: nextMode },
    }),
  );
  return nextMode;
}

export function onWallpaperPreviewModeChange(handler) {
  if (typeof window === "undefined") {
    return () => {};
  }

  const listener = (event) => {
    handler(event.detail?.mode || getWallpaperPreviewMode());
  };

  window.addEventListener(WALLPAPER_PREVIEW_EVENT, listener);
  return () => {
    window.removeEventListener(WALLPAPER_PREVIEW_EVENT, listener);
  };
}
