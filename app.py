import base64
import streamlit as st

st.set_page_config(page_title="Quantum Assistant", layout="wide")
st.title("Quantum Computing Assistant")
st.caption("Ask me to run Deutsch, Grover, Simon, or Teleportation experiments.")


@st.cache_resource
def get_agent():
    from src.quantum_agent import run_agent
    return run_agent


# --- Session state ---
if "history" not in st.session_state:
    st.session_state.history = []  # [{role, content, images?}, ...]


# --- Render chat history ---
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        for img in msg.get("images", []):
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Circuit")
                st.image(base64.b64decode(img["circuit_img"]))
            with col2:
                st.caption("Results")
                st.image(base64.b64decode(img["histogram_img"]))


# --- Chat input ---
if user_input := st.chat_input("e.g. 'Run Grover for |11⟩' or 'Teleport a qubit with theta=pi/3'"):
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Running simulation..."):
            run_agent = get_agent()
            response_text, tool_results = run_agent(
                user_input,
                history=st.session_state.history[:-1],
            )

        st.markdown(response_text)

        for img in tool_results:
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Circuit")
                st.image(base64.b64decode(img["circuit_img"]))
            with col2:
                st.caption("Results")
                st.image(base64.b64decode(img["histogram_img"]))

    st.session_state.history.append({
        "role": "assistant",
        "content": response_text,
        "images": tool_results,
    })
