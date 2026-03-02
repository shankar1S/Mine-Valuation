"""Streamlit launch entrypoint supporting both CLI styles."""

import os
import sys

from streamlit.runtime.scriptrunner import get_script_run_ctx

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from gui.dashboard import run_app


def _run_via_streamlit_cli():
    from streamlit.web import cli as stcli

    sys.argv = ["streamlit", "run", os.path.abspath(__file__)]
    raise SystemExit(stcli.main())


def main():
    # If launched as plain Python, hand off to Streamlit CLI.
    if get_script_run_ctx() is None:
        _run_via_streamlit_cli()
    import streamlit as st
    st.title("Mine Valuation Engine")
    # rest of your app code
    run_app()


if __name__ == "__main__":
    main()
