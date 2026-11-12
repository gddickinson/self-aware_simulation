"""Start the Self-Aware Simulation web app on http://127.0.0.1:8141 (local only).

Run: python run_web.py [--port 8141]
Needs: pip install -r requirements-web.txt
"""
import argparse

import uvicorn

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8141)
    port = ap.parse_args().port
    print(f"Self-Aware Simulation web app: http://127.0.0.1:{port}")
    uvicorn.run("web.app:app", host="127.0.0.1", port=port)
