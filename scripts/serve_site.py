#!/usr/bin/env python3
"""Serve the generated public site locally for inspection.

No-argument default: serve SITE_ROOT on http://127.0.0.1:8000. Read-only.
"""
from __future__ import annotations

import argparse
import http.server
import socketserver
from functools import partial

from repo_paths import SITE_ROOT


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()

    if not SITE_ROOT.is_dir():
        raise SystemExit(f"SITE_ROOT not found: {SITE_ROOT}")

    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE_ROOT))
    with socketserver.ThreadingTCPServer(("127.0.0.1", args.port), handler) as server:
        server.allow_reuse_address = True
        print(f"Serving {SITE_ROOT} at http://127.0.0.1:{args.port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
