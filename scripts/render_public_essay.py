"""Compatibility shim for lib.render_public_essay."""
from lib.render_public_essay import *  # noqa: F401, F403

if __name__ == "__main__":
    raise SystemExit(main())
