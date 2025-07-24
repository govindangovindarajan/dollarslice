#!/usr/bin/env python3
"""
CLI entry point for dollarslice command
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def main():
    """Main entry point - import print_slice directly to avoid heavy dependencies"""
    from print_slice import main as print_main
    print_main()

if __name__ == "__main__":
    main()