# Same as plastic-labs/honcho mcp/Dockerfile, but COPY paths assume the
# build context is the Honcho repo root (container-images build.yml).
FROM oven/bun:1.4.5

WORKDIR /app

RUN chown bun:bun /app
USER bun

COPY --chown=bun:bun mcp/package.json mcp/bun.lock mcp/bunfig.toml mcp/tsconfig.json ./
COPY --chown=bun:bun mcp/instructions.md ./
COPY --chown=bun:bun mcp/src ./src

RUN bun install --frozen-lockfile --production

EXPOSE 3000

ENV PORT=3000
ENV HOST=0.0.0.0

CMD ["bun", "src/http.ts"]
