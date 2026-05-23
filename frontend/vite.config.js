import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 5173,
    allowedHosts: [
      "vol-advice-invest-commented.trycloudflare.com", // 开放一个trycloudflare.com的白名单以便临时分享给别人访问，每次更改cf的域名后，这里都需要对应更改
    ],
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
