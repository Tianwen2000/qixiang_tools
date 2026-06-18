<script setup>
// 自包含的模型选择下拉：每行「模型名 + 右侧倍率徽标」，选中带 ✓ 高亮。
// 仅依赖 vue，保持 AI 模块独立。
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

const props = defineProps({
  modelValue: { type: [String, Number], default: "" },
  options: { type: Array, default: () => [] }, // [{ id, name, badge }]
  placeholder: { type: String, default: "选择模型" },
});

const emit = defineEmits(["update:modelValue"]);

const open = ref(false);
const rootRef = ref(null);

const selected = computed(() => props.options.find((item) => item.id === props.modelValue) || null);
const displayName = computed(() => selected.value?.name || props.placeholder);

function toggle() {
  if (props.options.length) open.value = !open.value;
}

function close() {
  open.value = false;
}

function choose(option) {
  emit("update:modelValue", option.id);
  close();
}

function onDocPointer(event) {
  if (rootRef.value && !rootRef.value.contains(event.target)) close();
}

onMounted(() => document.addEventListener("pointerdown", onDocPointer));
onBeforeUnmount(() => document.removeEventListener("pointerdown", onDocPointer));
</script>

<template>
  <div ref="rootRef" class="qxai-ms" :class="{ open }">
    <button
      type="button"
      class="qxai-ms-trigger"
      :class="{ placeholder: !selected }"
      :aria-expanded="open"
      aria-haspopup="listbox"
      @click="toggle"
    >
      <span class="qxai-ms-trigger-name">{{ displayName }}</span>
      <span v-if="selected?.badge" class="qxai-ms-trigger-badge">{{ selected.badge }}</span>
      <span class="qxai-ms-caret" aria-hidden="true">⌄</span>
    </button>

    <transition name="qxai-ms-pop">
      <ul v-if="open" class="qxai-ms-menu" role="listbox">
        <li v-for="option in options" :key="option.id">
          <button
            type="button"
            class="qxai-ms-option"
            :class="{ selected: option.id === modelValue }"
            role="option"
            :aria-selected="option.id === modelValue"
            @click="choose(option)"
          >
            <span class="qxai-ms-check" aria-hidden="true">{{ option.id === modelValue ? "✓" : "" }}</span>
            <span class="qxai-ms-name">{{ option.name }}</span>
            <span v-if="option.badge" class="qxai-ms-badge">{{ option.badge }}</span>
          </button>
        </li>
      </ul>
    </transition>
  </div>
</template>

<style scoped>
.qxai-ms {
  position: relative;
  width: 100%;
}

.qxai-ms-trigger {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 11px;
  border: 1px solid rgba(159, 188, 224, 0.7);
  background: #fff;
  padding: 0 10px;
  font-size: 13.5px;
  color: #20344f;
  cursor: pointer;
  transition: border-color 0.16s, box-shadow 0.16s;
}

.qxai-ms.open .qxai-ms-trigger,
.qxai-ms-trigger:hover {
  border-color: #6aa0ff;
  box-shadow: 0 0 0 3px rgba(106, 160, 255, 0.14);
}

.qxai-ms-trigger.placeholder {
  color: #8aa0bf;
}

.qxai-ms-trigger-name {
  flex: 1;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.qxai-ms-trigger-badge {
  font-size: 12px;
  color: #9aa6b8;
  font-variant-numeric: tabular-nums;
}

.qxai-ms-caret {
  color: #9aa6b8;
  font-size: 13px;
  line-height: 1;
  transition: transform 0.18s;
}

.qxai-ms.open .qxai-ms-caret {
  transform: rotate(180deg);
}

.qxai-ms-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  z-index: 5;
  margin: 0;
  padding: 6px;
  list-style: none;
  max-height: 280px;
  overflow-y: auto;
  border-radius: 12px;
  background: #fff;
  border: 1px solid rgba(117, 169, 255, 0.4);
  box-shadow: 0 16px 36px rgba(34, 70, 124, 0.22);
}

.qxai-ms-option {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
  background: transparent;
  border-radius: 9px;
  padding: 9px 8px;
  font-size: 13.5px;
  color: #2c3a4f;
  cursor: pointer;
  transition: background 0.14s;
}

.qxai-ms-option:hover {
  background: rgba(106, 160, 255, 0.12);
}

.qxai-ms-option.selected {
  background: rgba(106, 160, 255, 0.16);
  color: #2f6bff;
  font-weight: 600;
}

.qxai-ms-check {
  width: 14px;
  flex-shrink: 0;
  color: #3f8cff;
  font-size: 12px;
  text-align: center;
}

.qxai-ms-name {
  flex: 1;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.qxai-ms-badge {
  flex-shrink: 0;
  font-size: 12px;
  color: #9aa6b8;
  font-variant-numeric: tabular-nums;
}

.qxai-ms-option.selected .qxai-ms-badge {
  color: #6f9be0;
}

.qxai-ms-pop-enter-active,
.qxai-ms-pop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.qxai-ms-pop-enter-from,
.qxai-ms-pop-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
