FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml ./

RUN uv sync --frozen --extra web

FROM python:3.12-slim AS runtime

RUN groupadd --system roico && useradd --system --gid roico roico
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

USER roico
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:7860/ || exit 1

ENTRYPOINT ["roi-cropper"]
CMD ["web"]
