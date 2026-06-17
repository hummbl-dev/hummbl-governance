import hummbl_governance

def test_init_exports_all_present():
    """Verify all symbols in __all__ are importable and present in the module."""
    for symbol in hummbl_governance.__all__:
        assert hasattr(hummbl_governance, symbol), f"Symbol {symbol} listed in __all__ but missing from module"

def test_version_canonical():
    """Verify version matches current release."""
    assert hummbl_governance.__version__ == "1.2.0"

def test_new_primitives_exported():
    """Verify v0.4.0, v0.5.0, and v0.6.0 primitives are exported."""
    assert "KinematicGovernor" in hummbl_governance.__all__
    assert "pHRISafetyMonitor" in hummbl_governance.__all__
    assert "PhysicalSafetyMode" in hummbl_governance.__all__
    assert "eal_validate" in hummbl_governance.__all__
    assert "LamportTimestamp" in hummbl_governance.__all__


def test_kernel_primitives_exported():
    """Verify v1.2.0 Kernel primitives are exported."""
    assert "Kernel" in hummbl_governance.__all__
    assert "KernelInvariant" in hummbl_governance.__all__
    assert "KernelPanic" in hummbl_governance.__all__
    assert "Receipt" in hummbl_governance.__all__
    assert "ReceiptEngine" in hummbl_governance.__all__
    assert "LawEngine" in hummbl_governance.__all__
    assert "IdentityEngine" in hummbl_governance.__all__
    assert "SequenceEngine" in hummbl_governance.__all__
    assert "EvidenceEngine" in hummbl_governance.__all__
    assert "AuthorityEngine" in hummbl_governance.__all__
    assert "ScheduleEngine" in hummbl_governance.__all__
<<<<<<< HEAD
    assert "DoctrineEngine" in hummbl_governance.__all__
    assert "Stage" in hummbl_governance.__all__
=======
>>>>>>> 675d140 (feat: extract Kernel governance OS as v1.1.0)
