import sys
from pathlib import Path

# self_audit modules use flat imports (matching how `inspect eval` loads the
# task file, which puts self_audit/ on sys.path)
sys.path.insert(0, str(Path(__file__).parent / "self_audit"))
