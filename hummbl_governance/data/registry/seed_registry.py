"""Seed the model registry with existing artifacts."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hummbl_governance.kernel.model_registry import ModelRegistry


def main() -> None:
    reg = ModelRegistry()

    # Check if already seeded
    existing = reg.list_models()
    if existing:
        print(f"Registry already has {len(existing)} entries. Skipping seed.")
        return

    # SL-EXP003 — CPU scaling sweep
    reg.register(
        model_id="SL-EXP003",
        task="scaling_sweep",
        params_m=0.0,  # N/A for sweep
        checkpoint_path="tiny-jax-transformer/results/exp003_scaling_analysis.json",
        metrics={"alpha": 0.367, "beta": 0.128, "r_squared": 0.962},
        corpus_id="tinyshakespeare_65_vocab",
        config={
            "platform": "CPU",
            "framework": "JAX_CPU",
            "sizes": ["33K", "167K", "628K", "1.8M", "3.2M"],
            "token_budgets": [250000, 500000, 1000000, 2000000, 4000000],
        },
        hardware="AMD_Ryzen_5800X",
        framework="JAX_CPU",
        tags=["scaling_law", "chinchilla", "cpu", "dense"],
        notes="Chinchilla TinyShakespeare reconstruction on CPU. 25 configs.",
    )

    # SL-EXP004 — GPU scaling sweep
    reg.register(
        model_id="SL-EXP004",
        task="scaling_sweep",
        params_m=0.0,
        checkpoint_path="tiny-jax-transformer/sweep_gpu_20260618_000936/scaling_analysis.json",
        metrics={"alpha": 0.432, "beta": 0.381, "r_squared": 0.865},
        corpus_id="tinyshakespeare_65_vocab",
        config={
            "platform": "GPU",
            "framework": "JAX_CUDA12",
            "sizes": ["33K", "167K", "628K", "1.8M", "3.2M"],
            "token_budgets": [250000, 500000, 1000000, 2000000, 4000000],
            "batch_size": 64,
            "eval_every": 250,
        },
        hardware="RTX_3080_Ti",
        framework="JAX_CUDA12",
        tags=["scaling_law", "chinchilla", "gpu", "dense"],
        notes="Chinchilla TinyShakespeare reconstruction on GPU via WSL2. 25 configs.",
    )

    # Autoresearch best model (mar14 + later experiments)
    reg.register(
        model_id="autoresearch-mar14-best",
        task="char_lm",
        params_m=50.0,  # Approximate from depth=8 config
        checkpoint_path="autoresearch-win-rtx/checkpoints/",  # Approximate
        metrics={"val_bpb": 0.4646, "baseline_bpb": 0.8369, "improvement_pct": 44.5},
        corpus_id="tinystories_gpt4_clean",
        config={
            "depth": 8,
            "total_batch_size": 2**15,
            "window_pattern": "SSSL",
            "vocab_size": 8192,
            "optimizer": "Muon_plus_AdamW",
        },
        hardware="RTX_3080_Ti",
        framework="PyTorch",
        tags=["autoresearch", "karpathy", "tinystories", "muon"],
        notes="Best result from 110+ autoresearch experiments on RTX 3080 Ti. Batch size reduction was key.",
    )

    # HUMMBL Base Model v1 (placeholder)
    reg.register(
        model_id="hummbl-base-v1",
        task="char_lm",
        params_m=10.0,
        checkpoint_path="tiny-jax-transformer/hummbl_base_checkpoints/",
        metrics={"status": "training_queued"},
        corpus_id="hummbl_corpus_20260618",
        config={
            "embed_dim": 256,
            "num_layers": 4,
            "num_heads": 8,
            "mlp_dim": 1024,
            "vocab_size": 256,
            "max_len": 128,
            "train_tokens": 5000000,
        },
        hardware="RTX_3080_Ti",
        framework="JAX_Flax",
        tags=["hummbl", "base_model", "byte_level", "fleet_corpus"],
        notes="HUMMBL base model planned for the 6.5M-token fleet corpus. Queued for overnight training.",
    )

    # MoE experiment design (placeholder)
    reg.register(
        model_id="moe-sweep-2026-06-18",
        task="moe_experiment",
        params_m=0.0,
        checkpoint_path="tiny-jax-transformer/sweep_moe_*/",
        metrics={"status": "design_complete"},
        corpus_id="tinyshakespeare_65_vocab",
        config={
            "dense_vs_moe": True,
            "num_experts": [2, 4, 8, 16, 32],
            "top_k": 2,
            "sizes": ["200K", "1M", "3M", "6M", "10M"],
            "token_budgets": [250000, 500000, 1000000, 2000000, 4000000],
        },
        hardware="RTX_3080_Ti",
        framework="JAX_Flax",
        tags=["moe", "scaling_law", "experiment_design", "gpu"],
        notes="MoE vs dense scaling law experiment. 50 configs planned. Ready for sweep launch.",
    )

    stats = reg.stats()
    print(f"Seeded registry with {stats['count']} entries:")
    for entry in reg.list_models():
        print(f"  - {entry.model_id} ({entry.task}, {entry.params_m}M params)")


if __name__ == "__main__":
    main()
