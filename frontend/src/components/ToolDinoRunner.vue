<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const BEST_SCORE_KEY = "tw-dino-runner-best-score-v1";
const INK = "#535353";
const SOFT_INK = "#8b8b8b";
const PAPER = "#ffffff";

const RUNNER_SPRITES = {
  stand: [
    "....######......",
    "...########.....",
    "...###..####....",
    "...###..####....",
    "...########.....",
    "...#######......",
    "...#####........",
    "...######.......",
    "...#######......",
    ".############...",
    "###########.....",
    "#########.......",
    "..########......",
    "..###..###......",
    ".##....###......",
    "##.....####.....",
  ],
  runA: [
    "....######......",
    "...########.....",
    "...###..####....",
    "...###..####....",
    "...########.....",
    "...#######......",
    "...#####........",
    "...######.......",
    "...#######......",
    ".############...",
    "###########.....",
    "#########.......",
    "..########......",
    "..###..###......",
    ".##.....##......",
    "##......####....",
  ],
  runB: [
    "....######......",
    "...########.....",
    "...###..####....",
    "...###..####....",
    "...########.....",
    "...#######......",
    "...#####........",
    "...######.......",
    "...#######......",
    ".############...",
    "###########.....",
    "#########.......",
    "..########......",
    "..###..###......",
    "..##...####.....",
    ".##......##.....",
  ],
  duckA: [
    "...##########........",
    "..############.......",
    "..###..########......",
    "..###############....",
    "##################...",
    "################.....",
    "...##############....",
    "..###......#####.....",
    ".##........####......",
    "##.........#####.....",
  ],
  duckB: [
    "...##########........",
    "..############.......",
    "..###..########......",
    "..###############....",
    "##################...",
    "################.....",
    "...##############....",
    "..###......#####.....",
    "..##.......####......",
    ".##........#####.....",
  ],
  dead: [
    "....######......",
    "...########.....",
    "...###..####....",
    "...###..####....",
    "...########.....",
    "...#######......",
    "...#####........",
    "...######.......",
    "...#######......",
    ".############...",
    "###########.....",
    "#########.......",
    "..########......",
    "..###..###......",
    ".##....###......",
    "##.....####.....",
  ],
};

const CACTUS_SPRITES = {
  single: [
    "...##...",
    "...##...",
    "...##...",
    "..###...",
    "..###...",
    "..###...",
    "..####..",
    "..####..",
    "..####..",
    "..####..",
    "..####..",
    ".######.",
    ".######.",
    ".######.",
    ".######.",
    "########",
  ],
  tall: [
    "....##....",
    "....##....",
    "....##....",
    "....##....",
    "...###....",
    "...###....",
    "...###....",
    "..####....",
    "..####....",
    "..####....",
    "..######..",
    "..######..",
    "..######..",
    "..######..",
    ".########.",
    ".########.",
    ".########.",
    ".########.",
    "##########",
    "##########",
  ],
  double: [
    "...##......##.....",
    "...##......##.....",
    "...##......##.....",
    "..###.....###.....",
    "..###.....###.....",
    "..###.....###.....",
    "..####....####....",
    "..####....####....",
    "..####....####....",
    ".#####....#####...",
    ".#####....#####...",
    ".#####....#####...",
    ".#####....#####...",
    "######....######..",
    "######....######..",
    "######....######..",
    "##################",
    "##################",
  ],
};

const BIRD_SPRITES = {
  up: [
    "......##.......",
    ".....####......",
    ".############..",
    "##############.",
    ".....######....",
    "....##..####...",
    "...##.....###..",
    "..........###..",
  ],
  down: [
    "......##.......",
    ".....####......",
    ".############..",
    "##############.",
    "...##....##....",
    "..##......##...",
    ".##........##..",
    "...........###.",
  ],
};

const CLOUD_SPRITE = [
  "...####....####.....",
  ".######..########...",
  "##################..",
  "####################",
  "..################..",
  ".....##########.....",
];

