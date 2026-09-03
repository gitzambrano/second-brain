"""Compatibility shim for lib.render_public_essay."""
from lib.render_public_essay import *  # noqa: F401, F403
from lib.render_public_essay import main as _main

if __name__ == "__main__":
    raise SystemExit(_main())
