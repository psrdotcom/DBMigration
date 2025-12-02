#!/usr/bin/env python3
"""
Natural language UI entrypoint for DBMigration.

Usage (from project root):

    python frontend/nl_ui.py

Or with an explicit config file:

    python frontend/nl_ui.py --config config/config.yaml
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path so imports work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.natural_language_ui import run_natural_language_ui


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Natural language UI for Oracle to PostgreSQL migration"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file (default: config/config.yaml)",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    _, _ = run_natural_language_ui(config_path=args.config)
    return 0


if __name__ == "__main__":
    sys.exit(main())



