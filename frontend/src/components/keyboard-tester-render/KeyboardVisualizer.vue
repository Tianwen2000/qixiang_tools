<script setup>
import KeyboardKeyCap from "./KeyboardKeyCap.vue";
import KeyboardRow from "./KeyboardRow.vue";
import KeyboardStatusBar from "./KeyboardStatusBar.vue";

const props = defineProps({
  layout: {
    type: Object,
    required: true,
  },
  pressedKeys: {
    type: Object,
    required: true,
  },
  testedKeys: {
    type: Object,
    required: true,
  },
  lastKey: {
    type: Object,
    required: true,
  },
});

function resolveState(keyItem) {
  if (!keyItem) {
    return "default";
  }

  const isPressed = Boolean(props.pressedKeys?.[keyItem.code]);
  const isTested = Boolean(props.testedKeys?.[keyItem.code]);

  if (isPressed) {
    return "activeOrange";
  }

  if (isTested) {
    return "activeGreen";
  }

  return "default";
}
</script>

<template>
  <div class="kb-scroll">
    <section class="kb-panel" aria-label="全尺寸键盘状态检测面板">
      <div class="kb-top-line">
        <div class="kb-top-left">
          <KeyboardRow :keys="layout.topLeft" :resolve-state="resolveState" />
          <div class="kb-function-groups">
            <KeyboardRow
              v-for="(group, groupIndex) in layout.functionGroups"
              :key="`function-group-${groupIndex}`"
              :keys="group"
              :resolve-state="resolveState"
            />
          </div>
        </div>

        <div class="kb-top-right">
          <div class="kb-top-editor">
            <KeyboardRow :keys="layout.editorTopRow" :resolve-state="resolveState" />
          </div>

          <div class="kb-top-status">
            <KeyboardStatusBar :last-key="lastKey" />
          </div>
        </div>
      </div>

      <div class="kb-body">
        <div class="kb-main-area">
          <KeyboardRow
            v-for="(row, rowIndex) in layout.mainRows"
            :key="`main-row-${rowIndex}`"
            :keys="row"
            :resolve-state="resolveState"
          />
        </div>

        <div class="kb-side-area">
          <div class="kb-edit-area">
            <KeyboardRow
              v-for="(row, rowIndex) in layout.editRows"
              :key="`edit-row-${rowIndex}`"
              :keys="row"
              :resolve-state="resolveState"
            />
          </div>

          <div class="kb-arrow-area">
            <KeyboardRow
              v-for="(row, rowIndex) in layout.arrowRows"
              :key="`arrow-row-${rowIndex}`"
              :keys="row"
              :resolve-state="resolveState"
            />
          </div>
        </div>

        <div class="kb-numpad-grid">
          <KeyboardKeyCap
            v-for="keyItem in layout.numpadKeys"
            :key="keyItem.id"
            :key-item="keyItem"
            :state="resolveState(keyItem)"
            layout-mode="grid"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.kb-scroll {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  box-sizing: border-box;
}

.kb-panel {
  --kb-unit: clamp(42px, 2.75vw, 48px);
  --kb-gap: 6px;
  --kb-key-height: 42px;
  --kb-key-default: #f2f2f2;
  --kb-text: #8d97a8;
  --kb-green: #8df76b;
  --kb-orange: #f2b14f;
  --kb-active-text: #5e6674;
  --kb-section-gap: 12px;
  --kb-group-gap: 12px;

  width: max-content;
  min-width: max-content;
  background: #000000;
  padding: 10px 18px 12px 14px;
  display: grid;
  gap: 10px;
  box-sizing: border-box;
}

.kb-top-line {
  display: flex;
  align-items: flex-start;
  gap: 81px}

.kb-top-left,
.kb-function-groups,
.kb-edit-area,
.kb-arrow-area,
.kb-main-area,
.kb-side-area {
  display: grid;
  gap: var(--kb-gap);
}

.kb-top-left {
  display: flex;
  align-items: flex-start;
  gap: var(--kb-group-gap);
  flex: 0 0 auto;
}

.kb-function-groups {
  display: flex;
  align-items: flex-start;
  gap: var(--kb-group-gap);
}

.kb-top-right {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex: 0 0 auto;
}

.kb-top-editor {
  display: flex;
  align-items: flex-start;
}

.kb-top-status {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  white-space: nowrap;
  flex: 0 0 auto;
  min-height: var(--kb-key-height);
}

.kb-body {
  display: grid;
  grid-template-columns: auto auto auto;
  align-items: start;
  column-gap: 12px;
}

.kb-main-area {
  flex: 0 0 auto;
}

.kb-side-area {
  flex: 0 0 auto;
  gap: 8px;
}

.kb-edit-area {
  gap: var(--kb-gap);
}

.kb-arrow-area {
  padding-top: calc(var(--kb-key-height) + var(--kb-gap));
  gap: var(--kb-gap);
}

.kb-numpad-grid {
  display: grid;
  grid-template-columns: repeat(4, var(--kb-unit));
  grid-auto-rows: var(--kb-key-height);
  gap: var(--kb-gap);
  align-self: start;
}

@media (max-width: 1280px) {
  .kb-panel {
    --kb-unit: 44px;
    --kb-gap: 5px;
    --kb-key-height: 40px;
    --kb-section-gap: 10px;
    --kb-group-gap: 10px;
    padding: 10px 16px 12px 12px;
  }

  .kb-top-line,
  .kb-body {
    column-gap: 10px;
  }

  .kb-top-right {
    transform: translateX(-6px);
  }
}

@media (max-width: 960px) {
  .kb-panel {
    --kb-unit: 40px;
    --kb-gap: 5px;
    --kb-key-height: 38px;
    --kb-section-gap: 8px;
    --kb-group-gap: 8px;
    padding: 10px 14px 12px 10px;
  }

  .kb-top-line,
  .kb-body {
    column-gap: 8px;
  }

  .kb-top-right {
    transform: translateX(-4px);
  }
}
</style>