FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build the Nuxt app — API URL is injected at runtime via NUXT_PUBLIC_API_BASE
RUN npm run build

# ── Production image ──
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/.output ./.output

ENV PORT=3000
EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
