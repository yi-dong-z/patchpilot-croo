"""Prove the canonical patch turns the controlled fixture from red to green."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "demo-fixture"


def run() -> int:
    with tempfile.TemporaryDirectory(prefix="patchpilot-demo-") as directory:
        worktree = Path(directory) / "repo"
        shutil.copytree(FIXTURE, worktree)
        target = worktree / "calculator.py"
        source = target.read_text(encoding="utf-8")
        if "return total // parts" not in source:
            raise RuntimeError("controlled fixture no longer contains the expected bug")
        target.write_text(source.replace("return total // parts", "return total / parts"), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(worktree)],
            check=False,
        )
        return completed.returncode


if __name__ == "__main__":
    raise SystemExit(run())
