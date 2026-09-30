# syntax=docker/dockerfile:1.7
# ── build ──
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
# --legacy-peer-deps: TypeScript is pinned to 6.x (plan §16 — TS7's native port has no JS compiler
# API yet, which openapi-typescript and vue-tsc need); their published peer range still says <6.1,
# so npm's strict resolver rejects it even though it works. `npm install` (not `ci`) accepted this
# locally; `ci` re-validates peers strictly, so the flag is needed here too.
RUN npm ci --ignore-scripts --legacy-peer-deps
COPY . .
RUN npx nuxt prepare && npm run build

# ── runtime: only the Nitro output (no node_modules needed) ──
FROM node:22-alpine AS runtime
ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --from=builder --chown=app:app /app/.output ./.output
USER app
EXPOSE 3000
HEALTHCHECK --interval=15s --timeout=3s --start-period=15s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/ >/dev/null || exit 1
CMD ["node", ".output/server/index.mjs"]
