<script setup lang="ts">
const props = defineProps<{ score: number; label: string }>()

// Circle circumference at r=34: 2π×34 ≈ 213.6
const CIRC = 2 * Math.PI * 34

const scoreColor = computed(() => {
  if (props.score >= 80) return '#00E400'
  if (props.score >= 60) return '#9ACD32'
  if (props.score >= 40) return '#FF7E00'
  if (props.score >= 20) return '#FF0000'
  return '#8F3F97'
})

const animated = ref(0)
onMounted(() => { requestAnimationFrame(() => { animated.value = props.score }) })

const dasharray = computed(() => {
  const filled = (Math.min(animated.value, 100) / 100) * CIRC
  return `${filled} ${CIRC}`
})
</script>

<template>
  <div class="text-center shrink-0">
    <div class="relative w-20 h-20 mx-auto">
      <svg viewBox="0 0 80 80" class="w-full h-full -rotate-90">
        <circle cx="40" cy="40" r="34" fill="none" stroke="#1a1a2a" stroke-width="7" />
        <circle
          cx="40" cy="40" r="34"
          fill="none"
          :stroke="scoreColor"
          stroke-width="7"
          stroke-linecap="round"
          :stroke-dasharray="dasharray"
          style="transition: stroke-dasharray 1s cubic-bezier(0.4,0,0.2,1);"
        />
      </svg>
      <div class="absolute inset-0 flex items-center justify-center">
        <span class="text-white font-bold text-xl leading-none">{{ score }}</span>
      </div>
    </div>
    <p class="text-xs mt-1.5 font-medium" :style="`color: ${scoreColor}`">{{ label }}</p>
    <p class="text-gray-600 text-xs">Outdoor Safety</p>
  </div>
</template>
