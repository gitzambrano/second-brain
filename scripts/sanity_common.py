"""Compatibility shim for lib.sanity_common."""
from lib.sanity_common import *  # noqa: F401, F403
from lib.sanity_common import main as _main

if __name__ == "__main__":
    raise SystemExit(_main())
