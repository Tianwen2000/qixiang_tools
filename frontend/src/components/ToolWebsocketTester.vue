<script setup>
import { onBeforeUnmount, reactive, ref } from "vue";

import { showToast, updateToast } from "../utils/toast.js";

const form = reactive({
  url: "",
  message: "",
});

const status = ref("未连接");
const socket = ref(null);
const logs = ref([]);
let connectToastId = "";

function appendLog(type, content) {
  logs.value.unshift({
    id: `${Date.now()}-${Math.random()}`,
    type,
    content,
    time: new Date().toLocaleTimeString(),
  });
}

function getLogTypeLabel(type) {
  const labelMap = {
    system: "系统",
    receive: "接收",
    send: "发送",
    error: "错误",
  };
  return labelMap[type] || "消息";
}

function disconnect() {
  if (socket.value) {
    socket.value.close();
    socket.value = null;
  }
  status.value = "未连接";
}

function connect() {
  if (!form.url.trim()) {
    showToast({
      type: "error",
      title: "连接失败",
      message: "请输入 WebSocket 地址",
      duration: 3200,
    });
    return;
  }

  disconnect();
  status.value = "连接中";
  connectToastId = showToast({
    type: "loading",
    title: "正在建立连接",
    message: form.url,
    duration: 0,
  });

  try {
    const ws = new WebSocket(form.url);
    socket.value = ws;

    ws.addEventListener("open", () => {
      status.value = "已连接";
      appendLog("system", `已连接到 ${form.url}`);
      updateToast(connectToastId, {
        type: "success",
        title: "连接成功",
        message: `已连接到 ${form.url}`,
        duration: 2400,
      });
    });

    ws.addEventListener("message", (event) => {
      appendLog("receive", String(event.data));
    });

    ws.addEventListener("error", () => {
      appendLog("error", "连接过程中发生错误");
      updateToast(connectToastId, {
        type: "error",
        title: "连接失败",
        message: "请检查地址是否可达，或是否被浏览器策略拦截",
        duration: 3600,
      });
    });

    ws.addEventListener("close", () => {
      status.value = "已断开";
      appendLog("system", "连接已关闭");
      socket.value = null;
      connectToastId = "";
    });
  } catch (err) {
    status.value = "未连接";
    updateToast(connectToastId, {
      type: "error",
      title: "连接失败",
      message: err.message || "无法建立连接",
      duration: 3600,
    });
  }
}

function sendMessage() {
  if (!socket.value || socket.value.readyState !== WebSocket.OPEN) {
    showToast({
      type: "error",
      title: "发送失败",
      message: "请先建立连接",
      duration: 3200,
    });
    return;
  }
  socket.value.send(form.message);
  appendLog("send", form.message || "(空消息)");
  form.message = "";
  showToast({
    type: "success",
    title: "消息已发送",
    message: "已写入消息日志。",
    duration: 1800,
  });
}

onBeforeUnmount(() => {
  disconnect();
});

function clearOutput() {
  logs.value = [];
}
</script>

<template>
  <section class="tool-form local-tool-panel">
    <div class="local-tool-header">
      <h3>WebSocket 接口测试</h3>
      <p>直接在浏览器中建立 WebSocket 连接，适合调试消息推送、聊天室和实时接口。</p>
    </div>

    <div class="tester-grid">
      <label>
        <span>连接地址</span>
        <input v-model="form.url" type="text" placeholder="wss://echo.websocket.events" />
      </label>
      <label>
        <span>当前状态</span>
        <div class="status-chip">{{ status }}</div>
      </label>
    </div>

    <div class="tool-actions">
      <button type="button" @click="connect">建立连接</button>
      <button type="button" class="secondary-button" @click="disconnect">断开连接</button>
    </div>

    <label class="tester-block">
      <span>发送消息</span>
      <textarea v-model="form.message" rows="6" placeholder="请输入要发送的消息"></textarea>
    </label>

    <div class="tool-actions">
      <button type="button" :disabled="status !== '已连接'" @click="sendMessage">发送消息</button>
    </div>

    <section class="result-panel">
      <div class="result-panel-head">
        <h3>消息日志</h3>
        <div class="result-actions">
          <button type="button" class="secondary-button" @click="clearOutput">清空输出</button>
        </div>
      </div>
      <div v-if="logs.length" class="socket-log-list">
        <article v-for="item in logs" :key="item.id" class="socket-log-item" :data-kind="item.type">
          <div class="socket-log-meta">
            <strong>{{ getLogTypeLabel(item.type) }}</strong>
            <span>{{ item.time }}</span>
          </div>
          <pre>{{ item.content }}</pre>
        </article>
      </div>
      <p v-else class="empty-hint">暂时还没有消息记录。</p>
    </section>
  </section>
</template>
