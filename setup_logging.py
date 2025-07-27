#!/usr/bin/env python3
"""setup_logging.py

Example script showing how to configure logging for different environments.
Run this before starting your application to set up proper logging.
"""

import argparse
import sys
from pathlib import Path

# Add the app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config.logging_config import LoggingConfig


def main():
    parser = argparse.ArgumentParser(description='Configure logging for Recipe App')
    parser.add_argument(
        '--env', 
        choices=['development', 'testing', 'staging', 'production'],
        default='development',
        help='Environment to configure logging for'
    )
    parser.add_argument(
        '--log-file',
        help='Path to log file (optional)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode (overrides environment setting)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true', 
        help='Enable quiet mode (warnings and errors only)'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        LoggingConfig.enable_debug_mode()
    elif args.quiet:
        LoggingConfig.enable_quiet_mode()
    else:
        LoggingConfig.setup_logging(args.env, args.log_file)
    
    print(f"✅ Logging configured for {args.env} environment")
    if args.log_file:
        print(f"📝 Logging to file: {args.log_file}")


if __name__ == "__main__":
    main()