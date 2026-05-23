<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean, Object],
    default: "",
  },
  options: {
    type: Array,
    default: () => [],
  },
  placeholder: {
    type: String,
    default: "请选择",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["update:modelValue", "change"]);

const rootRef = ref(null);
const buttonRef = ref(null);
const open = ref(false);
const activeIndex = ref(-1);
const menuPlacement = ref("bottom");
const optionRefs = ref([]);
const listboxId = `glass-select-${Math.random().toString(36).slice(2, 10)}`;

const normalizedOptions = computed(() =>
  (props.options || []).map((option) => {
    if (option && typeof option === "object") {
      return {
        value: option.value,
        label: option.label ?? String(option.value ?? ""),
        description: option.description ?? "",
      };
    }
    return {
      value: option,
      label: String(option),
      description: "",
    };
  }),
);

const selectedIndex = computed(() =>
  normalizedOptions.value.findIndex((option) => Object.is(option.value, props.modelValue)),
);

const selectedOption = computed(() => normalizedOptions.value[selectedIndex.value] || null);

const displayLabel = computed(() => selectedOption.value?.label || props.placeholder);

function syncActiveIndex() {
  if (selectedIndex.value >= 0) {
    activeIndex.value = selectedIndex.value;
    return;
  }
  activeIndex.value = normalizedOptions.value.length ? 0 : -1;
}

function updatePlacement() {
  if (!rootRef.value || typeof window === "undefined") {
    return;
  }
  const rect = rootRef.value.getBoundingClientRect();
  const estimatedMenuHeight = Math.min(320, Math.max(220, normalizedOptions.value.length * 56));
  const spaceBelow = window.innerHeight - rect.bottom;
  const spaceAbove = rect.top;
  menuPlacement.value = spaceBelow < estimatedMenuHeight && spaceAbove > spaceBelow ? "top" : "bottom";
}

function openMenu() {
  if (props.disabled || !normalizedOptions.value.length) {
    return;
  }
  syncActiveIndex();
  updatePlacement();
  open.value = true;
}

function closeMenu() {
  open.value = false;
}

function toggleMenu() {
  if (open.value) {
    closeMenu();
    return;
  }
  openMenu();
}

function selectOption(option, { restoreFocus = true } = {}) {
  emit("update:modelValue", option.value);
  emit("change", option.value);
  closeMenu();
  if (restoreFocus) {
    buttonRef.value?.focus();
  }
}

function setOptionRef(element, index) {
  optionRefs.value[index] = element;
}

function scrollActiveOptionIntoView() {
  const node = optionRefs.value[activeIndex.value];
  if (node?.scrollIntoView) {
    node.scrollIntoView({ block: "nearest" });
  }
}

function moveActive(step) {
  if (!normalizedOptions.value.length) {
    return;
  }
  if (!open.value) {
    openMenu();
    return;
  }
  const total = normalizedOptions.value.length;
  const current = activeIndex.value === -1 ? 0 : activeIndex.value;
  activeIndex.value = (current + step + total) % total;
  scrollActiveOptionIntoView();
}

function confirmActive() {
  const option = normalizedOptions.value[activeIndex.value];
  if (option) {
    selectOption(option);
  }
}

function handleDocumentPointer(event) {
  if (!rootRef.value?.contains(event.target)) {
    closeMenu();
  }
}

watch(
  () => props.modelValue,
  () => {
    syncActiveIndex();
  },
  { immediate: true },
);

watch(
  () => props.options,
  () => {
    optionRefs.value = [];
    syncActiveIndex();
  },
  { deep: true },
);

onMounted(() => {
  document.addEventListener("pointerdown", handleDocumentPointer);
  window.addEventListener("resize", updatePlacement);
});

onBeforeUnmount(() => {
  document.removeEventListener("pointerdown", handleDocumentPointer);
  window.removeEventListener("resize", updatePlacement);
});
</script>

<template>
  <div
    ref="rootRef"
    class="glass-select"
    :class="{ open, disabled, 'is-empty': !selectedOption, 'opens-up': menuPlacement === 'top' }"
    @keydown.down.prevent="moveActive(1)"
    @keydown.up.prevent="moveActive(-1)"
    @keydown.enter.prevent="open ? confirmActive() : openMenu()"
    @keydown.space.prevent="open ? confirmActive() : openMenu()"
    @keydown.esc.prevent="closeMenu"
    @keydown.tab="closeMenu"
  >
    <button
      :id="`${listboxId}-trigger`"
      ref="buttonRef"
      type="button"
      class="glass-select-trigger"
      :aria-controls="listboxId"
      aria-haspopup="listbox"
      :aria-expanded="open ? 'true' : 'false'"
      :disabled="disabled"
      @click="toggleMenu"
    >
      <span class="glass-select-trigger-text" :class="{ placeholder: !selectedOption }">
        {{ displayLabel }}
      </span>
      <span class="glass-select-caret" aria-hidden="true">⌄</span>
    </button>

    <transition name="glass-select-pop">
      <div v-if="open" :id="listboxId" class="glass-select-menu" role="listbox" :aria-labelledby="`${listboxId}-trigger`">
        <button
          v-for="(option, index) in normalizedOptions"
          :key="`${option.label}-${index}`"
          :ref="(element) => setOptionRef(element, index)"
          type="button"
          class="glass-select-option"
          :class="{ active: index === activeIndex, selected: Object.is(option.value, props.modelValue) }"
          role="option"
          :aria-selected="Object.is(option.value, props.modelValue) ? 'true' : 'false'"
          @mouseenter="activeIndex = index"
          @click="selectOption(option)"
        >
          <span class="glass-select-option-main">
            <span class="glass-select-option-label">{{ option.label }}</span>
            <small v-if="option.description" class="glass-select-option-description">{{ option.description }}</small>
          </span>
          <span class="glass-select-option-check" aria-hidden="true">
            {{ Object.is(option.value, props.modelValue) ? "✓" : "" }}
          </span>
        </button>
      </div>
    </transition>
  </div>
</template>
