<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

const props = defineProps({
  tool: {
    type: Object,
    required: true,
  },
});

const difficulty = ref("normal");
const difficultyOpen = ref(false);
const status = ref("");
const STORAGE_PREFIX = "tw-mini-game";
const difficulties = [
  { value: "easy", label: "简单" },
  { value: "normal", label: "普通" },
  { value: "hard", label: "困难" },
];

const gameTitle = computed(() => props.tool.name || "本地小游戏");
const storageKey = computed(() => `${STORAGE_PREFIX}-${props.tool.slug}-v1`);
const gameKind = computed(() => {
  if (props.tool.slug === "game-2048") return "2048";
  if (props.tool.slug === "snake-game") return "snake";
  if (props.tool.slug === "minesweeper-game") return "minesweeper";
  if (props.tool.slug === "sokoban-game") return "sokoban";
  if (props.tool.slug === "water-sort-game") return "water";
  return "unknown";
});

function readSave() {
  try {
    return JSON.parse(localStorage.getItem(storageKey.value) || "null");
  } catch {
    return null;
  }
}

function writeSave(payload) {
  localStorage.setItem(storageKey.value, JSON.stringify({ ...payload, difficulty: difficulty.value }));
}

function clearSave() {
  localStorage.removeItem(storageKey.value);
}

function updateDifficulty(next) {
  difficulty.value = next;
  difficultyOpen.value = false;
  resetGame();
}

function toggleDifficultyOpen() {
  difficultyOpen.value = !difficultyOpen.value;
}

function closeDifficulty() {
  difficultyOpen.value = false;
}

// 2048
const board2048 = ref([]);
const score2048 = ref(0);
const best2048 = ref(0);
const over2048 = ref(false);

function emptyBoard2048() {
  return Array.from({ length: 4 }, () => Array(4).fill(0));
}

function spawn2048(board) {
  const empty = [];
  board.forEach((row, r) => row.forEach((value, c) => !value && empty.push([r, c])));
  if (!empty.length) return board;
  const [r, c] = empty[Math.floor(Math.random() * empty.length)];
  const fourRate = difficulty.value === "hard" ? 0.18 : difficulty.value === "easy" ? 0.05 : 0.1;
  board[r][c] = Math.random() < fourRate ? 4 : 2;
  return board;
}

function init2048(saved = null) {
  const savedBest = Number(saved?.best || 0);
  best2048.value = Math.max(best2048.value, savedBest);
  if (saved?.board?.length === 4) {
    board2048.value = saved.board;
    score2048.value = Number(saved.score || 0);
    over2048.value = Boolean(saved.over);
    return;
  }
  const board = emptyBoard2048();
  spawn2048(board);
  spawn2048(board);
  board2048.value = board;
  score2048.value = 0;
  over2048.value = false;
}

function compactLine(line) {
  const values = line.filter(Boolean);
  const merged = [];
  let gained = 0;
  for (let index = 0; index < values.length; index += 1) {
    if (values[index] === values[index + 1]) {
      const next = values[index] * 2;
      merged.push(next);
      gained += next;
      index += 1;
    } else {
      merged.push(values[index]);
    }
  }
  while (merged.length < 4) merged.push(0);
  return { line: merged, gained };
}

function canMove2048(board) {
  for (let r = 0; r < 4; r += 1) {
    for (let c = 0; c < 4; c += 1) {
      if (!board[r][c]) return true;
      if (board[r][c] === board[r]?.[c + 1] || board[r][c] === board[r + 1]?.[c]) return true;
    }
  }
  return false;
}

