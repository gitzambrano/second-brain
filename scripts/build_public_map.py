"""Compatibility shim for lib.build_public_map."""
from lib.build_public_map import *  # noqa: F401, F403
from lib.build_public_map import main as _main

if __name__ == "__main__":
    raise SystemExit(_main())
