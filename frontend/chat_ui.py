"""
Streamlit-based chatbot UI for DBMigration.

This app lets a user drive Oracle→PostgreSQL migration conversationally.
It uses OpenAI (GPT-4.x) behind the scenes through the existing
NaturalLanguagePlanner and AgentRouter.

Run from project root:

    streamlit run frontend/chat_ui.py
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path so imports work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st  # type: ignore[import]

# Initialize Oracle Client (Optional - Thick Mode)
# By default, oracledb uses Thin Mode which works on all platforms without Oracle Instant Client
# Thick Mode is only needed for advanced Oracle features
try:
    import oracledb
    import platform
    
    thick_mode_initialized = False
    
    # Try to initialize Thick Mode if Oracle Instant Client is available
    if platform.system() == "Darwin":  # macOS
        oracle_lib_paths = [
            os.getenv('ORACLE_CLIENT_LIB_DIR'),
            '/opt/oracle/instantclient_23_3',
            os.path.expanduser('~/oracle/instantclient_23_3'),
            os.path.expanduser('~/oracle/instantclient_21_1'),
        ]
        
        for lib_dir in oracle_lib_paths:
            if lib_dir and os.path.exists(lib_dir):
                try:
                    oracledb.init_oracle_client(lib_dir=lib_dir)
                    thick_mode_initialized = True
                    logging.info(f"Oracle Thick Mode initialized from: {lib_dir}")
                    break
                except Exception:
                    continue
                    
    elif platform.system() == "Linux":
        oracle_lib_paths = [
            os.getenv('ORACLE_CLIENT_LIB_DIR'),
            '/opt/oracle/instantclient_23_3',
            '/opt/oracle/instantclient_21_1',
            '/usr/lib/oracle/23.3/client64/lib',
            '/usr/lib/oracle/21.1/client64/lib',
        ]
        
        for lib_dir in oracle_lib_paths:
            if lib_dir and os.path.exists(lib_dir):
                try:
                    oracledb.init_oracle_client(lib_dir=lib_dir)
                    thick_mode_initialized = True
                    logging.info(f"Oracle Thick Mode initialized from: {lib_dir}")
                    break
                except Exception:
                    continue
                    
    elif platform.system() == "Windows":
        oracle_lib_paths = [
            os.getenv('ORACLE_CLIENT_LIB_DIR'),
            r'C:\oracle\instantclient_23_3',
            r'C:\oracle\instantclient_21_1',
        ]
        
        for lib_dir in oracle_lib_paths:
            if lib_dir and os.path.exists(lib_dir):
                try:
                    oracledb.init_oracle_client(lib_dir=lib_dir)
                    thick_mode_initialized = True
                    logging.info(f"Oracle Thick Mode initialized from: {lib_dir}")
                    break
                except Exception:
                    continue
    
    if not thick_mode_initialized:
        logging.info(f"Using Oracle Thin Mode on {platform.system()} (no client required)")
        
except ImportError:
    # oracledb not installed - that's okay if user only needs query conversion
    pass
except Exception as e:
    # Log but don't fail - Thin mode will be used automatically
    logging.info(f"Oracle Thin Mode will be used: {e}")

from src.utils.natural_language_ui import (
    NaturalLanguagePlanner,
    NLPlan,
    execute_plan,
)


logger = logging.getLogger(__name__)


def _init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, Any]] = []
    if "pending_plan" not in st.session_state:
        st.session_state.pending_plan: Optional[NLPlan] = None
    if "pending_summary" not in st.session_state:
        st.session_state.pending_summary: Optional[str] = None
    if "config_path" not in st.session_state:
        st.session_state.config_path = "config/config.yaml"


def render_sidebar() -> None:
    """Render sidebar controls."""
    st.sidebar.title("DBMigration Chatbot")
    st.sidebar.markdown(
        """
**How it works**

- You describe what you want (e.g. *"migrate all tables"*, *"validate data"*)
- The assistant interprets this into concrete migration tasks
- It shows a summary and **asks for confirmation**
- After you approve, it runs the tasks against your databases
        """
    )

    st.sidebar.markdown("---")
    config_path = st.sidebar.text_input(
        "Config file path",
        value=st.session_state.config_path,
        help="YAML config with Oracle/PostgreSQL connection details and LLM settings.",
    )
    st.session_state.config_path = config_path

    st.sidebar.markdown("---")
    st.sidebar.markdown("**OpenAI configuration**")
    st.sidebar.markdown(
        """
