<script setup lang="ts">
import type { AirQualityResponse, ForecastResponse } from '~/types'

const route = useRoute()
const city = route.params.city as string
const { getCurrentAQ, getForecast } = useBreatheApi()

const { data: aq, pending, error } = await getCurrentAQ(city)
const { data: forecast } = await getForecast(city)

useSeoMeta({
  title: () =>
    aq.value
      ? `${aq.value.location.city} — AQI ${aq.value.aqi.overall} (${aq.value.aqi.category}) | Breathe`
      : `${city} | Breathe`,
  description: () =>
    aq.value
      ? `Air quality in ${aq.value.location.city}: ${aq.value.aqi.category}. ${aq.value.advisories.general}`
      : '',
})

function formatDate(iso: string) {
  return new Date(iso).toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}

const pollutants = computed(() => {
  if (!aq.value) return []
  const { components, aqi } = aq.value
  return [
    { key: 'PM2.5',  value: components.pm2_5.toFixed(1), unit: 'µg/m³', index: aqi.per_pollutant.pm2_5 },
    { key: 'PM10',   value: components.pm10.toFixed(1),  unit: 'µg/m³', index: aqi.per_pollutant.pm10  },
    { key: 'O₃',     value: components.o3.toFixed(1),    unit: 'µg/m³', index: aqi.per_pollutant.o3    },
    { key: 'NO₂',    value: components.no2.toFixed(1),   unit: 'µg/m³', index: aqi.per_pollutant.no2   },
    { key: 'SO₂',    value: components.so2.toFixed(1),   unit: 'µg/m³', index: aqi.per_pollutant.so2   },
    { key: 'CO',     value: (components.co / 1000).toFixed(2), unit: 'mg/m³', index: aqi.per_pollutant.co },
  ]
})
</script>

<template>
  <div class="min-h-screen">

    <!-- Nav -->
    <div class="px-4 pt-6 max-w-4xl mx-auto">
      <NuxtLink to="/" class="text-gray-600 hover:text-white transition text-sm inline-flex items-center gap-1">
        ← Breathe
      </NuxtLink>
    </div>

    <!-- Loading -->
    <div v-if="pending" class="flex items-center justify-center min-h-[60vh]">
      <p class="text-gray-600 animate-pulse">Fetching air quality data…</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="flex flex-col items-center justify-center min-h-[60vh] gap-4 px-4 text-center">
      <p class="text-red-400 text-lg">Could not find <span class="font-semibold">"{{ city }}"</span></p>
      <p class="text-gray-600 text-sm">Check the spelling and try again.</p>
      <NuxtLink to="/" class="bg-white text-black px-5 py-2 rounded-xl text-sm font-semibold hover:bg-gray-100 transition">
        Try another city
      </NuxtLink>
    </div>

    <!-- Main dashboard -->
    <div v-else-if="aq" class="max-w-4xl mx-auto px-4 pb-20 space-y-4 mt-4">

      <!-- ── Hero ── -->
      <div class="rounded-3xl p-6 md:p-8 border border-white/8 relative overflow-hidden"
           style="background: #0D0D1A;">
        <!-- AQI color glow -->
        <div class="absolute inset-0 pointer-events-none rounded-3xl"
             :style="`background: radial-gradient(ellipse at 25% 50%, ${aq.aqi.color}18, transparent 65%)`" />

        <div class="relative flex flex-col md:flex-row items-center gap-8">

          <!-- Gauge -->
          <div class="w-52 shrink-0">
            <AqiGauge :aqi="aq.aqi.overall" :color="aq.aqi.color" />
          </div>

          <!-- AQI info -->
          <div class="flex-1 text-center md:text-left">
            <p class="text-gray-500 text-sm mb-1">
              {{ aq.location.city }}, {{ aq.location.country }}
            </p>
            <div class="flex items-end gap-3 justify-center md:justify-start mb-2">
              <span class="text-8xl font-bold text-white leading-none">{{ aq.aqi.overall }}</span>
              <div class="mb-2">
                <span class="block text-base font-semibold" :style="`color: ${aq.aqi.color}`">
                  {{ aq.aqi.category }}
                </span>
                <span class="text-gray-600 text-xs">EPA AQI</span>
              </div>
            </div>
            <p class="text-gray-500 text-sm">
              Dominant: <span class="text-gray-300 font-medium">
                {{ aq.aqi.dominant_pollutant.replace('_', '.').toUpperCase() }}
              </span>
            </p>
            <p class="text-gray-700 text-xs mt-1">
              {{ formatDate(aq.measured_at) }} UTC
            </p>
          </div>

          <!-- Safety score -->
          <SafetyScore :score="aq.outdoor_safety.score" :label="aq.outdoor_safety.label" />

        </div>
      </div>

      <!-- ── Weather ── -->
      <WeatherWidget v-if="aq.weather" :weather="aq.weather" />

      <!-- ── Pollutants ── -->
      <PollutantGrid :pollutants="pollutants" />

      <!-- ── WHO flag ── -->
      <div v-if="aq.aqi.who_guidelines_exceeded.length"
           class="rounded-2xl px-4 py-3 border border-yellow-500/20"
           style="background: rgba(234,179,8,0.04);">
        <p class="text-yellow-400 text-sm font-medium">⚠ WHO 2021 Guideline Exceeded</p>
        <p class="text-gray-500 text-xs mt-0.5">
          {{ aq.aqi.who_guidelines_exceeded.join(', ').replace(/_/g, '.').toUpperCase() }}
          exceed WHO 24-hour guidelines even at "Good" EPA AQI levels.
        </p>
      </div>
      <div v-else
           class="rounded-2xl px-4 py-3 border border-green-500/20"
           style="background: rgba(34,197,94,0.04);">
        <p class="text-green-400 text-sm font-medium">✓ All pollutants within WHO 2021 guidelines</p>
      </div>

      <!-- ── Advisories ── -->
      <AdvisoryPanel :advisories="aq.advisories" />

      <!-- ── Forecast ── -->
      <div v-if="forecast?.forecast.length">
        <h3 class="text-gray-500 text-xs font-medium uppercase tracking-wider mb-2">24-Hour Forecast</h3>
        <ForecastChart :forecast="forecast.forecast.slice(0, 8)" />
      </div>

    </div>
  </div>
</template>
