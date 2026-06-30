<!-- 文件说明：定义 HeaderQXMarquee 前端组件。 -->
<template>
  <div class="header-qx-flight" aria-hidden="true">
    <div class="header-qx-flight-lane lane-primary">
      <div class="header-qx-orb">
        <img class="header-qx-logo" src="/qx-logo-hua.png" alt="" role="presentation" />
      </div>
    </div>

    <div class="header-qx-flight-lane lane-secondary">
      <div class="header-qx-orb is-soft">
        <img class="header-qx-logo" src="/qx-logo-hua.png" alt="" role="presentation" />
      </div>
    </div>

    <div class="header-qx-flight-lane lane-tertiary">
      <div class="header-qx-orb is-small">
        <img class="header-qx-logo" src="/qx-logo-hua.png" alt="" role="presentation" />
      </div>
    </div>

    <div class="header-qx-flight-lane lane-quaternary">
      <div class="header-qx-orb is-faint">
        <img class="header-qx-logo" src="/qx-logo-hua.png" alt="" role="presentation" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-qx-flight {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
  contain: layout paint;
  transform: translate3d(0, 0, 0);
  will-change: transform;
}

.header-qx-flight-lane {
  position: absolute;
  top: 4px;
  left: -132px;
  width: 78px;
  height: 78px;
  opacity: 0.34;
  --flight-scale: 1;
  animation: qxFlightAcross 28s linear infinite;
  backface-visibility: hidden;
  contain: layout paint style;
  transform: translate3d(-12vw, 0, 0) scale(var(--flight-scale));
  transform-origin: center;
  will-change: transform;
}

.lane-primary {
  animation-delay: -6s;
}

.lane-secondary {
  top: 12px;
  opacity: 0.16;
  --flight-scale: 0.68;
  animation-duration: 34s;
  animation-delay: -18s;
}

.lane-tertiary {
  top: -2px;
  opacity: 0.22;
  --flight-scale: 0.56;
  animation-duration: 24s;
  animation-delay: -13s;
}

.lane-quaternary {
  top: 22px;
  opacity: 0.12;
  --flight-scale: 0.44;
  animation-duration: 38s;
  animation-delay: -28s;
}

.header-qx-orb {
  position: relative;
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  animation: qxFlightFloat 7.2s ease-in-out infinite, qxGlowPulse 5.8s ease-in-out infinite;
  backface-visibility: hidden;
  transform: translate3d(0, 0, 0);
  will-change: transform, opacity;
}

.header-qx-orb::before {
  content: "";
  position: absolute;
  inset: 8%;
  border-radius: 999px;
  background:
    radial-gradient(circle, rgba(119, 226, 255, 0.56) 0%, rgba(119, 226, 255, 0.24) 42%, rgba(119, 226, 255, 0.08) 60%, rgba(119, 226, 255, 0) 76%);
  filter: blur(16px);
  opacity: 1;
  transform: translate3d(0, 0, 0);
  will-change: opacity;
}

.header-qx-orb::after {
  content: "";
  position: absolute;
  inset: 18%;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(188, 244, 255, 0.42) 0%, rgba(188, 244, 255, 0.1) 44%, rgba(188, 244, 255, 0) 72%);
  filter: blur(9px);
  opacity: 0.96;
  transform: translate3d(0, 0, 0);
  will-change: opacity;
}

.header-qx-orb.is-soft {
  animation-duration: 8.8s, 7.4s;
}

.header-qx-orb.is-small {
  animation-duration: 6.4s, 6.8s;
}

.header-qx-orb.is-faint {
  animation-duration: 9.6s, 8.2s;
}

.header-qx-logo {
  width: 88%;
  height: 88%;
  object-fit: contain;
  display: block;
  backface-visibility: hidden;
  filter:
    drop-shadow(0 0 12px rgba(130, 226, 255, 0.42))
    drop-shadow(0 0 28px rgba(76, 184, 255, 0.24))
    drop-shadow(0 0 48px rgba(76, 184, 255, 0.12));
  transform: translate3d(0, 0, 0);
  will-change: transform;
}

@keyframes qxFlightAcross {
  0% {
    transform: translate3d(-12vw, 0, 0) scale(var(--flight-scale));
  }
  100% {
    transform: translate3d(120vw, 0, 0) scale(var(--flight-scale));
  }
}

@keyframes qxFlightFloat {
  0%,
  100% {
    transform: translateY(0) scale(1);
  }
  30% {
    transform: translateY(-5px) scale(1.02);
  }
  68% {
    transform: translateY(4px) scale(0.985);
  }
}

@keyframes qxGlowPulse {
  0%,
  100% {
    opacity: 0.84;
  }
  50% {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .header-qx-flight-lane {
    left: auto;
    right: 14%;
    animation: none;
    opacity: 0.16;
  }

  .header-qx-orb,
  .header-qx-orb.is-soft,
  .header-qx-orb.is-small,
  .header-qx-orb.is-faint {
    animation: none;
  }
}

@media (max-width: 960px) {
  .header-qx-flight-lane {
    width: 60px;
    height: 60px;
    opacity: 0.22;
  }

  .lane-secondary {
    opacity: 0.08;
  }

  .lane-tertiary {
    opacity: 0.12;
  }

  .lane-quaternary {
    opacity: 0.07;
  }
}

@media (max-width: 720px) {
  .header-qx-flight-lane {
    top: 12px;
    opacity: 0.12;
    animation-duration: 30s;
  }

  .lane-primary {
    top: 8px;
  }

  .lane-secondary {
    top: 18px;
    opacity: 0.08;
  }

  .lane-tertiary {
    top: 4px;
    opacity: 0.09;
  }

  .lane-quaternary {
    top: 24px;
    opacity: 0.06;
  }
}
</style>
