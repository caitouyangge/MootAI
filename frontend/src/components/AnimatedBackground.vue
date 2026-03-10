<template>
  <div class="animated-background-root" @click="onRootClick">
    <div class="bg-gradient"></div>
    <div class="bg-mesh"></div>

    <div v-if="enableRipples" class="water-ripples" aria-hidden="true">
      <div
        v-for="r in waterRipples"
        :key="r.id"
        class="ripple"
        :style="{
          left: r.x + '%',
          top: r.y + '%',
          width: r.size + 'px',
          height: r.size + 'px',
          '--ripple-duration': r.duration + 's',
          '--ripple-delay': r.delay + 's',
          '--ripple-opacity': r.opacity,
          '--ripple-stroke': r.stroke
        }"
        @animationend="removeRipple(r.id)"
      />
    </div>

    <div class="bg-particles" aria-hidden="true">
      <div v-for="i in particleCount" :key="i" class="particle" :style="getParticleStyle(i)"></div>
    </div>
    <div class="bg-noise" aria-hidden="true"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  enableRipples: { type: Boolean, default: false },
  clickToRipple: { type: Boolean, default: false },
  ignoreSelectors: { type: Array, default: () => ['button', '.modal-overlay', 'a'] },
  particleCount: { type: Number, default: 12 }
})

// 水圈波纹：欢迎页同款（随机生成，点击增强）
const waterRipples = ref([])
let rippleId = 0
let rippleTimer = null
const MAX_RIPPLES = 20

function addRipple(ev) {
  if (!props.enableRipples) return
  if (waterRipples.value.length >= MAX_RIPPLES) return
  const id = ++rippleId
  const isClick = !!ev && typeof ev.clientX === 'number' && typeof ev.clientY === 'number'
  // 样式统一为“点击生成”的水波参数
  const baseOpacity = 0.42
  const randOpacity = 0.18
  const baseStroke = 1.7
  const randStroke = 1.1
  const baseSize = isClick ? 90 : 60
  const randSize = isClick ? 260 : 200
  const size = baseSize + Math.random() * randSize
  // 越大的水波纹扩散越慢：点击与随机共用同一规律，仅由 size 决定 duration
  const sizeFactor = Math.min(Math.max(size / 260, 0.6), 2)
  const duration = 1.0 + 1.2 * sizeFactor + Math.random() * 0.5

  waterRipples.value.push({
    id,
    x: isClick ? (ev.clientX / window.innerWidth) * 100 : 8 + Math.random() * 84,
    y: isClick ? (ev.clientY / window.innerHeight) * 100 : 12 + Math.random() * 76,
    size,
    duration,
    delay: isClick ? 0 : Math.random() * 0.4,
    opacity: baseOpacity + Math.random() * randOpacity,
    stroke: baseStroke + Math.random() * randStroke
  })
}

function removeRipple(id) {
  waterRipples.value = waterRipples.value.filter((r) => r.id !== id)
}

function shouldIgnoreClick(ev) {
  const target = ev?.target
  if (!target || typeof target.closest !== 'function') return false
  return props.ignoreSelectors.some((sel) => target.closest(sel))
}

function onRootClick(ev) {
  if (!props.enableRipples || !props.clickToRipple) return
  if (shouldIgnoreClick(ev)) return
  addRipple(ev)
}

function onRequestRipple(e) {
  if (!props.enableRipples || !props.clickToRipple) return
  const { clientX, clientY } = e.detail || {}
  if (typeof clientX !== 'number' || typeof clientY !== 'number') return
  addRipple({ clientX, clientY })
}

onMounted(() => {
  if (!props.enableRipples) return
  addRipple()
  addRipple()
  addRipple()
  addRipple()
  rippleTimer = setInterval(() => {
    addRipple()
  }, 500 + Math.random() * 600)
  window.addEventListener('request-ripple', onRequestRipple)
})

onUnmounted(() => {
  if (rippleTimer) clearInterval(rippleTimer)
  window.removeEventListener('request-ripple', onRequestRipple)
})

