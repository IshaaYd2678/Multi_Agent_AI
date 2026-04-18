"""Deployment entrypoint for the Streamlit application."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


APP_FILE = Path(__file__).with_name("streamlit_app.py")


def _running_under_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
    except Exception:
        return False

    return get_script_run_ctx() is not None


def main() -> int:
    port = os.environ.get("PORT", "8501")
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_FILE),
        "--server.address",
        "0.0.0.0",
        "--server.port",
        port,
        "--server.headless",
        "true",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    if _running_under_streamlit():
        import streamlit_app  # noqa: F401
    else:
        raise SystemExit(main())
