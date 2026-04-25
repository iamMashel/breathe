import type { AirQualityResponse, ForecastResponse } from '~/types'

export function useBreatheApi() {
  const config = useRuntimeConfig()
  const base = config.public.apiBase as string

  function getCurrentAQ(city: string) {
    return useFetch<AirQualityResponse>(
      `${base}/api/v1/air-quality/${encodeURIComponent(city)}`,
      { key: `aq-${city}` },
    )
  }

  function getForecast(city: string) {
    return useFetch<ForecastResponse>(
      `${base}/api/v1/air-quality/${encodeURIComponent(city)}/forecast`,
      { key: `forecast-${city}` },
    )
  }

  return { getCurrentAQ, getForecast }
}
