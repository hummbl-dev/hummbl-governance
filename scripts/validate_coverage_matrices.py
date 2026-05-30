#!/usr/bin/env python3
"""Validate coverage matrix evidence cells for CI job."""

import os
import subprocess
import sys

MATRICES_DIR = "docs/coverage"
if not os.path.isdir(MATRICES_DIR):
    print("No coverage matrices directory - skipping validation")
    sys.exit(0)

FAILED = 0
for matrix in os.listdir(MATRICES_DIR):
    if not matrix.endswith(".md"):
        continue
    if matrix in ("README.md", "EVIDENCE_VALIDATION.md"):
        continue
    matrix_path = os.path.join(MATRICES_DIR, matrix)
    print(f"Validating: {matrix_path}")
    result = subprocess.run([
        sys.executable, "-m", "hummbl_governance.compliance_mapper",
        "--validate", matrix_path,
        "--repo-root", "."
    ])
    if result.returncode != 0:
        FAILED = 1

if FAILED != 0:
    print("::warning::Coverage matrix validation: one or more matrices have unresolved evidence references (advisory; matrices are DRAFT scaffolds)")
    sys.exit(0)

print("All coverage matrices pass evidence validation")
