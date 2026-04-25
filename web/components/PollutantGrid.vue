<script setup lang="ts">
interface Pollutant {
  key: string
  value: string
  unit: string
  index: number
}

defineProps<{ pollutants: Pollutant[] }>()

function indexColor(i: number): string {
  if (i <= 50)  return '#00E400'
  if (i <= 100) return '#C8C800'
  if (i <= 150) return '#FF7E00'
  if (i <= 200) return '#FF0000'
  if (i <= 300) return '#8F3F97'
  return '#7E0023'
}
</script>

<template>
  <div>
    <h3 class="text-gray-500 text-xs font-medium uppercase tracking-wider mb-2">Pollutants</h3>
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <div v-for="p in pollutants" :key="p.key"
           class="rounded-2xl px-4 py-3 border border-white/8"
           style="background: #0D0D1A;">
        <div class="flex items-center justify-between mb-2">
          <span class="text-gray-400 text-xs font-medium">{{ p.key }}</span>
          <span class="text-xs font-semibold rounded-full px-2 py-0.5"
                :style="`color:${indexColor(p.index)};background:${indexColor(p.index)}1a`">
            {{ p.index }}
          </span>
        </div>
        <div class="text-white font-semibold text-sm">{{ p.value }}</div>
        <div class="text-gray-600 text-xs">{{ p.unit }}</div>
        <div class="mt-2 h-1 rounded-full" style="background:rgba(255,255,255,0.06)">
          <div class="h-1 rounded-full transition-all duration-700"
               :style="`width:${Math.min((p.index/500)*100,100)}%;background:${indexColor(p.index)}`" />
        </div>
      </div>
    </div>
  </div>
</template>