function move2048(direction) {
  if (gameKind.value !== "2048" || over2048.value) return;
  const before = JSON.stringify(board2048.value);
  const board = board2048.value.map((row) => [...row]);
  let gained = 0;
  for (let i = 0; i < 4; i += 1) {
    const source =
      direction === "left" || direction === "right"
        ? board[i]
        : [board[0][i], board[1][i], board[2][i], board[3][i]];
    const work = direction === "right" || direction === "down" ? [...source].reverse() : source;
    const result = compactLine(work);
    const line = direction === "right" || direction === "down" ? result.line.reverse() : result.line;
    gained += result.gained;
    for (let j = 0; j < 4; j += 1) {
      if (direction === "left" || direction === "right") board[i][j] = line[j];
      else board[j][i] = line[j];
    }
  }
  if (JSON.stringify(board) === before) return;
  spawn2048(board);
  score2048.value += gained;
  best2048.value = Math.max(best2048.value, score2048.value);
  over2048.value = !canMove2048(board);
  board2048.value = board;
  saveGame();
}

// Snake
const snake = ref([]);
const food = ref({ x: 0, y: 0 });
const snakeDirection = ref("right");
const snakeNextDirection = ref("right");
const snakeRunning = ref(false);
const snakeOver = ref(false);
const snakeScore = ref(0);
const snakeBest = ref(0);
let snakeTimer = null;

const snakeConfig = computed(() => {
  if (difficulty.value === "easy") return { size: 12, speed: 220 };
  if (difficulty.value === "hard") return { size: 18, speed: 115 };
  return { size: 15, speed: 160 };
});

function randomFood(segments) {
  const size = snakeConfig.value.size;
  const occupied = new Set(segments.map((item) => `${item.x},${item.y}`));
  const cells = [];
  for (let y = 0; y < size; y += 1) {
    for (let x = 0; x < size; x += 1) {
      if (!occupied.has(`${x},${y}`)) cells.push({ x, y });
    }
  }
  return cells[Math.floor(Math.random() * cells.length)] || { x: 0, y: 0 };
}

function initSnake(saved = null) {
  snakeBest.value = Math.max(snakeBest.value, Number(saved?.best || 0));
  if (saved?.snake?.length) {
    snake.value = saved.snake;
    food.value = saved.food || randomFood(saved.snake);
    snakeDirection.value = saved.direction || "right";
    snakeNextDirection.value = snakeDirection.value;
    snakeScore.value = Number(saved.score || 0);
    snakeOver.value = Boolean(saved.over);
    snakeRunning.value = false;
    return;
  }
  const mid = Math.floor(snakeConfig.value.size / 2);
  snake.value = [
    { x: mid, y: mid },
    { x: mid - 1, y: mid },
    { x: mid - 2, y: mid },
  ];
  food.value = randomFood(snake.value);
  snakeDirection.value = "right";
  snakeNextDirection.value = "right";
  snakeScore.value = 0;
  snakeRunning.value = false;
  snakeOver.value = false;
}

function startSnake() {
  if (gameKind.value !== "snake" || snakeOver.value) return;
  snakeRunning.value = true;
  restartSnakeTimer();
}

function pauseSnake() {
  snakeRunning.value = false;
  if (snakeTimer) clearInterval(snakeTimer);
  snakeTimer = null;
  saveGame();
}

function restartSnakeTimer() {
  if (snakeTimer) clearInterval(snakeTimer);
  snakeTimer = setInterval(tickSnake, snakeConfig.value.speed);
}

function setSnakeDirection(direction) {
  const opposite = { up: "down", down: "up", left: "right", right: "left" };
  if (opposite[direction] !== snakeDirection.value) {
    snakeNextDirection.value = direction;
  }
}

