#!/usr/bin/env python3
"""Build wheel from sdist for install-smoke CI job."""

from pathlib import Path
import subprocess
import sys

sdists = list(Path("dist-smoke").glob("hummbl_governance-*.tar.gz"))
if len(sdists) != 1:
    raise SystemExit(f"expected exactly one sdist, found {len(sdists)}: {sdists}")
subprocess.check_call([
    sys.executable,
    "-m",
    "pip",
    "wheel",
    str(sdists[0]),
    "--no-deps",
    "--wheel-dir",
    "dist-from-sdist",
])
