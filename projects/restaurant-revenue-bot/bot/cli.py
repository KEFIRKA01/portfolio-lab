from __future__ import annotations

import argparse
from pathlib import Path

from .exports import public_case_summary
from .service import AppService
from .simulation import project

def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["overview", "seed-db", "simulate", "summary"])
    args = parser.parse_args()
    service = AppService.with_sqlite(Path(__file__).resolve().parents[1] / "seed" / "demo.sqlite3")
    if args.command == "overview":
        print(service.digest())
    elif args.command == "seed-db":
        print({"persisted": service.persist_queue()})
    elif args.command == "simulate":
        print(project(service.queue()[:3]))
    elif args.command == "summary":
        print(public_case_summary(service.queue()))

if __name__ == "__main__":
    main()
