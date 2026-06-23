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

"""Tests for ModelRegistry."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from hummbl_governance.kernel.model_registry import ModelEntry, ModelRegistry


class TestModelRegistry:
    def test_register_and_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = ModelRegistry(registry_path=f"{tmp}/models.jsonl")
            entry = reg.register(
                model_id="test-model-1",
                task="char_lm",
                params_m=1.5,
                checkpoint_path="/tmp/test.msgpack",
                metrics={"val_ppl": 20.0},
            )
            assert entry.model_id == "test-model-1"
            assert entry.task == "char_lm"
            assert entry.params_m == 1.5

            models = reg.list_models()
            assert len(models) == 1
            assert models[0].model_id == "test-model-1"

    def test_find_by_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = ModelRegistry(registry_path=f"{tmp}/models.jsonl")
            reg.register(model_id="m1", task="char_lm", params_m=1.0, checkpoint_path="/a")
            reg.register(model_id="m2", task="scaling_sweep", params_m=2.0, checkpoint_path="/b")
            reg.register(model_id="m3", task="char_lm", params_m=3.0, checkpoint_path="/c")

            char_models = reg.find(task="char_lm")
            assert len(char_models) == 2
            assert {m.model_id for m in char_models} == {"m1", "m3"}

    def test_find_by_params_range(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = ModelRegistry(registry_path=f"{tmp}/models.jsonl")
            reg.register(model_id="m1", task="t", params_m=1.0, checkpoint_path="/a")
            reg.register(model_id="m2", task="t", params_m=5.0, checkpoint_path="/b")
            reg.register(model_id="m3", task="t", params_m=10.0, checkpoint_path="/c")

            results = reg.find(min_params_m=2.0, max_params_m=8.0)
            assert len(results) == 1
            assert results[0].model_id == "m2"

    def test_best_metric(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = ModelRegistry(registry_path=f"{tmp}/models.jsonl")
            reg.register(
                model_id="bad", task="t", params_m=1.0, checkpoint_path="/a",
                metrics={"val_ppl": 30.0},
            )
            reg.register(
                model_id="good", task="t", params_m=1.0, checkpoint_path="/b",
                metrics={"val_ppl": 15.0},
            )

            best = reg.best("val_ppl", higher_is_better=False)
            assert best is not None
            assert best.model_id == "good"

    def test_get_by_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = ModelRegistry(registry_path=f"{tmp}/models.jsonl")
            reg.register(model_id="target", task="t", params_m=1.0, checkpoint_path="/a")
            reg.register(model_id="other", task="t", params_m=1.0, checkpoint_path="/b")

            found = reg.get("target")
            assert found is not None
            assert found.model_id == "target"

            missing = reg.get("nonexistent")
            assert missing is None

    def test_get_by_id_returns_latest_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "models.jsonl"
            records = [
                {
                    "model_id": "target",
                    "timestamp": "2026-06-18T00:00:00Z",
                    "task": "char_lm",
                    "params_m": 1.0,
                    "checkpoint_path": "/placeholder",
                    "metrics": {"status": "training_queued"},
                },
                {
                    "model_id": "target",
                    "timestamp": "2026-06-18T06:00:00Z",
                    "task": "char_lm",
                    "params_m": 1.0,
                    "checkpoint_path": "/trained",
                    "metrics": {"val_loss": 2.5},
                },
            ]
            with path.open("w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record) + "\n")

            found = ModelRegistry(registry_path=str(path)).get("target")
            assert found is not None
            assert found.checkpoint_path == "/trained"

    def test_default_registry_path_uses_state_copy(self, tmp_path, monkeypatch):
        registry_path = tmp_path / "state" / "models.jsonl"
        monkeypatch.setenv("HUMMBL_MODEL_REGISTRY_PATH", str(registry_path))

        reg = ModelRegistry()

        assert reg.registry_path == registry_path
        assert registry_path.exists()
        assert len(reg.list_models()) >= 5

    def test_lineage(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = ModelRegistry(registry_path=f"{tmp}/models.jsonl")
            reg.register(
                model_id="ancestor", task="t", params_m=1.0, checkpoint_path="/a",
                metrics={"val_ppl": 25.0},
            )
            reg.register(
                model_id="child", task="t", params_m=1.0, checkpoint_path="/b",
                parent_id="ancestor", metrics={"val_ppl": 20.0},
            )
            reg.register(
                model_id="grandchild", task="t", params_m=1.0, checkpoint_path="/c",
                parent_id="child", metrics={"val_ppl": 18.0},
            )

            chain = reg.lineage("grandchild")
            assert len(chain) == 3
            assert [m.model_id for m in chain] == ["ancestor", "child", "grandchild"]

    def test_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = ModelRegistry(registry_path=f"{tmp}/models.jsonl")
            reg.register(model_id="m1", task="char_lm", params_m=1.0, checkpoint_path="/a")
            reg.register(model_id="m2", task="moe", params_m=2.0, checkpoint_path="/b")

            stats = reg.stats()
            assert stats["count"] == 2
            assert stats["tasks"] == {"char_lm": 1, "moe": 1}
            assert stats["total_params_m"] == 3.0

    def test_empty_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = ModelRegistry(registry_path=f"{tmp}/models.jsonl")
            assert reg.list_models() == []
            assert reg.best("val_ppl") is None
            assert reg.stats()["count"] == 0


class TestModelEntry:
    def test_roundtrip(self):
        entry = ModelEntry(
            model_id="test",
            timestamp="2026-06-18T00:00:00Z",
            task="char_lm",
            params_m=10.0,
            checkpoint_path="/tmp/test.msgpack",
            metrics={"val_ppl": 18.5},
            config={"embed_dim": 256, "num_layers": 4},
            hardware="RTX_3080_Ti",
            framework="JAX_Flax",
            tags=["base", "v1"],
        )
        d = entry.to_dict()
        restored = ModelEntry.from_dict(d)
        assert restored.model_id == entry.model_id
        assert restored.metrics["val_ppl"] == 18.5
        assert restored.config["embed_dim"] == 256
