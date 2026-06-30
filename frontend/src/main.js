// 文件说明：Vue 前端入口，创建应用、挂载路由并引入全局样式。
import { createApp } from "vue";

import App from "./App.vue";
import router from "./router/index.js";
import "./styles/reset.css";
import "./styles/global.css";
import "./styles/wallpaper.css";
import "./styles/tool.css";

const app = createApp(App);

app.use(router).mount("#app");
