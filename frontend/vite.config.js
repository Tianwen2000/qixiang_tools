// 文件说明：Vite 构建配置，负责开发服务器、代理和前端构建参数。
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,
    port: 5173,
    allowedHosts: [
      "192.168.9.69", // 本机当前局域网 IP，手机同 Wi-Fi 调试时访问
      "vol-advice-invest-commented.trycloudflare.com", // 开放一个trycloudflare.com的白名单以便临时分享给别人访问，每次更改cf的域名后，这里都需要对应更改
    ],
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000", //浏览器请求 localhost:5173/api/xxx
                                         // Vite 内部转发到 127.0.0.1:8000/api/xxx
        changeOrigin: true,
      },
    },
  },
});
