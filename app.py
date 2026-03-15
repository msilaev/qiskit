import os
import json
import base64
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Quantum Assistant", layout="wide")
st.title("Quantum Computing Assistant")

# Allow users to supply their own key via the sidebar
with st.sidebar:
    st.header("Settings")
    user_key = st.text_input("OpenAI API key", type="password",
                             placeholder="sk-... (optional, enables chat)")
    # Store per-session, never in os.environ (which is shared across all users)
    if user_key:
        st.session_state["openai_api_key"] = user_key

HAS_OPENAI = bool(
    st.session_state.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
)


def get_api_key() -> str:
    return st.session_state.get("openai_api_key") or os.environ.get("OPENAI_API_KEY", "")


def show_results(tool_results: list):
    for img in tool_results:
        col1, col2 = st.columns(2)
        with col1:
            st.caption("Circuit")
            st.image(base64.b64decode(img["circuit_img"]))
        with col2:
            st.caption("Results")
            st.image(base64.b64decode(img["histogram_img"]))
        st.caption(img.get("summary", ""))


# ── Widget mode (always available) ───────────────────────────────────────────

def widget_mode():
    from src.quantum_tools import run_deutsch, run_grover, run_simon, run_teleportation

    st.subheader("Run an experiment")

    experiment = st.selectbox("Experiment", [
        "Deutsch's Algorithm",
        "Grover's Search",
        "Simon's Algorithm",
        "Quantum Teleportation",
    ])

    if experiment == "Deutsch's Algorithm":
        oracle = st.selectbox("Oracle", [
            "constant_0", "constant_1", "balanced_identity", "balanced_not"
        ])
        if st.button("Run"):
            with st.spinner("Simulating..."):
                result = json.loads(run_deutsch(oracle_type=oracle))
            st.success(result["summary"])
            show_results([result])

    elif experiment == "Grover's Search":
        target = st.selectbox("Target state", ["00", "01", "10", "11"])
        if st.button("Run"):
            with st.spinner("Simulating..."):
                result = json.loads(run_grover(target_state=target))
            st.success(result["summary"])
            show_results([result])

    elif experiment == "Simon's Algorithm":
        secret = st.text_input("Secret string b (binary)", value="11")
        if st.button("Run"):
            with st.spinner("Simulating..."):
                result = json.loads(run_simon(secret_string=secret))
            if "error" in result:
                st.error(result["error"])
            else:
                st.success(result["summary"])
                show_results([result])

    elif experiment == "Quantum Teleportation":
        theta = st.slider("θ (as fraction of π)", 0.0, 2.0, 0.333, step=0.05,
                          help="Teleports state cos(θ/2)|0⟩ + sin(θ/2)|1⟩")
        st.caption(f"θ = {theta:.3f}π")
        if st.button("Run"):
            with st.spinner("Simulating..."):
                result = json.loads(run_teleportation(theta_over_pi=theta))
            st.success(result["summary"])
            show_results([result])


# ── Chat mode (requires OPENAI_API_KEY) ──────────────────────────────────────

@st.cache_resource
def get_agent():
    from src.quantum_agent import run_agent
    return run_agent


def chat_mode():
    if "history" not in st.session_state:
        st.session_state.history = []

    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            show_results(msg.get("images", []))

    if user_input := st.chat_input("e.g. 'Run Grover for |11⟩' or 'Teleport theta=pi/3'"):
        st.session_state.history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Running simulation..."):
                run_agent = get_agent()
                response_text, tool_results = run_agent(
                    user_input,
                    history=st.session_state.history[:-1],
                    api_key=get_api_key(),
                )
            st.markdown(response_text)
            show_results(tool_results)

        st.session_state.history.append({
            "role": "assistant",
            "content": response_text,
            "images": tool_results,
        })


# ── Mode selector ─────────────────────────────────────────────────────────────

if HAS_OPENAI:
    tab1, tab2 = st.tabs(["Chat", "Experiments"])
    with tab1:
        chat_mode()
    with tab2:
        widget_mode()
else:
    st.caption("Set OPENAI_API_KEY in .env to enable the chat interface.")
    widget_mode()