function tickSnake() {
  if (!snakeRunning.value || snakeOver.value) return;
  snakeDirection.value = snakeNextDirection.value;
  const head = snake.value[0];
  const delta = {
    up: { x: 0, y: -1 },
    down: { x: 0, y: 1 },
    left: { x: -1, y: 0 },
    right: { x: 1, y: 0 },
  }[snakeDirection.value];
  const next = { x: head.x + delta.x, y: head.y + delta.y };
  const size = snakeConfig.value.size;
  const hitWall = next.x < 0 || next.y < 0 || next.x >= size || next.y >= size;
  const hitSelf = snake.value.some((item) => item.x === next.x && item.y === next.y);
  if (hitWall || hitSelf) {
    snakeOver.value = true;
    snakeRunning.value = false;
    if (snakeTimer) clearInterval(snakeTimer);
    snakeTimer = null;
    saveGame();
    return;
  }
  const nextSnake = [next, ...snake.value];
  if (next.x === food.value.x && next.y === food.value.y) {
    snakeScore.value += 10;
    snakeBest.value = Math.max(snakeBest.value, snakeScore.value);
    food.value = randomFood(nextSnake);
  } else {
    nextSnake.pop();
  }
  snake.value = nextSnake;
  saveGame();
}

// Minesweeper
const mineCells = ref([]);
const mineStatus = ref("playing");
const mineFirstClick = ref(true);

const mineConfig = computed(() => {
  if (difficulty.value === "easy") return { rows: 8, cols: 8, mines: 10 };
  if (difficulty.value === "hard") return { rows: 12, cols: 12, mines: 28 };
  return { rows: 10, cols: 10, mines: 16 };
});

function createMineBoard(seedIndex = -1) {
  const { rows, cols, mines } = mineConfig.value;
  const total = rows * cols;
  const mineSet = new Set();
  while (mineSet.size < mines) {
    const index = Math.floor(Math.random() * total);
    if (index !== seedIndex) mineSet.add(index);
  }
  const cells = Array.from({ length: total }, (_, index) => ({
    index,
    mine: mineSet.has(index),
    open: false,
    flag: false,
    count: 0,
  }));
  cells.forEach((cell) => {
    cell.count = neighbors(cell.index, rows, cols).filter((idx) => cells[idx].mine).length;
  });
  return cells;
}

function neighbors(index, rows, cols) {
  const r = Math.floor(index / cols);
  const c = index % cols;
  const result = [];
  for (let dr = -1; dr <= 1; dr += 1) {
    for (let dc = -1; dc <= 1; dc += 1) {
      if (!dr && !dc) continue;
      const nr = r + dr;
      const nc = c + dc;
      if (nr >= 0 && nc >= 0 && nr < rows && nc < cols) result.push(nr * cols + nc);
    }
  }
  return result;
}

function initMinesweeper(saved = null) {
  if (saved?.cells?.length) {
    mineCells.value = saved.cells;
    mineStatus.value = saved.status || "playing";
    mineFirstClick.value = Boolean(saved.firstClick);
    return;
  }
  mineCells.value = createMineBoard();
  mineStatus.value = "playing";
  mineFirstClick.value = true;
}

function openMine(index) {
  if (gameKind.value !== "minesweeper" || mineStatus.value !== "playing") return;
  if (mineFirstClick.value) {
    mineCells.value = createMineBoard(index);
    mineFirstClick.value = false;
  }
  const cells = mineCells.value.map((cell) => ({ ...cell }));
  const target = cells[index];
  if (!target || target.flag || target.open) return;
  if (target.mine) {
    target.open = true;
    cells.forEach((cell) => {
      if (cell.mine) cell.open = true;
    });
    mineCells.value = cells;
    mineStatus.value = "lost";
    saveGame();
    return;
  }
  const queue = [index];
  while (queue.length) {
    const current = cells[queue.shift()];
    if (!current || current.open || current.flag) continue;
    current.open = true;
    if (!current.count) {
      neighbors(current.index, mineConfig.value.rows, mineConfig.value.cols).forEach((idx) => {
        if (!cells[idx].open && !cells[idx].mine) queue.push(idx);
      });
    }
  }
  mineCells.value = cells;
  if (cells.filter((cell) => !cell.mine).every((cell) => cell.open)) {
    mineStatus.value = "won";
  }
  saveGame();
}

