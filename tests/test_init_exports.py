import hummbl_governance

def test_init_exports_all_present():
    """Verify all symbols in __all__ are importable and present in the module."""
    for symbol in hummbl_governance.__all__:
        assert hasattr(hummbl_governance, symbol), f"Symbol {symbol} listed in __all__ but missing from module"

def test_version_canonical():
    """Verify version matches expected v0.5.0."""
    assert hummbl_governance.__version__ == "0.5.0"

def test_new_primitives_exported():
    """Verify v0.4.0 and v0.5.0 primitives are exported."""
    assert "KinematicGovernor" in hummbl_governance.__all__
    assert "pHRISafetyMonitor" in hummbl_governance.__all__
    assert "PhysicalSafetyMode" in hummbl_governance.__all__
    assert "eal_validate" in hummbl_governance.__all__
    assert "LamportTimestamp" in hummbl_governance.__all__