const getParticleStyle = () => {
  const size = Math.random() * 2.5 + 1.2
  const left = Math.random() * 100
  const delay = Math.random() * 5
  const duration = Math.random() * 3 + 2
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`
  }
}
</script>

<style scoped>
.animated-background-root {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    var(--primary-purple-lightest) 0%,
    var(--primary-purple-lighter) 25%,
    var(--primary-purple-light) 50%,
    var(--primary-purple) 75%,
    var(--primary-purple-dark) 100%
  );
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

.bg-mesh {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% 15%, rgba(255,255,255,0.18) 0%, transparent 55%),
    radial-gradient(ellipse 60% 40% at 75% 85%, rgba(255,255,255,0.08) 0%, transparent 50%),
    radial-gradient(ellipse 50% 35% at 25% 70%, rgba(6, 182, 212, 0.06) 0%, transparent 50%);
  pointer-events: none;
}

.bg-particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.35);
  border-radius: 50%;
  animation: float 3s ease-in-out infinite;
  box-shadow: 0 0 6px rgba(6, 182, 212, 0.25);
  top: -10%;
}

.bg-noise {
  position: absolute;
  inset: 0;
  opacity: 0.035;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-repeat: repeat;
}

/* 水圈波纹：真实物理感（扩散 + 衰减） */
.water-ripples {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.ripple {
  position: absolute;
  border-radius: 50%;
  border: calc(var(--ripple-stroke, 1.5) * 1px) solid rgba(255, 255, 255, var(--ripple-opacity, 0.42));
  box-shadow:
    0 0 0 0 rgba(255, 255, 255, 0),
    0 0 18px rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.35)),
    inset 0 0 18px rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.55));
  transform: translate(-50%, -50%) scale(0);
  opacity: 1;
  animation: rippleExpand var(--ripple-duration, 2.8s) var(--ripple-delay, 0s) cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
  will-change: transform, opacity, border-color, box-shadow;
  mix-blend-mode: screen;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.22)));
}

.ripple::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.7));
  opacity: 0;
  animation: rippleRing 2.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
}

.ripple::after {
  content: '';
  position: absolute;
  inset: -14px;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.20)) 0%,
    rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.08)) 35%,
    rgba(255, 255, 255, 0) 70%
  );
  opacity: 0;
  animation: rippleGlow var(--ripple-duration, 2.8s) var(--ripple-delay, 0s) ease-out forwards;
  pointer-events: none;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes float {
  0% { transform: translateY(0); opacity: 0.9; }
  50% { transform: translateY(14px); opacity: 1; }
  100% { transform: translateY(0); opacity: 0.9; }
}

@keyframes rippleExpand {
  0% {
    transform: translate(-50%, -50%) scale(0);
    opacity: 1;
    border-color: rgba(255, 255, 255, var(--ripple-opacity, 0.42));
    box-shadow:
      0 0 0 0 rgba(255, 255, 255, 0.18),
      0 0 24px rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.35)),
      inset 0 0 22px rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.68));
  }
  18% {
    opacity: 1;
    border-color: rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 1.0));
    box-shadow:
      0 0 0 0 rgba(255, 255, 255, 0.22),
      0 0 34px rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.42)),
      inset 0 0 26px rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.72));
  }
  42% {
    border-color: rgba(255, 255, 255, calc(var(--ripple-opacity, 0.42) * 0.95));
  }
  100% {
    transform: translate(-50%, -50%) scale(2.85);
    opacity: 0;
    border-color: rgba(255, 255, 255, 0);
    box-shadow:
      0 0 32px 2px rgba(255, 255, 255, 0),
      inset 0 0 30px rgba(255, 255, 255, 0);
  }
}

@keyframes rippleRing {
  0% { transform: scale(0.5); opacity: 0.6; }
  100% { transform: scale(1.1); opacity: 0; }
}

@keyframes rippleGlow {
  0% { transform: scale(0.55); opacity: 0; }
  12% { opacity: 0.85; }
  100% { transform: scale(1.25); opacity: 0; }
}
</style>
