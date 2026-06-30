<script setup>
// 文件说明：定义 SeasonalForestScene 前端组件。
import { computed } from "vue";

const props = defineProps({
  season: {
    type: String,
    default: "spring",
  },
});

const particleKinds = {
  spring: "petal",
  summer: "summer-leaf",
  autumn: "leaf",
  winter: "snow",
};

const gustKinds = {
  spring: "petal-wind",
  summer: "firefly-wind",
  autumn: "leaf-gust",
  winter: "snow-squall",
};

const seasonClass = computed(() => `forest-season-${props.season || "spring"}`);

const particles = computed(() => {
  const season = props.season || "spring";
  const kind = particleKinds[season] || particleKinds.spring;
  const count = season === "winter" ? 72 : season === "autumn" ? 58 : 52;

  return Array.from({ length: count }, (_, index) => {
    const lane = index % 9;
    const left = (index * 13 + lane * 7) % 112 - 6;
    const size = season === "winter" ? 5 + (index % 6) * 1.8 : 8 + (index % 5) * 2.8;
    const duration = season === "summer" ? 11 + (index % 7) * 1.15 : season === "winter" ? 12 + (index % 8) * 1.05 : 13 + (index % 9) * 1.15;
    const drift = (index % 2 === 0 ? 1 : -1) * (70 + lane * 18);
    const depth = index % 6 === 0 ? "near" : index % 4 === 0 ? "far" : "mid";
    const startTop = -22 - (index % 7) * 5;

    return {
      id: `${season}-forest-particle-${index + 1}`,
      kind,
      depth,
      style: {
        left: `${left}%`,
        top: `${startTop}%`,
        width: `${size}px`,
        height: `${season === "winter" ? size : Math.round(size * 1.28)}px`,
        animationDuration: `${duration.toFixed(1)}s`,
        animationDelay: `${(-1 * ((index * 1.7) % duration)).toFixed(1)}s`,
        "--forest-fall-x": `${drift}px`,
        "--forest-fall-y": `${118 + (index % 6) * 7}vh`,
        "--forest-spin": `${index % 2 === 0 ? 240 + lane * 22 : -210 - lane * 18}deg`,
        "--forest-opacity": depth === "near" ? "0.78" : depth === "far" ? "0.32" : "0.56",
        "--forest-sway-a": `${index % 2 === 0 ? 18 + lane * 4 : -18 - lane * 4}px`,
        "--forest-sway-b": `${index % 2 === 0 ? -24 - lane * 5 : 24 + lane * 5}px`,
      },
    };
  });
});

const gusts = computed(() => {
  const season = props.season || "spring";
  const kind = gustKinds[season] || gustKinds.spring;
  const count = season === "winter" ? 7 : 6;

  return Array.from({ length: count }, (_, index) => ({
    id: `${season}-forest-gust-${index + 1}`,
    kind,
    style: {
      left: `${-18 - (index % 2) * 8}%`,
      top: `${12 + index * 12}%`,
      width: `${96 + (index % 3) * 18}%`,
      height: `${season === "winter" ? 44 + (index % 3) * 8 : 34 + (index % 3) * 7}px`,
      opacity: `${0.14 + (index % 3) * 0.035}`,
      animationDuration: `${9 + (index % 4) * 1.7}s`,
      animationDelay: `${-1 * (index * 1.4)}s`,
      "--forest-gust-y": `${index % 2 === 0 ? -18 : 18}px`,
    },
  }));
});

const lights = computed(() => {
  const season = props.season || "spring";
  if (!["summer", "winter", "spring"].includes(season)) {
    return [];
  }
  const count = season === "summer" ? 30 : season === "winter" ? 22 : 18;

  return Array.from({ length: count }, (_, index) => {
    const lane = index % 8;
    return {
      id: `${season}-forest-light-${index + 1}`,
      kind: season === "summer" ? "firefly" : season === "winter" ? "ice-spark" : "dew-spark",
      style: {
        left: `${8 + ((index * 19 + lane * 4) % 88)}%`,
        top: `${16 + ((index * 11 + lane * 5) % 66)}%`,
        width: `${season === "summer" ? 4 + (index % 4) : 3 + (index % 3)}px`,
        height: `${season === "summer" ? 4 + (index % 4) : 3 + (index % 3)}px`,
        animationDuration: `${5 + (index % 6) * 0.9}s`,
        animationDelay: `${-1 * (index % 9) * 0.7}s`,
        "--forest-light-x": `${(index % 2 === 0 ? 1 : -1) * (22 + lane * 5)}px`,
        "--forest-light-y": `${(index % 3 - 1) * 18}px`,
      },
    };
  });
});
</script>

