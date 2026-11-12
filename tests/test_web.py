"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web import headless  # noqa: E402
from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


FIXTURE = ROOT / "tests" / "fixtures" / "sim_runs.json"


def _close(a, b, path=""):
    """Deep comparison with rtol 1e-9 for numbers (libm differs in the last bit between platforms)."""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        assert abs(a - b) <= 1e-9 * max(1, abs(a), abs(b)), f"{path}: {a} vs {b}"
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), f"{path}: length"
        for i, (x, y) in enumerate(zip(a, b)):
            _close(x, y, f"{path}[{i}]")
    elif isinstance(a, dict):
        assert isinstance(b, dict) and sorted(a) == sorted(b), f"{path}: keys"
        for k in a:
            _close(a[k], b[k], f"{path}.{k}")
    else:
        assert a == b, f"{path}: {a!r} vs {b!r}"


def test_fixture_is_current():
    """The JS reference fixture still matches the Python game (first frames of two runs, one with user actions)."""
    import json
    sys.path.insert(0, str(ROOT / "scripts"))
    import make_sim_fixture
    fixture = json.loads(FIXTURE.read_text())
    assert fixture["rng"] == make_sim_fixture.rng_streams()
    for i, steps in ((0, 600), (4, 1200)):
        want = fixture["runs"][i]
        spec = make_sim_fixture.RUNS[i]
        got = headless.run(spec["seed"], steps, every=fixture["every"], actions=spec.get("actions", ()))
        _close(got["init"], want["init"], "init")
        _close(got["snaps"], want["snaps"][:len(got["snaps"])], "snaps")
        assert got["events"] == [e for e in want["events"] if e[0] < steps]


def test_run_endpoint_matches_headless_and_validates():
    r = client.get("/api/run/3?steps=200&every=100")
    assert r.status_code == 200
    body = r.json()
    assert body["seed"] == 3 and [s["step"] for s in body["snaps"]] == [100, 200]
    assert len(body["init"]["chars"]) == 15 and len(body["init"]["zones"]) == 6
    assert client.get("/api/run/3?steps=0").status_code == 400
    assert client.get("/api/run/3?steps=9000").status_code == 400


def test_headless_leaves_logging_and_clock_alone():
    import logging
    import pygame
    before = (logging.getLogger().handlers[:], pygame.time.get_ticks)
    headless.run(1, 10, every=10)
    assert logging.getLogger().handlers == before[0] and pygame.time.get_ticks is before[1]


def test_info_reads_python_enums():
    info = client.get("/api/info").json()
    assert info["stages"][0] == "UNAWARE" and info["stages"][-1] == "TRANSCENDED"
    assert "WEATHER" in info["deity_powers"] and info["frames_per_day"] == 1500
