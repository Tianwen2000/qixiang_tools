<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import { getTool } from "../api/tools.js";
import LoadingState from "../components/LoadingState.vue";
import SiteHeader from "../components/SiteHeader.vue";
import ToolAbstractAppliance from "../components/ToolAbstractAppliance.vue";
import ToolBrowserInfo from "../components/ToolBrowserInfo.vue";
import ToolChartStudio from "../components/ToolChartStudio.vue";
import ToolDateTimeCard from "../components/ToolDateTimeCard.vue";
import ToolDateIntervalCalculator from "../components/ToolDateIntervalCalculator.vue";
import ToolDetailActions from "../components/ToolDetailActions.vue";
import ToolDinoRunner from "../components/ToolDinoRunner.vue";
import ToolFileForm from "../components/ToolFileForm.vue";
import ToolHttpTester from "../components/ToolHttpTester.vue";
import ToolKeyboardTester from "../components/ToolKeyboardTester.vue";
import ToolLocalIpLookup from "../components/ToolLocalIpLookup.vue";
import ToolMarketQuote from "../components/ToolMarketQuote.vue";
import ToolOffWorkCountdown from "../components/ToolOffWorkCountdown.vue";
import ToolOnlineCalendar from "../components/ToolOnlineCalendar.vue";
import ToolResponsiveCheck from "../components/ToolResponsiveCheck.vue";
import ToolSolarLunarViewer from "../components/ToolSolarLunarViewer.vue";
import ToolStopwatchTimer from "../components/ToolStopwatchTimer.vue";
import ToolTextForm from "../components/ToolTextForm.vue";
import ToolTimeConverter from "../components/ToolTimeConverter.vue";
import ToolWhiteboard from "../components/ToolWhiteboard.vue";
import ToolWebsocketTester from "../components/ToolWebsocketTester.vue";
import ToolWorldTimeClock from "../components/ToolWorldTimeClock.vue";
import ToolTimestampConverter from "../components/ToolTimestampConverter.vue";
import ToolAgeCalculator from "../components/ToolAgeCalculator.vue";
import ToolBabyHundredDaysCalculator from "../components/ToolBabyHundredDaysCalculator.vue";
import ToolChineseHistoryTable from "../components/ToolChineseHistoryTable.vue";
import ToolCommandCatalog from "../components/ToolCommandCatalog.vue";
import ToolCountdownTimer from "../components/ToolCountdownTimer.vue";
import ToolHolidaySchedule2026 from "../components/ToolHolidaySchedule2026.vue";
import { getCategoryTheme, getToolModeLabel, resolveToolComponent } from "../data/ui-mapping.js";
import { readJsonCache, writeJsonCache } from "../utils/page-cache.js";
import ToolPregnancyDueCalculator from "../components/ToolPregnancyDueCalculator.vue";
import ToolScheduleMemo from "../components/ToolScheduleMemo.vue";
import ToolShelfLifeCalculator from "../components/ToolShelfLifeCalculator.vue";
import ToolSolarTermsViewer from "../components/ToolSolarTermsViewer.vue";
import ToolZodiacSignFinder from "../components/ToolZodiacSignFinder.vue";

const route = useRoute();
const tool = ref(null);
const loading = ref(true);
const error = ref("");
const headerKeyword = ref(typeof route.query.keyword === "string" ? route.query.keyword : "");