<template>
  <div class="seasonal-forest-scene" :class="seasonClass" aria-hidden="true">
    <span class="forest-weather-sky"></span>

    <svg class="forest-svg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
      <defs>
        <linearGradient id="forestGroundGradient" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="var(--forest-ground-a)" />
          <stop offset="100%" stop-color="var(--forest-ground-b)" />
        </linearGradient>
        <linearGradient id="forestTrunkGradient" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="var(--forest-trunk-a)" />
          <stop offset="100%" stop-color="var(--forest-trunk-b)" />
        </linearGradient>
        <radialGradient id="forestCanopyGradient" cx="48%" cy="34%" r="70%">
          <stop offset="0%" stop-color="var(--forest-canopy-a)" />
          <stop offset="58%" stop-color="var(--forest-canopy-b)" />
          <stop offset="100%" stop-color="var(--forest-canopy-c)" />
        </radialGradient>
        <filter id="forestSoftGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="10" />
        </filter>
      </defs>

      <g class="forest-back">
        <path class="forest-hill far" d="M0 610 C190 552 324 626 502 584 C696 538 842 620 1038 572 C1202 532 1324 560 1440 522 L1440 900 L0 900 Z" />
        <path class="forest-hill near" d="M0 704 C158 642 314 704 482 662 C690 610 826 706 1042 656 C1218 616 1334 654 1440 610 L1440 900 L0 900 Z" />
        <path class="forest-tree-line" d="M0 660 L34 596 L58 648 L96 568 L128 648 L164 590 L202 656 L244 548 L284 654 L322 584 L362 654 L410 560 L450 650 L488 598 L526 662 L574 552 L616 654 L662 580 L708 660 L748 544 L790 656 L836 586 L880 660 L928 558 L970 650 L1018 588 L1064 660 L1110 540 L1156 652 L1202 584 L1246 660 L1290 552 L1336 648 L1384 582 L1440 656 L1440 900 L0 900 Z" />
      </g>

      <g class="forest-hero-tree">
        <ellipse class="hero-shadow" cx="1084" cy="838" rx="270" ry="46" />
        <path class="hero-trunk" d="M1046 900 C1032 790 1052 688 1028 586 C1004 484 1028 376 1076 252 C1086 226 1128 226 1124 260 C1110 364 1124 458 1168 554 C1224 678 1190 796 1210 900 Z" />
        <path class="hero-branch strong" d="M1092 456 C1016 404 946 334 872 238" />
        <path class="hero-branch strong right" d="M1118 420 C1192 374 1252 310 1314 220" />
        <path class="hero-branch mid" d="M1100 538 C1014 510 942 470 850 404" />
        <path class="hero-branch mid right" d="M1142 532 C1226 498 1286 452 1360 382" />
        <path class="hero-branch thin" d="M1082 360 C1038 318 1000 274 960 214" />
        <path class="hero-branch thin right" d="M1136 346 C1184 310 1224 268 1266 206" />

        <g class="hero-canopy" filter="url(#forestSoftGlow)">
          <ellipse cx="990" cy="248" rx="226" ry="158" />
          <ellipse cx="1164" cy="280" rx="248" ry="174" />
          <ellipse cx="1058" cy="360" rx="310" ry="190" />
          <ellipse cx="904" cy="380" rx="180" ry="132" />
          <ellipse cx="1248" cy="418" rx="168" ry="126" />
        </g>
        <g class="canopy-detail">
          <circle cx="940" cy="248" r="78" />
          <circle cx="1090" cy="220" r="92" />
          <circle cx="1218" cy="306" r="84" />
          <circle cx="1020" cy="374" r="118" />
          <circle cx="1190" cy="424" r="92" />
          <circle cx="880" cy="402" r="82" />
        </g>
        <g class="winter-snow-caps">
          <path d="M842 382 C922 324 1002 328 1084 376 C1168 314 1262 330 1342 398 C1218 372 1122 420 1030 406 C960 394 902 368 842 382 Z" />
          <path d="M938 230 C1016 176 1118 184 1186 238 C1098 226 1032 252 938 230 Z" />
        </g>
      </g>

      <g class="forest-front">
        <path class="front-ground" d="M0 792 C176 742 310 800 480 768 C674 732 806 802 1014 754 C1198 712 1304 744 1440 704 L1440 900 L0 900 Z" />
        <path class="front-grass" d="M0 820 C160 796 320 822 486 800 C662 776 828 822 994 792 C1170 760 1300 796 1440 762" />
      </g>
    </svg>

    <span
      v-for="gust in gusts"
      :key="gust.id"
      class="forest-gust"
      :data-kind="gust.kind"
      :style="gust.style"
    ></span>

    <span
      v-for="light in lights"
      :key="light.id"
      class="forest-light"
      :data-kind="light.kind"
      :style="light.style"
    ></span>

    <span
      v-for="particle in particles"
      :key="particle.id"
      class="forest-particle"
      :data-kind="particle.kind"
      :data-depth="particle.depth"
      :style="particle.style"
    ></span>
  </div>
