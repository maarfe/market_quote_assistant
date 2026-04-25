from __future__ import annotations

import subprocess
import sys

from run_multi_market import run_multi_market


def should_skip_dashboard() -> bool:
    return "--no-dashboard" in sys.argv


def main() -> None:
    print("🚀 Iniciando Market Quote Assistant...\n")

    run_multi_market()

    if should_skip_dashboard():
        print("\nDashboard ignorado (--no-dashboard).")
        return

    print("\n📊 Abrindo dashboard...\n")

    subprocess.run(
        ["streamlit", "run", "dashboard.py"],
        check=False
    )


if __name__ == "__main__":
    main()