<script setup lang="ts">
import type { WeatherInfo } from '~/types'
defineProps<{ weather: WeatherInfo }>()
</script>

<template>
  <div class="rounded-2xl px-5 py-4 border border-white/8 flex flex-wrap items-center gap-6"
       style="background: #0D0D1A;">
    <div>
      <div class="text-3xl font-bold text-white">{{ Math.round(weather.temperature_c) }}°C</div>
      <div class="text-gray-500 text-xs capitalize mt-0.5">{{ weather.condition }}</div>
    </div>
    <div class="flex gap-6 text-sm">
      <div>
        <div class="text-white font-medium">{{ weather.humidity_pct }}%</div>
        <div class="text-gray-600 text-xs">Humidity</div>
      </div>
      <div>
        <div class="text-white font-medium">{{ weather.wind_speed_ms }} m/s</div>
        <div class="text-gray-600 text-xs">Wind</div>
      </div>
      <div>
        <div class="text-white font-medium">{{ Math.round(weather.feels_like_c) }}°C</div>
        <div class="text-gray-600 text-xs">Feels like</div>
      </div>
    </div>
  </div>
</template>
