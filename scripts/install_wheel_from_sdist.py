#!/usr/bin/env python3
"""Install wheel built from sdist for install-smoke CI job."""

from pathlib import Path
import subprocess
import sys

wheels = list(Path("dist-from-sdist").glob("hummbl_governance-*.whl"))
if len(wheels) != 1:
    raise SystemExit(f"expected exactly one wheel, found {len(wheels)}: {wheels}")
subprocess.check_call([
    sys.executable,
    "-m",
    "pip",
    "install",
    "--force-reinstall",
    "--no-deps",
    str(wheels[0]),
])