const RESTART_SPRITE = [
  "....####........",
  "...######.......",
  "..##....##......",
  "..##..######....",
  "..##..######....",
  "..##....##.##...",
  "..##....##..##..",
  "..##....##..##..",
  "..##....##..##..",
  "...######..##...",
  "....####..##....",
  "..........##....",
];

const canvasRef = ref(null);
const score = ref(0);
const bestScore = ref(0);
const running = ref(false);
const crashed = ref(false);
const started = ref(false);
const duckPressed = ref(false);

const stage = reactive({
  width: 0,
  height: 0,
  groundY: 0,
  pixelScale: 3,
});

const runner = reactive({
  x: 56,
  y: 0,
  width: 0,
  height: 0,
  velocityY: 0,
});

const physics = reactive({
  speed: 420,
  gravity: 2280,
  jumpVelocity: -800,
  obstacleTimer: 0,
  cloudTimer: 0,
  elapsed: 0,
});

const obstacles = ref([]);
const clouds = ref([]);

let context = null;
let frameHandle = 0;
let lastTimestamp = 0;
let obstacleSeed = 0;

const statusTitle = computed(() => {
  if (crashed.value) {
    return "按空格键重新开始游戏";
  }
  if (!started.value) {
    return "按空格键即可开始游戏";
  }
  if (!running.value) {
    return "游戏已暂停";
  }
  return "空格跳跃，方向下键下蹲";
});

const statusDescription = computed(() => {
  if (crashed.value) {
    return "撞上障碍后会显示 GAME OVER。点击画布、按空格，或点“重新开始”都能立即再来一局。";
  }
  if (!started.value) {
    return "这版改成了更接近 Chrome 断网小游戏的黑白像素风，所有逻辑都在浏览器本地运行。";
  }
  if (!running.value) {
    return "点“继续游戏”或直接按空格，就能回到赛道继续挑战。";
  }
  return "分数和历史最高分会显示在右上角，速度会随着时间逐渐提升。";
});

const tips = computed(() => {
  if (crashed.value) {
    return ["空格 / 点击画布：立即重开", "↓：落地后可下蹲", "所有数据只保存在当前浏览器"];
  }
  return ["空格 / ↑：跳跃", "↓：下蹲闪避飞鸟", "纯前端本地版，不占用后端资源"];
});

const mainButtonLabel = computed(() => {
  if (!started.value) {
    return "开始游戏";
  }
  if (crashed.value) {
    return "重新开始";
  }
  return running.value ? "暂停游戏" : "继续游戏";
});

function handleMainButton() {
  if (!started.value) {
    beginRun();
    return;
  }

  if (crashed.value) {
    restartGame();
    return;
  }

  running.value = !running.value;
}

function getSpriteSize(sprite, scale = stage.pixelScale) {
  return {
    width: sprite[0].length * scale,
    height: sprite.length * scale,
  };
}

function getRunnerSprite(timestamp = 0) {
  if (crashed.value) {
    return RUNNER_SPRITES.dead;
  }
  if (duckPressed.value && isRunnerGrounded()) {
    return Math.floor(timestamp / 120) % 2 === 0 ? RUNNER_SPRITES.duckA : RUNNER_SPRITES.duckB;
  }
  if (running.value && isRunnerGrounded()) {
    return Math.floor(timestamp / 120) % 2 === 0 ? RUNNER_SPRITES.runA : RUNNER_SPRITES.runB;
  }
  return RUNNER_SPRITES.stand;
}

function getBirdSprite(timestamp = 0) {
  return Math.floor(timestamp / 140) % 2 === 0 ? BIRD_SPRITES.up : BIRD_SPRITES.down;
}

function formatScore(value) {
  return Math.max(0, Math.floor(value)).toString().padStart(5, "0");
}

