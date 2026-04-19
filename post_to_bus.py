from hummbl_governance.coordination_bus import BusWriter
import os

if __name__ == "__main__":
    if not hasattr(os, 'fork'):
        print("Skipping bus post on non-Unix platform.")
    else:
        bus = BusWriter(".governance/bus.tsv")
        bus.post("gemini-agent", "all", "TEST", "This is a test message from the Gemini agent.")
        print("Message posted to .governance/bus.tsv")
