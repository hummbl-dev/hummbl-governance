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

from hummbl_governance.coordination_bus import BusWriter
import os

if __name__ == "__main__":
    if not hasattr(os, 'fork'):
        print("Skipping bus post on non-Unix platform.")
    else:
        bus = BusWriter(".governance/bus.tsv")
        bus.post("gemini-agent", "all", "TEST", "This is a test message from the Gemini agent.")
        print("Message posted to .governance/bus.tsv")
