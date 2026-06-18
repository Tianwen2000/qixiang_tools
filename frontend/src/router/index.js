import { createRouter, createWebHistory } from "vue-router";

import FeedbackPage from "../pages/FeedbackPage.vue";
import FavoritesPage from "../pages/FavoritesPage.vue";
import Home from "../pages/Home.vue";
import PreviewPage from "../pages/PreviewPage.vue";
import SupportPage from "../pages/SupportPage.vue";
import ToolPage from "../pages/ToolPage.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: Home, meta: { wallpaperMode: "seasonal" } },
    { path: "/tool/:slug", name: "tool", component: ToolPage, props: true, meta: { wallpaperMode: "seasonal" } },
    { path: "/favorites", name: "favorites", component: FavoritesPage, meta: { wallpaperMode: "seasonal" } },
    { path: "/preview", name: "preview", component: PreviewPage, meta: { wallpaperMode: "seasonal" } },
    { path: "/feedback", name: "feedback", component: FeedbackPage, meta: { wallpaperMode: "seasonal" } },
    { path: "/support", name: "support", component: SupportPage, meta: { wallpaperMode: "seasonal" } },
    {
      path: "/admin",
      name: "admin",
      component: () => import("../components/ai-assistant/AdminConsole.vue"),
      meta: { wallpaperMode: "seasonal" },
    },
    { path: "/:pathMatch(.*)*", redirect: { name: "home" } },
  ],
});

export default router;
