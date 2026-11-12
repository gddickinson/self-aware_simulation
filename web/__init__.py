"""Web interface for the Self-Aware Simulation.

Contents:
- app.py: FastAPI app (front end in static/, JSON API under /api, STATIC_ENDPOINTS for the GitHub Pages export)
- headless.py: seeded, fixed-step run of the real game without drawing (the reference for the JS engine)
- snapshot.py: JSON snapshots of the game state, mirrored by static/sim_engine.js
- static/: plain ES-module front end; sim_*.js is the browser port of the simulation
"""