function toggleMineFlag(index, event) {
  event?.preventDefault();
  if (gameKind.value !== "minesweeper" || mineStatus.value !== "playing") return;
  const cells = mineCells.value.map((cell) => ({ ...cell }));
  if (!cells[index].open) cells[index].flag = !cells[index].flag;
  mineCells.value = cells;
  saveGame();
}

// Sokoban
const sokobanLevel = ref(null);
const sokobanMoves = ref(0);

const sokobanMaps = {
  easy: ["#####", "#@$.#", "#####"],
  normal: ["#######", "#.. . #", "# #$# #", "# @ $ #", "#   . #", "#######"],
  hard: ["########", "#  .   #", "# $$#  #", "#  # . #", "# @    #", "########"],
};

function parseSokoban(mapRows) {
  const walls = new Set();
  const goals = new Set();
  const boxes = [];
  let player = { x: 1, y: 1 };
  mapRows.forEach((row, y) => {
    [...row].forEach((char, x) => {
      if (char === "#") walls.add(`${x},${y}`);
      if (char === "." || char === "*" || char === "+") goals.add(`${x},${y}`);
      if (char === "$" || char === "*") boxes.push({ x, y });
      if (char === "@" || char === "+") player = { x, y };
    });
  });
  return { rows: mapRows, walls: [...walls], goals: [...goals], boxes, player, won: false };
}

function initSokoban(saved = null) {
  if (saved?.level?.rows) {
    sokobanLevel.value = saved.level;
    sokobanMoves.value = Number(saved.moves || 0);
    return;
  }
  sokobanLevel.value = parseSokoban(sokobanMaps[difficulty.value]);
  sokobanMoves.value = 0;
}

function sokobanCell(x, y) {
  const level = sokobanLevel.value;
  if (!level) return "";
  const key = `${x},${y}`;
  const hasBox = level.boxes.some((box) => box.x === x && box.y === y);
  if (level.player.x === x && level.player.y === y) return "player";
  if (hasBox && level.goals.includes(key)) return "box goal-box";
  if (hasBox) return "box";
  if (level.walls.includes(key)) return "wall";
  if (level.goals.includes(key)) return "goal";
  return "floor";
}

function moveSokoban(direction) {
  if (gameKind.value !== "sokoban" || sokobanLevel.value?.won) return;
  const delta = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] }[direction];
  const level = JSON.parse(JSON.stringify(sokobanLevel.value));
  const next = { x: level.player.x + delta[0], y: level.player.y + delta[1] };
  const nextKey = `${next.x},${next.y}`;
  if (level.walls.includes(nextKey)) return;
  const boxIndex = level.boxes.findIndex((box) => box.x === next.x && box.y === next.y);
  if (boxIndex >= 0) {
    const pushed = { x: next.x + delta[0], y: next.y + delta[1] };
    const pushedKey = `${pushed.x},${pushed.y}`;
    if (level.walls.includes(pushedKey) || level.boxes.some((box) => box.x === pushed.x && box.y === pushed.y)) return;
    level.boxes[boxIndex] = pushed;
  }
  level.player = next;
  level.won = level.boxes.every((box) => level.goals.includes(`${box.x},${box.y}`));
  sokobanLevel.value = level;
  sokobanMoves.value += 1;
  saveGame();
}

// Water sort
const bottles = ref([]);
const selectedBottle = ref(null);
const waterWon = computed(() =>
  bottles.value.every((bottle) => !bottle.length || (bottle.length === 4 && bottle.every((color) => color === bottle[0]))),
);

const waterLevels = {
  easy: [
    ["red", "blue", "red", "blue"],
    ["blue", "red", "blue", "red"],
    [],
  ],
  normal: [
    ["red", "blue", "green", "red"],
    ["green", "red", "blue", "green"],
    ["blue", "green", "red", "blue"],
    [],
    [],
  ],
  hard: [
    ["red", "blue", "green", "yellow"],
    ["yellow", "red", "blue", "green"],
    ["green", "yellow", "red", "blue"],
    ["blue", "green", "yellow", "red"],
    [],
    [],
  ],
};