</template>

<style scoped>
.seasonal-forest-scene {
  --forest-ground-a: rgba(184, 224, 218, 0.2);
  --forest-ground-b: rgba(126, 184, 190, 0.22);
  --forest-trunk-a: rgba(128, 114, 92, 0.34);
  --forest-trunk-b: rgba(88, 78, 66, 0.56);
  --forest-branch: rgba(88, 82, 68, 0.28);
  --forest-back: rgba(162, 210, 214, 0.18);
  --forest-line: rgba(122, 174, 188, 0.18);
  --forest-canopy-a: rgba(218, 246, 236, 0.68);
  --forest-canopy-b: rgba(154, 218, 220, 0.44);
  --forest-canopy-c: rgba(116, 184, 190, 0.11);
  --forest-front: rgba(136, 190, 196, 0.18);
  --forest-particle-a: rgba(218, 246, 236, 0.9);
  --forest-particle-b: rgba(148, 204, 214, 0.68);

  position: absolute;
  inset: -7%;
  overflow: hidden;
  transform: translate3d(calc(var(--pointer-shift-x-soft) * -0.34), calc(var(--pointer-shift-y-soft) * -0.16), 0);
  transform-style: preserve-3d;
}

.forest-weather-sky,
.forest-gust,
.forest-light {
  position: absolute;
  pointer-events: none;
}

.forest-weather-sky {
  inset: -10%;
  opacity: 0.5;
  mix-blend-mode: screen;
  filter: saturate(116%);
  animation: forestSkyBreath 12s ease-in-out infinite;
}

.forest-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  opacity: 0.94;
}

.forest-back {
  transform: translate3d(calc(var(--pointer-shift-x-soft) * -0.48), calc(var(--pointer-shift-y-soft) * -0.18), 0);
}

.forest-hill {
  fill: var(--forest-back);
}

.forest-hill.near {
  fill: var(--forest-front);
}

.forest-tree-line {
  fill: var(--forest-line);
  opacity: 0.78;
}

.forest-hero-tree {
  transform-origin: 1084px 900px;
  animation: forestHeroSway 15s ease-in-out infinite;
}

.hero-shadow {
  fill: rgba(24, 38, 30, 0.14);
  filter: blur(12px);
}

.hero-trunk {
  fill: url("#forestTrunkGradient");
}

.hero-branch {
  fill: none;
  stroke: var(--forest-branch);
  stroke-linecap: round;
  stroke-width: 20;
}

.hero-branch.mid {
  stroke-width: 14;
}

.hero-branch.thin {
  stroke-width: 9;
  opacity: 0.76;
}

.hero-branch.right {
  opacity: 0.88;
}

.hero-canopy {
  fill: url("#forestCanopyGradient");
  opacity: 0.78;
  transform-origin: 1080px 330px;
  animation: forestCanopyBreath 9s ease-in-out infinite;
}

