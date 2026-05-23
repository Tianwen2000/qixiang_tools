import { createApp } from "vue";

import App from "./App.vue";
import router from "./router/index.js";
import "./styles/reset.css";
import "./styles/global.css";
import "./styles/wallpaper.css";
import "./styles/tool.css";

const app = createApp(App);

app.use(router).mount("#app");
