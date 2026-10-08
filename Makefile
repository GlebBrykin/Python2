.PHONY: lint install run

lint:
    uv run ruff check .
    uv run ruff format --check .

install:
    uv sync

run:
    uv run database