.canopy-detail {
  fill: var(--forest-canopy-b);
  opacity: 0.34;
  filter: blur(5px);
  mix-blend-mode: screen;
  animation: forestCanopyDrift 11s ease-in-out infinite;
}

.winter-snow-caps {
  fill: rgba(255, 255, 255, 0.7);
  filter: blur(1px);
  opacity: 0;
}

.front-ground {
  fill: url("#forestGroundGradient");
}

.front-grass {
  fill: none;
  stroke: rgba(255, 255, 255, 0.14);
  stroke-linecap: round;
  stroke-width: 2;
  opacity: 0.28;
}

.forest-gust {
  display: block;
  border-radius: 999px;
  background:
    linear-gradient(
      90deg,
      transparent 0%,
      rgba(255, 255, 255, 0.06) 18%,
      rgba(255, 255, 255, 0.32) 48%,
      rgba(255, 255, 255, 0.08) 76%,
      transparent 100%
    );
  filter: blur(5px);
  mix-blend-mode: screen;
  transform: rotate(-8deg) translate3d(-20vw, 0, 0);
  will-change: transform, opacity;
  animation: forestGustSweep ease-in-out infinite;
}

.forest-gust[data-kind="leaf-gust"] {
  background:
    linear-gradient(
      90deg,
      transparent 0%,
      rgba(255, 226, 150, 0.06) 18%,
      rgba(244, 150, 54, 0.24) 46%,
      rgba(255, 238, 186, 0.08) 78%,
      transparent 100%
    );
}

.forest-gust[data-kind="snow-squall"] {
  background:
    linear-gradient(
      90deg,
      transparent 0%,
      rgba(200, 228, 255, 0.08) 14%,
      rgba(255, 255, 255, 0.36) 44%,
      rgba(174, 214, 255, 0.12) 74%,
      transparent 100%
    );
  filter: blur(7px);
}

.forest-light {
  display: block;
  border-radius: 50%;
  background: rgba(255, 244, 164, 0.9);
  box-shadow:
    0 0 8px rgba(255, 234, 120, 0.8),
    0 0 20px rgba(106, 232, 164, 0.36);
  opacity: 0;
  transform: translate3d(0, 0, 0);
  will-change: transform, opacity;
  animation: forestLightFloat ease-in-out infinite;
}

.forest-light[data-kind="dew-spark"] {
  background: rgba(214, 248, 234, 0.84);
  box-shadow:
    0 0 7px rgba(214, 248, 234, 0.68),
    0 0 18px rgba(152, 220, 230, 0.24);
}

.forest-light[data-kind="ice-spark"] {
  background: rgba(236, 250, 255, 0.86);
  box-shadow:
    0 0 8px rgba(255, 255, 255, 0.8),
    0 0 18px rgba(150, 210, 255, 0.42);
}

.forest-particle {
  --forest-depth-scale: 1;

  position: absolute;
  display: block;
  top: -18%;
  opacity: 0;
  will-change: transform, opacity;
  animation:
    forestParticleFall linear infinite,
    forestParticleSway ease-in-out infinite;
}

.forest-particle::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 70% 30% 66% 34%;
  background:
    radial-gradient(circle at 30% 26%, rgba(255, 255, 255, 0.7), transparent 34%),
    linear-gradient(180deg, var(--forest-particle-a), var(--forest-particle-b));
  box-shadow: 0 10px 18px rgba(36, 42, 34, 0.12);
  transform-origin: 50% 20%;
  animation: forestParticleFlutter 2.8s ease-in-out infinite;
}

.forest-particle[data-depth="far"] {
  --forest-depth-scale: 0.72;

  filter: blur(0.7px);
}

.forest-particle[data-depth="near"] {
  --forest-depth-scale: 1.18;

  filter: blur(0.1px);
}

.forest-particle[data-kind="summer-leaf"]::before {
  --forest-particle-a: rgba(177, 226, 158, 0.88);
  --forest-particle-b: rgba(88, 156, 112, 0.62);
  border-radius: 20% 80% 24% 76%;
}

.forest-particle[data-kind="leaf"]::before {
  --forest-particle-a: rgba(238, 184, 88, 0.9);
  --forest-particle-b: rgba(178, 116, 58, 0.64);
  border-radius: 20% 80% 22% 78%;
}

