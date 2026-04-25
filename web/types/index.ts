export interface Location {
  city: string
  country: string
  lat: number
  lon: number
}

export interface AQIBreakdown {
  overall: number
  category: string
  color: string
  dominant_pollutant: string
  per_pollutant: Record<string, number>
  who_guidelines_exceeded: string[]
}

export interface PollutantComponents {
  co: number
  no: number
  no2: number
  o3: number
  so2: number
  pm2_5: number
  pm10: number
  nh3: number
}

export interface OutdoorSafety {
  score: number
  label: string
}

export interface WeatherInfo {
  temperature_c: number
  feels_like_c: number
  humidity_pct: number
  condition: string
  wind_speed_ms: number
}

export interface AirQualityResponse {
  location: Location
  aqi: AQIBreakdown
  components: PollutantComponents
  advisories: Record<string, string>
  outdoor_safety: OutdoorSafety
  weather: WeatherInfo | null
  measured_at: string
}

export interface ForecastEntry {
  aqi: number
  category: string
  color: string
  dominant_pollutant: string
  components: PollutantComponents
  timestamp: string
}

export interface ForecastResponse {
  location: Location
  forecast: ForecastEntry[]
}
