import sys
from streamlit.web import cli as stcli

if __name__ == "__main__":
    # This is the "Key" that starts the engine
    sys.argv = ["streamlit", "run", "gui/dashboard.py"]
    sys.exit(stcli.main())