.forest-particle[data-kind="snow"]::before {
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.96), rgba(255, 255, 255, 0.18) 66%, transparent 74%);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.forest-season-summer {
  --forest-ground-a: rgba(151, 200, 166, 0.18);
  --forest-ground-b: rgba(103, 160, 136, 0.22);
  --forest-trunk-a: rgba(130, 105, 72, 0.36);
  --forest-trunk-b: rgba(92, 70, 50, 0.52);
  --forest-branch: rgba(92, 72, 52, 0.34);
  --forest-back: rgba(118, 178, 146, 0.14);
  --forest-line: rgba(96, 154, 128, 0.18);
  --forest-canopy-a: rgba(172, 229, 178, 0.52);
  --forest-canopy-b: rgba(116, 188, 140, 0.36);
  --forest-canopy-c: rgba(72, 138, 116, 0.1);
  --forest-front: rgba(104, 164, 138, 0.16);
}

.forest-season-spring .forest-weather-sky {
  background:
    radial-gradient(circle at 26% 18%, rgba(190, 234, 238, 0.42), transparent 28%),
    radial-gradient(circle at 70% 22%, rgba(176, 232, 214, 0.26), transparent 30%),
    linear-gradient(115deg, transparent 16%, rgba(236, 252, 246, 0.18) 36%, transparent 58%);
}

.forest-season-summer .forest-weather-sky {
  background:
    radial-gradient(circle at 22% 18%, rgba(255, 238, 174, 0.18), transparent 24%),
    radial-gradient(circle at 74% 18%, rgba(132, 231, 196, 0.16), transparent 28%),
    linear-gradient(100deg, rgba(255, 255, 255, 0.08), transparent 28%, rgba(132, 219, 194, 0.1) 52%, transparent 74%);
  animation:
    forestSkyBreath 9s ease-in-out infinite,
    forestHeatShimmer 5.6s ease-in-out infinite;
}

.forest-season-autumn {
  --forest-ground-a: rgba(202, 168, 92, 0.2);
  --forest-ground-b: rgba(158, 120, 62, 0.22);
  --forest-trunk-a: rgba(132, 84, 42, 0.36);
  --forest-trunk-b: rgba(92, 58, 32, 0.54);
  --forest-branch: rgba(102, 62, 32, 0.34);
  --forest-back: rgba(214, 154, 78, 0.15);
  --forest-line: rgba(174, 116, 54, 0.18);
  --forest-canopy-a: rgba(246, 199, 92, 0.52);
  --forest-canopy-b: rgba(210, 148, 66, 0.36);
  --forest-canopy-c: rgba(150, 95, 44, 0.1);
  --forest-front: rgba(166, 126, 64, 0.16);
}

.forest-season-autumn .forest-weather-sky {
  background:
    radial-gradient(circle at 34% 18%, rgba(255, 212, 126, 0.24), transparent 28%),
    radial-gradient(circle at 84% 28%, rgba(244, 184, 92, 0.16), transparent 24%),
    linear-gradient(118deg, transparent 14%, rgba(255, 224, 150, 0.14) 38%, transparent 62%);
}

.forest-season-winter {
  --forest-ground-a: rgba(248, 252, 255, 0.42);
  --forest-ground-b: rgba(218, 236, 250, 0.22);
  --forest-trunk-a: rgba(156, 176, 190, 0.28);
  --forest-trunk-b: rgba(118, 138, 154, 0.46);
  --forest-branch: rgba(122, 144, 160, 0.28);
  --forest-back: rgba(224, 240, 252, 0.22);
  --forest-line: rgba(184, 208, 228, 0.18);
  --forest-canopy-a: rgba(255, 255, 255, 0.32);
  --forest-canopy-b: rgba(230, 242, 252, 0.18);
  --forest-canopy-c: rgba(196, 220, 240, 0.06);
  --forest-front: rgba(226, 240, 252, 0.18);
}

.forest-season-winter .forest-weather-sky {
  background:
    radial-gradient(ellipse at 32% 18%, rgba(236, 249, 255, 0.32), transparent 34%),
    radial-gradient(ellipse at 66% 16%, rgba(255, 255, 255, 0.32), transparent 28%),
    linear-gradient(104deg, transparent 12%, rgba(216, 240, 255, 0.18) 36%, rgba(255, 255, 255, 0.18) 52%, transparent 78%);
  filter: blur(1px) saturate(112%);
  animation:
    forestSkyBreath 12s ease-in-out infinite,
    forestAuroraDrift 10s ease-in-out infinite;
}

