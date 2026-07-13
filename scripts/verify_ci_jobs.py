#!/usr/bin/env python3
# Copyright 2024-2026 HUMMBL, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

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
