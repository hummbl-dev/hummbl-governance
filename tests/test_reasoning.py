import json
import tempfile
from pathlib import Path

from hummbl_governance.reasoning import ReasoningEngine


def test_reasoning_engine_loads_models():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
        models = [
            {
                "code": "DE1",
                "name": "5 Whys",
                "transformation": "Decomposition",
                "definition": "Deep root cause analysis",
            },
            {
                "code": "S1",
                "name": "Systems Thinking",
                "transformation": "Systems",
                "definition": "Feedback loops",
            },
        ]
        json.dump(models, tf)
        tf_path = Path(tf.name)

    try:
        engine = ReasoningEngine(models_path=tf_path)
        assert len(engine.models) == 2
        assert engine.get_model("DE1").name == "5 Whys"
    finally:
        tf_path.unlink()


def test_generate_system_prompt():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
        models = [
            {
                "code": "DE1",
                "name": "5 Whys",
                "transformation": "Decomposition",
                "definition": "Deep root cause analysis",
            },
            {
                "code": "P1",
                "name": "First Principles",
                "transformation": "Perspective",
                "definition": "Reducing to axioms",
            },
        ]
        json.dump(models, tf)
        tf_path = Path(tf.name)

    try:
        engine = ReasoningEngine(models_path=tf_path)
        prompt = engine.generate_system_prompt("DE1", depth=3)
        assert "DE1" in prompt
        assert "why_5" in prompt

        prompt_p1 = engine.generate_system_prompt("P1")
        assert "axioms" in prompt_p1
    finally:
        tf_path.unlink()


def test_parse_llm_output():
    engine = ReasoningEngine()
    output = """
    ```json
    {
        "analysis": {"step1": "test"},
        "recommendation": "Do it",
        "confidence": 0.9
    }
    ```
    """
    result = engine.parse_llm_output("DE1", output)
    assert result.confidence == 0.9
    assert result.recommendation == "Do it"
    assert result.analysis["step1"] == "test"


def test_parse_invalid_output_graceful():
    engine = ReasoningEngine()
    result = engine.parse_llm_output("DE1", "not json")
    assert result.confidence == 0.0
    assert "error" in result.analysis
