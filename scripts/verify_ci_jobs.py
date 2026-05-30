#!/usr/bin/env python3
"""Verify required CI jobs passed for ci-aggregate job."""

import os
import sys

results = {
    "test": os.environ.get("NEEDS_TEST_RESULT", "unknown"),
    "install-smoke": os.environ.get("NEEDS_INSTALL_SMOKE_RESULT", "unknown"),
    "lint": os.environ.get("NEEDS_LINT_RESULT", "unknown"),
    "arbiter-governance": os.environ.get("NEEDS_ARBITER_GOVERNANCE_RESULT", "unknown"),
    "coverage-matrix-validate": os.environ.get("NEEDS_COVERAGE_MATRIX_VALIDATE_RESULT", "unknown"),
}

failed = 0
for job, result in results.items():
    if result != "success":
        print(f"{job} finished with result: {result}")
        failed = 1

sys.exit(failed)
