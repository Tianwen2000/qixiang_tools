<script setup>
import { useToast } from "../utils/toast.js";

const { toasts, dismissToast } = useToast();

function getToastRole(type) {
  return type === "error" ? "alert" : "status";
}
</script>

<template>
  <Teleport to="body">
    <transition-group name="toast-stack" tag="div" class="toast-viewport">
      <article
        v-for="toast in toasts"
        :key="toast.id"
        class="toast-card"
        :data-type="toast.type"
        :role="getToastRole(toast.type)"
      >
        <div class="toast-card-main">
          <strong>{{ toast.title }}</strong>
          <p v-if="toast.message">{{ toast.message }}</p>
        </div>
        <button type="button" class="toast-close" @click="dismissToast(toast.id)">×</button>
      </article>
    </transition-group>
  </Teleport>
</template>
