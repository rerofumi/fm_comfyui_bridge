# AGENTS.md

## Purpose
This file defines repository-local working rules for humans and coding agents.

## Environment and toolchain
- This repository is a `uv` project.
- Run Python-related commands through `uv`.
- Do not invoke `python`, `pip`, `pytest`, or similar tools directly when `uv` equivalents are available.

## Python command rules
- Run scripts with `uv run python ...`
- Run tests with `uv run pytest ...`
- Run module entry points with `uv run ...`
- Add or update dependencies with `uv add ...`
- Remove dependencies with `uv remove ...`
- Sync or reproduce the environment with `uv sync`

## Version control rules
- This repository uses `jj` as its VCS workflow.
- Do not operate `git` directly in this repository.
- Use `jj` commands for status inspection, describing changes, branching, and other repository operations.

## Development rules
- Before creating files or running commands, confirm the current directory.
- Prefer concise, minimal changes that match the existing code style.
- Preserve backward compatibility unless the task explicitly requires a breaking change.
- Prefer adding or updating tests for changed behavior when practical.
- Keep documentation in sync when behavior, workflow, or developer usage changes.

## Project conventions
- New development for the requested redesign should follow the requirements and specifications under `plan/`.
- When validating changes in this repository, prefer `uv run pytest` for tests.
- When inspecting repository state, prefer `jj status`.
