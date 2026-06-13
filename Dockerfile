FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /task-tracker

COPY .python-version pyproject.toml uv.lock /task-tracker

RUN uv sync --frozen

COPY . /task-tracker

CMD ["sh", "-c", "uv run fastapi run main.py --port $PORT"]


