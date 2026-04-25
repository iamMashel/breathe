<script setup lang="ts">
import type { ForecastEntry } from '~/types'

const props = defineProps<{ forecast: ForecastEntry[] }>()

const maxAqi = computed(() => Math.max(...props.forecast.map(e => e.aqi), 100))

function hour(iso: string) {
  return new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', hour12: false })
}
</script>

<template>
  <div class="rounded-2xl px-4 pt-4 pb-3 border border-white/8" style="background: #0D0D1A;">
    <!-- Bars -->
    <div class="flex items-end gap-2" style="height: 120px;">
      <div v-for="entry in forecast" :key="entry.timestamp"
           class="flex-1 flex flex-col justify-end">
        <div
          class="w-full rounded-t-sm"
          :style="{
            height: `${Math.max((entry.aqi / maxAqi) * 100, 5)}%`,
            backgroundColor: entry.color,
            opacity: '0.85',
            transition: 'height 0.7s ease',
          }"
          :title="`${hour(entry.timestamp)}: AQI ${entry.aqi} — ${entry.category}`"
        />
      </div>
    </div>
    <!-- Time labels -->
    <div class="flex gap-2 mt-1.5">
      <div v-for="entry in forecast" :key="entry.timestamp"
           class="flex-1 text-center text-gray-600 text-xs">
        {{ hour(entry.timestamp) }}
      </div>
    </div>
    <!-- Legend -->
    <div class="mt-3 flex flex-wrap gap-4 text-xs text-gray-600">
      <span v-for="[label, color] in [['Good','#00E400'],['Moderate','#C8C800'],['USG','#FF7E00'],['Unhealthy','#FF0000']]"
            :key="label" class="flex items-center gap-1.5">
        <span class="w-2.5 h-2.5 rounded-sm inline-block" :style="`background:${color}`" />
        {{ label }}
      </span>
    </div>
  </div>
</template>
