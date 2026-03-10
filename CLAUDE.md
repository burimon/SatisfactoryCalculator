# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
python -m unittest discover -s tests -q

# Run a single test file
python -m unittest tests.test_planner -q

# Run a single test case
python -m unittest tests.test_planner.TestScaleRecipe.test_iron_ingot -q

# Lint and format (pre-commit hooks)
ruff check src/ tests/
ruff format src/ tests/
mypy src/

# Run the web server
python -m SatisfactoryCalculator
```

## Architecture

A web-based production planner for the game Satisfactory. Python backend serves a vanilla JS single-page app.

### Backend (`src/SatisfactoryCalculator/`)

- **`recipes.py`** — Central data: `Item` enum, `Recipe` frozen dataclass, and the `RECIPES` registry. All other modules derive from this.
- **`planner.py`** — Core computation engine. `PlannerNode`/`PlannerEdge`/`Workflow` dataclasses, recipe scaling with belt capacity constraints, connection imbalance detection, proportional flow allocation, and workflow serialization/validation.
- **`workflow_store.py`** — File-based JSON persistence in platform-specific app data directories (via `platformdirs`).
- **`webapp/server.py`** — `http.server`-based HTTP server. Routes: static file serving, REST API (`/api/recipes`, `/api/items`, `/api/workflows`).
- **`webapp/api.py`** — JSON payload builders for the API layer.
- **`webapp/static_assets.py`** — Bundles static CSS/JS files with the package.

### Frontend (`webapp/static/`)

Vanilla JS with ES6 modules, no framework. Canvas-based planner rendering.

- **`js/app.js`** — Bootstrap and global state (mode switching between Browser and Planner views).
- **`js/planner/`** — Planner canvas: `state.js` (centralized state), `computation.js` (rate math), `controller.js` (orchestration), `viewport.js` (pan/zoom), `interactions.js` (drag/click), `render-*.js` (drawing).
- **`js/browser/`** — Recipe browser view.
- **`js/api/client.js`** — HTTP fetch utilities.

### Key Conventions

- Rates are normalized to **per-minute**. Mining recipes produce 60/min (1/sec). Power stays in MW.
- `Recipe`, `PlannerNode`, `PlannerEdge` are **frozen dataclasses**.
- Ruff config: rules E, F, I; line length 100. MyPy targets Python 3.10.
- Tests use `unittest` (not pytest). Test files mirror source structure in `tests/`.
