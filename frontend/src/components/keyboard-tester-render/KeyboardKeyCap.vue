<script setup>
import { computed } from "vue";

const props = defineProps({
  keyItem: {
    type: Object,
    required: true,
  },
  state: {
    type: String,
    default: "default",
  },
  layoutMode: {
    type: String,
    default: "flex",
  },
});

const isSpacer = computed(() => {
  return (
    props.keyItem?.placeholder === true ||
    props.keyItem?.spacer === true ||
    (
      (props.keyItem?.label === "" || props.keyItem?.label == null) &&
      !props.keyItem?.secondaryLabel
    )
  );
});

const stateClass = computed(() => {
  if (isSpacer.value) {
    return "is-spacer";
  }

  if (props.state === "activeOrange" || props.state === "activeYellow") {
    return "is-active-orange";
  }
  if (props.state === "activeGreen") {
    return "is-active-green";
  }
  return "is-default";
});

const isSecondaryOnTop = computed(() => props.keyItem.secondaryPlacement !== "bottom");

const keyStyle = computed(() => {
  const widthRatio = props.keyItem.widthRatio || 1;
  const style = {
    "--kb-width-ratio": String(widthRatio),
  };

  if (props.layoutMode === "grid") {
    style.gridColumn = `span ${props.keyItem.colSpan || 1}`;
    style.gridRow = `span ${props.keyItem.rowSpan || 1}`;
  }

  return style;
});
</script>

<template>
  <div
    class="kb-key"
    :class="[
      stateClass,
      {
        'is-tall': keyItem.tall,
        'is-grid': layoutMode === 'grid',
        'is-center': keyItem.align === 'center',
        'is-unavailable': keyItem.unavailable,
      },
    ]"
    :style="keyStyle"
  >
    <div
      v-if="!isSpacer"
      class="kb-key-content"
      :class="{ 'is-stack-bottom': keyItem.secondaryLabel && !isSecondaryOnTop }"
    >
      <template v-if="keyItem.secondaryLabel">
        <span v-if="isSecondaryOnTop" class="kb-key-secondary">{{ keyItem.secondaryLabel }}</span>
        <span class="kb-key-primary">{{ keyItem.label }}</span>
        <span v-if="!isSecondaryOnTop" class="kb-key-secondary">{{ keyItem.secondaryLabel }}</span>
      </template>
      <span v-else class="kb-key-primary">{{ keyItem.label }}</span>
    </div>
  </div>
</template>

<style scoped>
.kb-key {
  width: calc((var(--kb-unit) * var(--kb-width-ratio)) + (var(--kb-gap) * (var(--kb-width-ratio) - 1)));
  min-width: calc((var(--kb-unit) * var(--kb-width-ratio)) + (var(--kb-gap) * (var(--kb-width-ratio) - 1)));
  height: var(--kb-key-height);
  background: var(--kb-key-default);
  color: var(--kb-text);
  border-radius: 2px;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  box-sizing: border-box;
  transition: background-color 0.12s ease, color 0.12s ease, opacity 0.12s ease;
}

.kb-key.is-grid {
  width: auto;
  min-width: 0;
  height: auto;
}

.kb-key.is-tall {
  height: calc((var(--kb-key-height) * 2) + var(--kb-gap));
}

.kb-key.is-default {
  background: var(--kb-key-default);
  color: var(--kb-text);
}

.kb-key.is-active-green {
  background: var(--kb-green);
  color: var(--kb-active-text);
}

.kb-key.is-active-orange {
  background: var(--kb-orange);
  color: var(--kb-active-text);
}

.kb-key.is-unavailable {
  opacity: 0.58;
}

.kb-key.is-spacer {
  background: transparent;
  color: transparent;
  pointer-events: none;
  box-shadow: none;
}

.kb-key-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  padding: 5px 6px 4px;
  box-sizing: border-box;
  line-height: 1.05;
  gap: 2px;
}

.kb-key-content.is-stack-bottom {
  justify-content: space-between;
}

.kb-key.is-center .kb-key-content {
  align-items: center;
  justify-content: center;
  padding: 0;
}

.kb-key-primary,
.kb-key-secondary {
  color: currentColor;
  white-space: nowrap;
}

.kb-key-primary {
  font-size: 10px;
  font-weight: 600;
}

.kb-key-secondary {
  font-size: 10px;
  font-weight: 500;
}

.kb-key.is-center .kb-key-primary,
.kb-key.is-center .kb-key-secondary {
  text-align: center;
}
</style>