function initWater(saved = null) {
  bottles.value = saved?.bottles?.length ? saved.bottles : JSON.parse(JSON.stringify(waterLevels[difficulty.value]));
  selectedBottle.value = null;
}

function topColor(bottle) {
  return bottle[bottle.length - 1];
}

function pourWater(fromIndex, toIndex) {
  if (fromIndex === toIndex) return false;
  const next = bottles.value.map((bottle) => [...bottle]);
  const from = next[fromIndex];
  const to = next[toIndex];
  if (!from?.length || !to || to.length >= 4) return false;
  const color = topColor(from);
  if (to.length && topColor(to) !== color) return false;
  while (from.length && topColor(from) === color && to.length < 4) {
    to.push(from.pop());
  }
  bottles.value = next;
  saveGame();
  return true;
}

function clickBottle(index) {
  if (gameKind.value !== "water" || waterWon.value) return;
  if (selectedBottle.value === null) {
    if (bottles.value[index]?.length) selectedBottle.value = index;
    return;
  }
  if (!pourWater(selectedBottle.value, index) && bottles.value[index]?.length) {
    selectedBottle.value = index;
    return;
  }
  selectedBottle.value = null;
}

function saveGame() {
  const payload = { kind: gameKind.value };
  if (gameKind.value === "2048") Object.assign(payload, { board: board2048.value, score: score2048.value, best: best2048.value, over: over2048.value });
  if (gameKind.value === "snake") Object.assign(payload, { snake: snake.value, food: food.value, direction: snakeDirection.value, score: snakeScore.value, best: snakeBest.value, over: snakeOver.value });
  if (gameKind.value === "minesweeper") Object.assign(payload, { cells: mineCells.value, status: mineStatus.value, firstClick: mineFirstClick.value });
  if (gameKind.value === "sokoban") Object.assign(payload, { level: sokobanLevel.value, moves: sokobanMoves.value });
  if (gameKind.value === "water") Object.assign(payload, { bottles: bottles.value });
  writeSave(payload);
}

function resetGame() {
  pauseSnake();
  clearSave();
  initGame();
  saveGame();
}

function initGame() {
  const saved = readSave();
  if (saved?.difficulty) difficulty.value = saved.difficulty;
  if (gameKind.value === "2048") init2048(saved);
  if (gameKind.value === "snake") initSnake(saved);
  if (gameKind.value === "minesweeper") initMinesweeper(saved);
  if (gameKind.value === "sokoban") initSokoban(saved);
  if (gameKind.value === "water") initWater(saved);
}

function handleGameDirection(direction) {
  if (gameKind.value === "2048") move2048(direction);

  if (gameKind.value === "snake") {
    setSnakeDirection(direction);
    startSnake();
  }

  if (gameKind.value === "sokoban") moveSokoban(direction);
}

function handleKey(event) {
  const keyMap = {
    ArrowUp: "up",
    ArrowDown: "down",
    ArrowLeft: "left",
    ArrowRight: "right",
    w: "up",
    s: "down",
    a: "left",
    d: "right",
  };

  const direction = keyMap[event.key];
  if (!direction) return;

  event.preventDefault();
  handleGameDirection(direction);
}

function board2048Class(value) {
  return `tile tile-${value || 0}`;
}

onMounted(() => {
  initGame();
  window.addEventListener("keydown", handleKey);
  window.addEventListener("click", closeDifficulty);
});

onBeforeUnmount(() => {
  window.removeEventListener("keydown", handleKey);
  window.removeEventListener("click", closeDifficulty);
  pauseSnake();
});

watch(difficulty, () => {
  status.value = "";
});
</script>

