<script setup lang="ts">
const props = defineProps<{ aqi: number; color: string }>()

// Semicircle: M 20 100 A 80 80 0 0 0 180 100
// Path length = π × r = π × 80 ≈ 251.33
const ARC_LEN = Math.PI * 80

// Animate from 0 on mount
const animated = ref(0)
onMounted(() => {
  requestAnimationFrame(() => { animated.value = props.aqi })
})
watch(() => props.aqi, (val) => { animated.value = val })

const dasharray = computed(() => {
  const filled = (Math.min(animated.value, 500) / 500) * ARC_LEN
  return `${filled} ${ARC_LEN}`
})
</script>

<template>
  <div class="flex flex-col items-center">
    <svg viewBox="0 0 200 110" class="w-full" aria-label="AQI gauge">
      <!-- Track -->
      <path d="M 20 100 A 80 80 0 0 0 180 100"
            fill="none" stroke="#1a1a2a" stroke-width="13" stroke-linecap="round" />
      <!-- Progress -->
      <path d="M 20 100 A 80 80 0 0 0 180 100"
            fill="none"
            :stroke="color"
            stroke-width="13"
            stroke-linecap="round"
            :stroke-dasharray="dasharray"
            stroke-dashoffset="0"
            style="transition: stroke-dasharray 1s cubic-bezier(0.4,0,0.2,1);" />
      <!-- Min / Max labels -->
      <text x="16" y="116" fill="#3a3a5a" font-size="10" text-anchor="middle">0</text>
      <text x="184" y="116" fill="#3a3a5a" font-size="10" text-anchor="middle">500</text>
    </svg>
  </div>
</template>
