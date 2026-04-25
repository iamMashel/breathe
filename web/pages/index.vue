<script setup lang="ts">
useSeoMeta({
  title: 'Breathe — Air Quality & Health',
  description: 'Real-time air quality monitoring and personalised health advisories for any city.',
})

const query = ref('')
const router = useRouter()

function search() {
  const city = query.value.trim()
  if (city) router.push(`/${encodeURIComponent(city)}`)
}

const quickCities = ['Nairobi', 'Kampala', 'Lagos', 'Johannesburg', 'Accra', 'Cairo', 'Dar es Salaam']
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-4 py-20">
    <div class="w-full max-w-xl text-center">

      <!-- Brand -->
      <h1 class="text-7xl font-bold tracking-tight text-white mb-3">Breathe</h1>
      <p class="text-gray-500 text-lg mb-14">
        Real-time air quality &amp; health advisories for any city.
      </p>

      <!-- Search -->
      <form @submit.prevent="search" class="relative mb-8">
        <input
          v-model="query"
          type="text"
          placeholder="Enter a city name..."
          autofocus
          class="w-full border border-white/10 rounded-2xl px-6 py-4 pr-36 text-white placeholder-gray-600 text-lg focus:outline-none focus:border-white/25 transition"
          style="background: rgba(255,255,255,0.04);"
        />
        <button
          type="submit"
          class="absolute right-2 top-1/2 -translate-y-1/2 bg-white text-black px-5 py-2.5 rounded-xl font-semibold hover:bg-gray-100 active:scale-95 transition text-sm"
        >
          Check Air →
        </button>
      </form>

      <!-- Quick-access cities -->
      <div class="flex flex-wrap gap-2 justify-center">
        <button
          v-for="city in quickCities"
          :key="city"
          @click="router.push(`/${city}`)"
          class="px-4 py-1.5 rounded-full text-sm text-gray-500 border border-white/10 hover:border-white/25 hover:text-gray-300 transition"
        >
          {{ city }}
        </button>
      </div>
    </div>

    <p class="absolute bottom-6 text-gray-700 text-xs text-center">
      Data: OpenWeatherMap · Index: EPA AQI · Health: WHO 2021 Guidelines
    </p>
  </div>
</template>
