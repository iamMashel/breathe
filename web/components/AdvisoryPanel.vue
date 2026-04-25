<script setup lang="ts">
defineProps<{ advisories: Record<string, string> }>()

const groups = [
  { key: 'general',     label: 'General'     },
  { key: 'children',    label: 'Children'    },
  { key: 'elderly',     label: 'Elderly'     },
  { key: 'respiratory', label: 'Respiratory' },
  { key: 'athletes',    label: 'Athletes'    },
  { key: 'pregnant',    label: 'Pregnant'    },
]

const active = ref('general')
</script>

<template>
  <div class="rounded-2xl border border-white/8 overflow-hidden" style="background: #0D0D1A;">
    <div class="px-4 pt-4 pb-3 border-b border-white/5">
      <h3 class="text-gray-500 text-xs font-medium uppercase tracking-wider">Health Advisories</h3>
    </div>
    <!-- Group tabs -->
    <div class="flex gap-1 px-3 py-2 overflow-x-auto scrollbar-none border-b border-white/5">
      <button
        v-for="g in groups"
        :key="g.key"
        @click="active = g.key"
        class="whitespace-nowrap px-3 py-1.5 rounded-lg text-xs font-medium transition"
        :class="active === g.key ? 'bg-white/10 text-white' : 'text-gray-600 hover:text-gray-300'"
      >
        {{ g.label }}
      </button>
    </div>
    <!-- Text -->
    <div class="px-4 py-4">
      <p class="text-gray-300 text-sm leading-relaxed">{{ advisories[active] }}</p>
    </div>
  </div>
</template>