This app uses the same OpenAI configuration as the backend:

- Set `OPENAI_API_KEY` in your environment
- Optionally set `OPENAI_MODEL` (e.g. `gpt-4.1`)
        """
    )


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def display_chat_history() -> None:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])


def main() -> None:
    st.set_page_config(page_title="DBMigration Chatbot", page_icon="🗄️", layout="wide")
    _init_session_state()
    render_sidebar()

    st.title("Oracle → PostgreSQL Migration Chatbot")
    st.caption("Describe what you want to do in natural language; I'll plan and run the migration for you.")

    display_chat_history()

    user_input = st.chat_input("How can I help with your migration?")
    if user_input:
        add_message("user", user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                planner = NaturalLanguagePlanner()

                try:
                    plan = planner.plan_from_text(
                        user_input,
                        default_config_path=st.session_state.config_path,
                    )
                except Exception as e:
                    logger.error(f"Failed to build plan: {e}", exc_info=True)
                    error_msg = f"Sorry, I couldn't interpret that request: `{e}`"
                    st.markdown(error_msg)
                    add_message("assistant", error_msg)
                    return

                # Build a concise summary for chat
                lines: List[str] = []
                lines.append(f"**Intent:** {plan.intent}")
                lines.append("")
                lines.append("**Planned tasks:**")
                for i, t in enumerate(plan.tasks, start=1):
                    opt_parts = []
                    for k, v in t.options.items():
                        opt_parts.append(f"`{k}={v}`")
                    opts_str = ", ".join(opt_parts) if opt_parts else "_no options_"
                    lines.append(f"- {i}. `{t.type}` ({opts_str})")

                lines.append("")
                lines.append("**Equivalent CLI command:**")
                lines.append(f"`{plan.cli_command}`")

                if plan.notes:
                    lines.append("")
                    lines.append(f"**Notes:** {plan.notes}")

                lines.append("")
                lines.append(
                    "If this looks correct, click **Approve & Run** below to execute these actions. "
                    "Otherwise, you can refine your request with another message."
                )

                summary_md = "\n".join(lines)
                st.markdown(summary_md)

                # Save pending plan for approval buttons below
                st.session_state.pending_plan = plan
                st.session_state.pending_summary = summary_md

    # Render approval / cancel buttons if there is a pending plan
    if st.session_state.pending_plan is not None:
        st.markdown("---")
        cols = st.columns(2)
        with cols[0]:
            approve = st.button("✅ Approve & Run", type="primary")
        with cols[1]:
            cancel = st.button("❌ Cancel Plan")

        if approve:
            plan = st.session_state.pending_plan
            summary_md = st.session_state.pending_summary or ""

            with st.chat_message("assistant"):
                st.markdown("Running the approved plan...")
                st.markdown(summary_md)

                try:
                    results = execute_plan(plan, config_path=st.session_state.config_path)
                except Exception as e:
                    logger.error(f"Failed to execute plan: {e}", exc_info=True)
                    st.error(f"Execution failed: {e}")
                    add_message("assistant", f"Execution failed: `{e}`")
                    # Clear pending plan
                    st.session_state.pending_plan = None
                    st.session_state.pending_summary = None
                    return

                result_lines: List[str] = []
                result_lines.append("**Execution summary:**")
                for i, r in enumerate(results, start=1):
                    agent_name = r.get("agent", "Unknown")
                    status = r.get("status", "unknown")
                    message = r.get("message")
                    line = f"- {i}. Agent `{agent_name}` → status: **{status}**"
                    if message and status != "success":
                        line += f"  \n  ↳ `{message}`"
                    result_lines.append(line)

                result_md = "\n".join(result_lines)
                st.markdown(result_md)
                add_message("assistant", summary_md + "\n\n" + result_md)

            # Clear pending plan after execution
            st.session_state.pending_plan = None
            st.session_state.pending_summary = None

        elif cancel:
            with st.chat_message("assistant"):
                st.markdown("Okay, I've cancelled that plan. You can describe a new request anytime.")
            add_message(
                "assistant",
                "I've cancelled the previous plan. Please describe what you'd like to do next.",
            )
            st.session_state.pending_plan = None
            st.session_state.pending_summary = None


if __name__ == "__main__":
    main()