.forest-season-winter .hero-canopy,
.forest-season-winter .canopy-detail {
  opacity: 0.11;
}

.forest-season-winter .winter-snow-caps {
  opacity: 0.88;
}

.forest-season-winter .hero-shadow {
  fill: rgba(170, 198, 218, 0.08);
}

@media (max-width: 720px) {
  .seasonal-forest-scene {
    inset: -10% -22% -8% -18%;
    opacity: 0.82;
  }

  .forest-hero-tree {
    transform: translateX(90px) scale(0.9);
  }
}

@media (prefers-reduced-motion: reduce) {
  .forest-hero-tree,
  .hero-canopy,
  .canopy-detail,
  .forest-weather-sky,
  .forest-gust,
  .forest-light,
  .forest-particle,
  .forest-particle::before {
    animation-duration: 40s !important;
  }
}

@keyframes forestHeroSway {
  0%,
  100% {
    transform: rotate(-0.7deg) translate3d(0, 0, 0);
  }
  50% {
    transform: rotate(0.9deg) translate3d(8px, -4px, 0);
  }
}

@keyframes forestCanopyBreath {
  0%,
  100% {
    transform: scale(0.99);
  }
  50% {
    transform: scale(1.035) translate3d(4px, -3px, 0);
  }
}

@keyframes forestCanopyDrift {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
    opacity: 0.3;
  }
  50% {
    transform: translate3d(10px, -4px, 0);
    opacity: 0.42;
  }
}

@keyframes forestParticleFall {
  0% {
    transform: translate3d(0, -12vh, 0) rotate(0deg) scale(var(--forest-depth-scale));
    opacity: 0;
  }
  10% {
    opacity: var(--forest-opacity);
  }
  100% {
    transform: translate3d(var(--forest-fall-x), var(--forest-fall-y), 0) rotate(var(--forest-spin)) scale(var(--forest-depth-scale));
    opacity: 0.08;
  }
}

@keyframes forestParticleSway {
  0%,
  100% {
    margin-left: 0;
  }
  35% {
    margin-left: var(--forest-sway-a);
  }
  70% {
    margin-left: var(--forest-sway-b);
  }
}

@keyframes forestParticleFlutter {
  0%,
  100% {
    transform: rotateY(-24deg) rotateZ(-8deg) scale(0.94);
  }
  50% {
    transform: rotateY(34deg) rotateZ(16deg) scale(1.06);
  }
}

@keyframes forestGustSweep {
  0% {
    transform: rotate(-8deg) translate3d(-26vw, var(--forest-gust-y), 0);
    opacity: 0;
  }
  18% {
    opacity: 1;
  }
  70% {
    opacity: 0.72;
  }
  100% {
    transform: rotate(-8deg) translate3d(58vw, calc(var(--forest-gust-y) * -0.4), 0);
    opacity: 0;
  }
}

@keyframes forestLightFloat {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(0.62);
    opacity: 0;
  }
  22% {
    opacity: 0.86;
  }
  58% {
    transform: translate3d(var(--forest-light-x), var(--forest-light-y), 0) scale(1.18);
    opacity: 0.96;
  }
  82% {
    opacity: 0.24;
  }
}

@keyframes forestSkyBreath {
  0%,
  100% {
    transform: translate3d(0, 0, 0) scale(1);
    opacity: 0.42;
  }
  50% {
    transform: translate3d(calc(var(--pointer-shift-x-soft) * 0.8), calc(var(--pointer-shift-y-soft) * -0.5), 0) scale(1.04);
    opacity: 0.72;
  }
}

@keyframes forestHeatShimmer {
  0%,
  100% {
    filter: blur(0.4px) saturate(118%);
  }
  50% {
    filter: blur(2px) saturate(142%);
  }
}

@keyframes forestAuroraDrift {
  0%,
  100% {
    background-position: 0% 0%;
  }
  50% {
    background-position: 18% 8%;
  }
}
</style>
