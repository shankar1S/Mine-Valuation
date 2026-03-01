"""
Streamlit launch entrypoint.

Supports:
- streamlit run launch.py
- python3 launch.py
"""

import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gui.dashboard import run_app

def main():
    run_app()


if __name__ == "__main__":
    main()