const componentName = computed(() => resolveToolComponent(tool.value));
const formComponent = computed(() => {
  const componentMap = {
    ToolTextForm,
    ToolFileForm,
    ToolAbstractAppliance,
    ToolBrowserInfo,
    ToolChartStudio,
    ToolDateIntervalCalculator,
    ToolDinoRunner,
    ToolHttpTester,
    ToolKeyboardTester,
    ToolLocalIpLookup,
    ToolMarketQuote,
    ToolOffWorkCountdown,
    ToolOnlineCalendar,
    ToolScheduleMemo,
    ToolResponsiveCheck,
    ToolSolarLunarViewer,
    ToolSolarTermsViewer,
    ToolStopwatchTimer,
    ToolTimeConverter,
    ToolTimestampConverter,
    ToolWorldTimeClock,
    ToolAgeCalculator,
    ToolBabyHundredDaysCalculator,
    ToolChineseHistoryTable,
    ToolCommandCatalog,
    ToolCountdownTimer,
    ToolHolidaySchedule2026,
    ToolPregnancyDueCalculator,
    ToolShelfLifeCalculator,
    ToolZodiacSignFinder,
    ToolWhiteboard,
    ToolWebsocketTester,
  };
  return componentMap[componentName.value] || ToolTextForm;
});
const toolTheme = computed(() => getCategoryTheme(tool.value?.category));
const headerActiveCategory = computed(() => {
  if (typeof route.query.category === "string" && route.query.category) {
    return route.query.category;
  }
  return tool.value?.category || "";
});
const backTarget = computed(() => {
  const query = {};
  if (typeof route.query.category === "string" && route.query.category) {
    query.category = route.query.category;
  }
  if (typeof route.query.keyword === "string" && route.query.keyword) {
    query.keyword = route.query.keyword;
  }
  return { name: "home", query };
});
const backLabel = computed(() => {
  if (typeof route.query.keyword === "string" && route.query.keyword) {
    return "返回搜索结果";
  }
  if (typeof route.query.category === "string" && route.query.category) {
    return "返回上一分类";
  }
  return "返回工具首页";
});

function getToolCacheKey(slug) {
  return `tw-tool-detail-${slug}`;
}

function hydrateToolFromCache(slug) {
  const cachedTool = readJsonCache(getToolCacheKey(slug), null);
  if (!cachedTool?.slug || cachedTool.slug !== slug) {
    return false;
  }
  tool.value = cachedTool;
  loading.value = false;
  return true;
}

async function fetchTool() {
  const slug = route.params.slug;
  const hasCachedTool = hydrateToolFromCache(slug);
  if (!hasCachedTool) {
    tool.value = null;
  }
  loading.value = !hasCachedTool;
  error.value = "";
  try {
    const latestTool = await getTool(slug);
    tool.value = latestTool;
    writeJsonCache(getToolCacheKey(slug), latestTool);
  } catch (err) {
    if (!tool.value) {
      error.value = err.message || "工具加载失败";
    }
  } finally {
    loading.value = false;
  }
}

hydrateToolFromCache(route.params.slug);

watch(
  () => route.params.slug,
  () => {
    fetchTool();
  },
);

watch(
  () => route.query.keyword,
  (value) => {
    headerKeyword.value = typeof value === "string" ? value : "";
  },
);

onMounted(fetchTool);
</script>

<template>
  <main class="tool-detail-page">
    <SiteHeader :active-category="headerActiveCategory" :keyword="headerKeyword" @update:keyword="headerKeyword = $event" />

    <div class="page-shell">
      <div class="detail-back-row">
        <router-link class="back-link prominent" :to="backTarget">{{ backLabel }}</router-link>
      </div>
      <LoadingState v-if="loading" />
      <section v-else-if="error" class="empty-state status-card">
        <h3>工具详情暂时打不开</h3>
        <p>{{ error }}</p>
        <button type="button" class="mega-panel-action" @click="fetchTool">重新加载</button>
      </section>
      <section
        v-else-if="tool"
        class="tool-page"
        :style="{ '--detail-accent': toolTheme.accent, '--detail-soft': toolTheme.soft }"
      >
        <header class="tool-header detail-header">
          <div class="detail-header-grid">
            <div class="detail-header-copy">
              <div class="tool-header-top">
                <span class="tool-chip">{{ getToolModeLabel(tool) }}</span>
                <span class="tool-chip muted">{{ toolTheme.label }}</span>
              </div>
              <h1>{{ tool.name }}</h1>
              <p>{{ tool.summary }}</p>
              <p class="tool-description">{{ tool.description }}</p>
            </div>
            <ToolDateTimeCard />
          </div>
        </header>
        <ToolDetailActions :tool="tool" />
        <component :is="formComponent" :tool="tool" />
      </section>
    </div>
  </main>
</template>