function readBestScore() {
  if (typeof window === "undefined") {
    return 0;
  }
  const raw = window.localStorage.getItem(BEST_SCORE_KEY);
  const parsed = Number(raw || 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function saveBestScore(nextScore) {
  bestScore.value = Math.max(bestScore.value, Math.floor(nextScore));
  if (typeof window !== "undefined") {
    window.localStorage.setItem(BEST_SCORE_KEY, String(bestScore.value));
  }
}

function resetRunner() {
  const { width, height } = getSpriteSize(RUNNER_SPRITES.stand);
  runner.width = width;
  runner.height = height;
  runner.velocityY = 0;
  runner.y = stage.groundY - runner.height;
}

function configureCanvas() {
  const canvas = canvasRef.value;
  if (!canvas) {
    return;
  }
  const wrapper = canvas.parentElement;
  const width = Math.max(320, wrapper?.clientWidth || 920);
  const height = width < 560 ? 220 : 250;
  const ratio = window.devicePixelRatio || 1;

  stage.width = width;
  stage.height = height;
  stage.pixelScale = width < 460 ? 2 : 3;
  stage.groundY = height - 54;

  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;

  context = canvas.getContext("2d");
  if (!context) {
    return;
  }

  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.imageSmoothingEnabled = false;
  context.textBaseline = "top";

  resetRunner();
  drawScene(lastTimestamp || performance.now());
}

function seedClouds() {
  clouds.value = [
    { x: stage.width * 0.34, y: 36, scale: 1 },
    { x: stage.width * 0.68, y: 54, scale: 1.25 },
  ];
}

function resetGameState() {
  score.value = 0;
  running.value = false;
  crashed.value = false;
  started.value = false;
  duckPressed.value = false;
  physics.speed = 420;
  physics.obstacleTimer = 1.6 + Math.random() * 0.3;
  physics.cloudTimer = 1.8;
  physics.elapsed = 0;
  obstacles.value = [];
  seedClouds();
  resetRunner();
}

function beginRun() {
  if (running.value || crashed.value) {
    return;
  }
  started.value = true;
  running.value = true;
}

function isRunnerGrounded() {
  return runner.y >= stage.groundY - runner.height - 0.5;
}

function triggerJump() {
  if (crashed.value) {
    restartGame();
    return;
  }

  if (!started.value || !running.value) {
    beginRun();
  }

  if (!isRunnerGrounded()) {
    return;
  }

  runner.velocityY = physics.jumpVelocity;
}

function setDuckState(nextValue) {
  if (crashed.value || !started.value) {
    duckPressed.value = false;
    return;
  }
  duckPressed.value = nextValue;
}

function restartGame() {
  resetGameState();
  beginRun();
}

function randomRange(min, max) {
  return min + Math.random() * (max - min);
}

function spawnCloud() {
  const scales = [0.85, 1, 1.25];
  clouds.value.push({
    x: stage.width + randomRange(30, 120),
    y: randomRange(24, 68),
    scale: scales[Math.floor(Math.random() * scales.length)],
  });
}

function spawnObstacle() {
  const allowBird = score.value > 180;
  const shouldSpawnBird = allowBird && Math.random() < 0.24;

  if (shouldSpawnBird) {
    const sprite = BIRD_SPRITES.down;
    const { width, height } = getSpriteSize(sprite);
    const clearance = Math.random() < 0.5 ? 24 : 54;
    obstacles.value.push({
      id: obstacleSeed++,
      kind: "bird",
      x: stage.width + randomRange(20, 56),
      y: stage.groundY - height - clearance,
      width,
      height,
    });
    return;
  }

  const styles = ["single", "tall", "double"];
  const style = styles[Math.floor(Math.random() * styles.length)];
  const sprite = CACTUS_SPRITES[style];
  const { width, height } = getSpriteSize(sprite);
  obstacles.value.push({
    id: obstacleSeed++,
    kind: "cactus",
    style,
    x: stage.width + randomRange(10, 40),
    y: stage.groundY - height,
    width,
    height,
  });
}

function runnerHitbox() {
  const insetX = duckPressed.value && isRunnerGrounded() ? 9 : 8;
  const insetY = duckPressed.value && isRunnerGrounded() ? 4 : 6;
  return {
    x: runner.x + insetX,
    y: runner.y + insetY,
    width: runner.width - insetX * 2,
    height: runner.height - insetY - 4,
  };
}

function obstacleHitbox(obstacle) {
  if (obstacle.kind === "bird") {
    return {
      x: obstacle.x + 6,
      y: obstacle.y + 4,
      width: obstacle.width - 12,
      height: obstacle.height - 8,
    };
  }

  return {
    x: obstacle.x + 3,
    y: obstacle.y + 2,
    width: obstacle.width - 6,
    height: obstacle.height - 3,
  };
}

function overlaps(a, b) {
  return a.x < b.x + b.width && a.x + a.width > b.x && a.y < b.y + b.height && a.y + a.height > b.y;
}

function finishRun() {
  running.value = false;
  crashed.value = true;
  duckPressed.value = false;
  saveBestScore(score.value);
}

function updateRunner(dt) {
  const standing = getSpriteSize(RUNNER_SPRITES.stand);
  const ducking = getSpriteSize(RUNNER_SPRITES.duckA);
  const shouldDuck = duckPressed.value && isRunnerGrounded();
  const targetHeight = shouldDuck ? ducking.height : standing.height;
  const targetWidth = shouldDuck ? ducking.width : standing.width;

  if (runner.height !== targetHeight) {
    runner.y += runner.height - targetHeight;
    runner.height = targetHeight;
  }
  runner.width = targetWidth;

  const gravityScale = duckPressed.value && !isRunnerGrounded() ? 1.26 : 1;
  runner.velocityY += physics.gravity * gravityScale * dt;
  runner.y += runner.velocityY * dt;

  const groundLevel = stage.groundY - runner.height;
  if (runner.y >= groundLevel) {
    runner.y = groundLevel;
    runner.velocityY = 0;
  }
}

function updateClouds(dt) {
  clouds.value = clouds.value
    .map((cloud) => ({
      ...cloud,
      x: cloud.x - physics.speed * 0.08 * dt,
    }))
    .filter((cloud) => cloud.x > -120);

  physics.cloudTimer -= dt;
  if (physics.cloudTimer <= 0) {
    spawnCloud();
    physics.cloudTimer = randomRange(1.9, 3.6);
  }
}

function updateObstacles(dt) {
  obstacles.value = obstacles.value
    .map((obstacle) => ({
      ...obstacle,
      x: obstacle.x - physics.speed * dt,
    }))
    .filter((obstacle) => obstacle.x + obstacle.width > -40);

  physics.obstacleTimer -= dt;
  if (physics.obstacleTimer <= 0) {
    spawnObstacle();
    physics.obstacleTimer = Math.max(0.72, 1.18 - Math.min(score.value, 600) * 0.00045) + Math.random() * 0.38;
  }
}

function updateGame(dt) {
  if (!running.value) {
    return;
  }

  physics.elapsed += dt;
  physics.speed = Math.min(560, 360 + physics.elapsed * 6);
  score.value += dt * 12;

  updateRunner(dt);
  updateClouds(dt);
  updateObstacles(dt);

  const hitbox = runnerHitbox();
  if (obstacles.value.some((obstacle) => overlaps(hitbox, obstacleHitbox(obstacle)))) {
    finishRun();
  }

  if (Math.floor(score.value) > bestScore.value) {
    bestScore.value = Math.floor(score.value);
  }
}

function drawSprite(sprite, x, y, color = INK, scale = stage.pixelScale) {
  context.fillStyle = color;
  for (let rowIndex = 0; rowIndex < sprite.length; rowIndex += 1) {
    const row = sprite[rowIndex];
    for (let columnIndex = 0; columnIndex < row.length; columnIndex += 1) {
      if (row[columnIndex] === ".") {
        continue;
      }
      context.fillRect(
        Math.round(x + columnIndex * scale),
        Math.round(y + rowIndex * scale),
        Math.max(1, scale),
        Math.max(1, scale),
      );
    }
  }
}

function drawCloud(cloud) {
  const scale = Math.max(2, Math.round(stage.pixelScale * cloud.scale));
  drawSprite(CLOUD_SPRITE, cloud.x, cloud.y, "#c7c7c7", scale);
}

function drawGround(timestamp) {
  const trackOffset = running.value ? Math.floor((timestamp / 1000) * physics.speed) % 44 : 0;

  context.fillStyle = INK;
  context.fillRect(0, stage.groundY, stage.width, 2);

  for (let x = -trackOffset; x < stage.width + 44; x += 44) {
    context.fillRect(x + 4, stage.groundY + 9, 16, 2);
    context.fillRect(x + 24, stage.groundY + 9, 10, 2);
    context.fillRect(x + 18, stage.groundY - 1, 6, 2);
    context.fillRect(x + 22, stage.groundY - 3, 4, 2);
  }
}

function drawCactus(obstacle) {
  drawSprite(CACTUS_SPRITES[obstacle.style], obstacle.x, obstacle.y, INK);
}

function drawBird(obstacle, timestamp) {
  drawSprite(getBirdSprite(timestamp), obstacle.x, obstacle.y, INK);
}

function drawRunner(timestamp) {
  const sprite = getRunnerSprite(timestamp);
  drawSprite(sprite, runner.x, runner.y, INK);

  if (crashed.value) {
    const eyeSize = Math.max(1, stage.pixelScale - 1);
    context.strokeStyle = PAPER;
    context.lineWidth = 1.5;
    const eyeX = runner.x + stage.pixelScale * 8;
    const eyeY = runner.y + stage.pixelScale * 2;
    context.beginPath();
    context.moveTo(eyeX, eyeY);
    context.lineTo(eyeX + eyeSize * 2, eyeY + eyeSize * 2);
    context.moveTo(eyeX + eyeSize * 2, eyeY);
    context.lineTo(eyeX, eyeY + eyeSize * 2);
    context.stroke();
    return;
  }

  context.fillStyle = PAPER;
  context.fillRect(runner.x + stage.pixelScale * 8, runner.y + stage.pixelScale * 2, stage.pixelScale, stage.pixelScale);
}

function drawHud() {
  const scoreLabel = formatScore(score.value);
  const highLabel = formatScore(bestScore.value);
  const hudLabel = bestScore.value > 0 ? `HI ${highLabel} ${scoreLabel}` : scoreLabel;

  context.fillStyle = SOFT_INK;
  context.font = `700 ${Math.max(16, stage.pixelScale * 4 + 6)}px ui-monospace, SFMono-Regular, Menlo, Monaco, monospace`;
  const textWidth = context.measureText(hudLabel).width;
  context.fillText(hudLabel, stage.width - textWidth - 14, 18);
}

function drawGameOver() {
  const label = "GAME OVER";
  context.fillStyle = INK;
  context.font = `700 ${Math.max(20, stage.pixelScale * 5 + 8)}px ui-monospace, SFMono-Regular, Menlo, Monaco, monospace`;
  const textWidth = context.measureText(label).width;
  const textX = (stage.width - textWidth) / 2;
  const textY = Math.max(38, stage.groundY - 92);
  context.fillText(label, textX, textY);

  const iconScale = stage.pixelScale;
  const iconSize = getSpriteSize(RESTART_SPRITE, iconScale);
  const iconX = (stage.width - iconSize.width) / 2;
  const iconY = textY + 40;
  context.strokeStyle = SOFT_INK;
  context.lineWidth = 2;
  context.strokeRect(iconX - 10, iconY - 8, iconSize.width + 20, iconSize.height + 16);
  drawSprite(RESTART_SPRITE, iconX, iconY, INK, iconScale);
}

function drawScene(timestamp) {
  if (!context) {
    return;
  }

  context.clearRect(0, 0, stage.width, stage.height);
  context.fillStyle = PAPER;
  context.fillRect(0, 0, stage.width, stage.height);

  clouds.value.forEach(drawCloud);
  drawGround(timestamp);

  obstacles.value.forEach((obstacle) => {
    if (obstacle.kind === "bird") {
      drawBird(obstacle, timestamp);
      return;
    }
    drawCactus(obstacle);
  });

  drawRunner(timestamp);
  drawHud();

  if (crashed.value) {
    drawGameOver();
  }
}

function frame(timestamp) {
  if (!lastTimestamp) {
    lastTimestamp = timestamp;
  }
  const delta = Math.min((timestamp - lastTimestamp) / 1000, 0.032);
  lastTimestamp = timestamp;

  updateGame(delta);
  drawScene(timestamp);
  frameHandle = window.requestAnimationFrame(frame);
}

function handleResize() {
  configureCanvas();
}

function handleKeydown(event) {
  if (event.repeat && ["ArrowDown", "KeyS"].includes(event.code)) {
    return;
  }

  if (["Space", "ArrowUp", "KeyW"].includes(event.code)) {
    event.preventDefault();
    triggerJump();
    return;
  }

  if (["ArrowDown", "KeyS"].includes(event.code)) {
    event.preventDefault();
    setDuckState(true);
    return;
  }

  if (event.code === "Enter" && crashed.value) {
    event.preventDefault();
    restartGame();
  }
}

function handleKeyup(event) {
  if (["ArrowDown", "KeyS"].includes(event.code)) {
    event.preventDefault();
    setDuckState(false);
  }
}

function handleCanvasTap() {
  triggerJump();
}

function handleDuckRelease() {
  setDuckState(false);
}

onMounted(() => {
  void props.tool;
  bestScore.value = readBestScore();
  configureCanvas();
  resetGameState();
  window.addEventListener("resize", handleResize);
  window.addEventListener("keydown", handleKeydown);
  window.addEventListener("keyup", handleKeyup);
  frameHandle = window.requestAnimationFrame(frame);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
  window.removeEventListener("keydown", handleKeydown);
  window.removeEventListener("keyup", handleKeyup);
  window.cancelAnimationFrame(frameHandle);
});
</script>

<template>
  <section class="tool-form local-tool-panel dino-runner-shell">
    <div class="dino-runner-chrome">
      <div class="dino-runner-caption">
        <span class="dino-runner-badge">Dino Runner</span>
        <span>Chrome 像素风 · 本地单机版 · 不请求后端</span>
      </div>

      <div class="dino-runner-stage-wrap">
        <canvas ref="canvasRef" class="dino-runner-stage" @click="handleCanvasTap"></canvas>
      </div>

      <div class="dino-runner-readout">
        <h3>{{ statusTitle }}</h3>
        <p>{{ statusDescription }}</p>

        <div class="dino-runner-controls">
          <button
            type="button"
            class="dino-runner-button is-primary"
            :class="{ 'is-active': started && !crashed }"
            @click="handleMainButton"
          >
            {{ mainButtonLabel }}
          </button>
          <button type="button" class="dino-runner-button" @click="triggerJump">跳跃</button>
          <button
            type="button"
            class="dino-runner-button"
            :class="{ 'is-active': duckPressed }"
            @pointerdown.prevent="setDuckState(true)"
            @pointerup.prevent="handleDuckRelease"
            @pointerleave.prevent="handleDuckRelease"
            @click.prevent
          >
            下蹲
          </button>
        </div>

        <div class="dino-runner-tips">
          <span v-for="tip in tips" :key="tip">{{ tip }}</span>
        </div>

        <div class="dino-runner-footer">
          <span>HI {{ formatScore(bestScore) }}</span>
          <span>SCORE {{ formatScore(score) }}</span>
          <span>LOCAL PIXEL EDITION</span>
        </div>
      </div>
    </div>
  </section>
</template>