<template>
  <section class="tool-form mini-game-shell">
    <div class="mini-game-head">
      <div>
        <span class="mini-game-kicker">本地进度自动保存</span>
        <h3>{{ gameTitle }}</h3>
      </div>
      <div class="mini-game-difficulty" @click.stop>
        <span>难度</span>
        <button type="button" class="mini-game-select-button" :class="{ open: difficultyOpen }" @click="toggleDifficultyOpen">
          {{ difficulties.find((item) => item.value === difficulty)?.label || "普通" }}
        </button>
        <div v-if="difficultyOpen" class="mini-game-select-menu">
          <button
            v-for="item in difficulties"
            :key="item.value"
            type="button"
            :class="{ active: item.value === difficulty }"
            @click="updateDifficulty(item.value)"
          >
            <span>{{ item.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="gameKind === '2048'" class="mini-game-board-wrap">
      <div class="mini-game-score-row">
        <span>分数：{{ score2048 }}</span>
        <span>最高：{{ best2048 }}</span>
        <strong v-if="over2048">无可移动方块</strong>
      </div>
      <div class="game-2048-board">
        <button v-for="(value, index) in board2048.flat()" :key="index" type="button" :class="board2048Class(value)">
          {{ value || "" }}
        </button>
      </div>
      <div class="mini-game-pad mini-game-pad-with-dpad">
        <div class="mini-game-dpad" aria-label="方向控制">
          <button type="button" class="mini-game-dpad-button mini-game-dpad-up" aria-label="向上" @click="handleGameDirection('up')">
            ▲
          </button>
          <button type="button" class="mini-game-dpad-button mini-game-dpad-left" aria-label="向左" @click="handleGameDirection('left')">
            ◀
          </button>
          <div class="mini-game-dpad-center" aria-hidden="true"></div>
          <button type="button" class="mini-game-dpad-button mini-game-dpad-right" aria-label="向右" @click="handleGameDirection('right')">
            ▶
          </button>
          <button type="button" class="mini-game-dpad-button mini-game-dpad-down" aria-label="向下" @click="handleGameDirection('down')">
            ▼
          </button>
        </div>
        <button type="button" class="mini-game-action-button" @click="resetGame">重开</button>
      </div>
    </div>

    <div v-else-if="gameKind === 'snake'" class="mini-game-board-wrap">
      <div class="mini-game-score-row">
        <span>分数：{{ snakeScore }}</span>
        <span>最高：{{ snakeBest }}</span>
        <strong v-if="snakeOver">游戏结束</strong>
      </div>
      <div class="snake-board" :style="{ gridTemplateColumns: `repeat(${snakeConfig.size}, 1fr)` }">
        <span
          v-for="index in snakeConfig.size * snakeConfig.size"
          :key="index"
          :class="{
            snake: snake.some((item) => item.x === (index - 1) % snakeConfig.size && item.y === Math.floor((index - 1) / snakeConfig.size)),
            food: food.x === (index - 1) % snakeConfig.size && food.y === Math.floor((index - 1) / snakeConfig.size),
          }"
        ></span>
      </div>
      <div class="mini-game-pad mini-game-pad-with-dpad">
        <div class="mini-game-dpad" aria-label="方向控制">
          <button type="button" class="mini-game-dpad-button mini-game-dpad-up" aria-label="向上" @click="setSnakeDirection('up'); startSnake()">
            ▲
          </button>
          <button type="button" class="mini-game-dpad-button mini-game-dpad-left" aria-label="向左" @click="setSnakeDirection('left'); startSnake()">
            ◀
          </button>
          <div class="mini-game-dpad-center" aria-hidden="true"></div>
          <button type="button" class="mini-game-dpad-button mini-game-dpad-right" aria-label="向右" @click="setSnakeDirection('right'); startSnake()">
            ▶
          </button>
          <button type="button" class="mini-game-dpad-button mini-game-dpad-down" aria-label="向下" @click="setSnakeDirection('down'); startSnake()">
            ▼
          </button>
        </div>
        <button type="button" class="mini-game-action-button" @click="snakeRunning ? pauseSnake() : startSnake()">{{ snakeRunning ? "暂停" : "开始" }}</button>
        <button type="button" class="mini-game-action-button" @click="resetGame">重开</button>
      </div>
    </div>

    <div v-else-if="gameKind === 'minesweeper'" class="mini-game-board-wrap">
      <div class="mini-game-score-row">
        <span>地雷：{{ mineConfig.mines }}</span>
        <span>标记：{{ mineCells.filter((cell) => cell.flag).length }}</span>
        <strong v-if="mineStatus === 'won'">已完成</strong>
        <strong v-if="mineStatus === 'lost'">踩到地雷</strong>
      </div>
      <div class="minesweeper-board" :style="{ gridTemplateColumns: `repeat(${mineConfig.cols}, 1fr)` }">
        <button
          v-for="cell in mineCells"
          :key="cell.index"
          type="button"
          :class="{ open: cell.open, flag: cell.flag, mine: cell.open && cell.mine }"
          @click="openMine(cell.index)"
          @contextmenu="toggleMineFlag(cell.index, $event)"
        >
          {{ cell.open ? (cell.mine ? "＊" : cell.count || "") : cell.flag ? "旗" : "" }}
        </button>
      </div>
      <div class="mini-game-pad">
        <button @click="resetGame">重开</button>
      </div>
    </div>

    <div v-else-if="gameKind === 'sokoban'" class="mini-game-board-wrap">
      <div class="mini-game-score-row">
        <span>步数：{{ sokobanMoves }}</span>
        <strong v-if="sokobanLevel?.won">已完成</strong>
      </div>
      <div class="sokoban-board" :style="{ gridTemplateColumns: `repeat(${sokobanLevel?.rows?.[0]?.length || 1}, 1fr)` }">
        <span v-for="(_, index) in (sokobanLevel?.rows?.length || 0) * (sokobanLevel?.rows?.[0]?.length || 0)" :key="index" :class="sokobanCell(index % sokobanLevel.rows[0].length, Math.floor(index / sokobanLevel.rows[0].length))"></span>
      </div>
      <div class="mini-game-pad mini-game-pad-with-dpad">
        <div class="mini-game-dpad" aria-label="方向控制">
          <button type="button" class="mini-game-dpad-button mini-game-dpad-up" aria-label="向上" @click="handleGameDirection('up')">
            ▲
          </button>
          <button type="button" class="mini-game-dpad-button mini-game-dpad-left" aria-label="向左" @click="handleGameDirection('left')">
            ◀
          </button>
          <div class="mini-game-dpad-center" aria-hidden="true"></div>
          <button type="button" class="mini-game-dpad-button mini-game-dpad-right" aria-label="向右" @click="handleGameDirection('right')">
            ▶
          </button>
          <button type="button" class="mini-game-dpad-button mini-game-dpad-down" aria-label="向下" @click="handleGameDirection('down')">
            ▼
          </button>
        </div>
        <button type="button" class="mini-game-action-button" @click="resetGame">重开</button>
      </div>
    </div>

    <div v-else-if="gameKind === 'water'" class="mini-game-board-wrap">
      <div class="mini-game-score-row">
        <span>点击瓶子选择来源和目标</span>
        <strong v-if="waterWon">已完成</strong>
      </div>
      <div class="water-sort-board">
        <button v-for="(bottle, index) in bottles" :key="index" type="button" class="water-bottle" :class="{ selected: selectedBottle === index }" @click="clickBottle(index)">
          <span v-for="slot in 4" :key="slot" :class="['water-layer', bottle[4 - slot] || 'empty']"></span>
        </button>
      </div>
      <div class="mini-game-pad">
        <button @click="selectedBottle = null">取消选择</button>
        <button @click="resetGame">重开</button>
      </div>
    </div>
  </section>
</template>
