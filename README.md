# Agentic Quantum Computing Assistant
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A Streamlit web app for running and exploring quantum computing experiments — no coding required. Powered by an AI agent that understands natural-language requests and executes Qiskit simulations on demand.

**Live demo:** [qiskit-zcjbmoxzjpi7kmoqyrnsdb.streamlit.app](https://qiskit-zcjbmoxzjpi7kmoqyrnsdb.streamlit.app/)

Built with [Qiskit](https://qiskit.org/) and IBM quantum processors.

---

## App — app.py

### Chat mode (requires OpenAI API key)
A conversational interface powered by an OpenAI-backed agent. Describe what you want in plain English and the agent dispatches the appropriate quantum simulation tool, returning a circuit diagram, measurement histogram, and explanation.

Example prompts:
- `"Run Grover search for |11⟩"`
- `"Teleport a qubit with theta = pi/3"`
- `"Show me Simon's algorithm with secret string 11"`

The API key can be set via a `.env` file or entered directly in the sidebar.

### Widget mode (always available)
A dropdown-based UI for running simulations without an API key or writing any code. Select an experiment, adjust parameters, and get a circuit diagram and histogram side-by-side.

Supported experiments:
- **Deutsch's Algorithm** — determines whether a black-box function is constant or balanced
- **Grover's Search** — searches a 2-qubit space for a marked target state
- **Simon's Algorithm** — finds the hidden period of a 2-to-1 function
- **Quantum Teleportation** — teleports a qubit state parameterised by a θ slider

### Running locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

Set your OpenAI API key in a `.env` file:
```
OPENAI_API_KEY=sk-...
```

---

## Course Notebooks

The `notebooks/` folder contains homework assignments for the [Introduction to Quantum Computing](https://sites.google.com/view/qcintro) course at the University of Jyväskylä ([course page](https://sisu.jyu.fi/student/courseunit/otm-7f81baf5-90e5-45dc-bd46-c4d04e511313/brochure)). Each notebook implements a key quantum algorithm from scratch using Qiskit, with verification against classical results and optional execution on real IBM hardware via `QiskitRuntimeService`.

### Grover2Qbit.ipynb
Implements **Grover's search algorithm** on a 2-qubit system. Constructs the oracle and diffusion operator, runs amplitude amplification, and verifies the target state is found with near-certainty after one iteration. Includes IBM cloud execution via `SamplerV2`.

### Quantum Teleportation.ipynb
Full implementation of the **quantum teleportation protocol**: transmits |ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩ from Alice to Bob using a Bell pair and 2 classical bits. Verifies Bob's measurement statistics match the original state on both simulator and real IBM hardware.

### ToffoliTest1.ipynb
Constructs the **Toffoli (CCX) gate** from primitive gates (H, CNOT, T, T†) and verifies its truth table on all input states — demonstrating the 3-qubit universal reversible gate.

### Simon.ipynb
Implements **Simon's algorithm** for finding a hidden period `s` of a 2-to-1 function. Demonstrates exponential quantum speedup, recovering `s` with certainty using O(n) queries and classical Gaussian elimination.

### QFT.ipynb
Implements the **Quantum Fourier Transform** and verifies it against a classical DFT on random complex state vectors. Also includes **Quantum Phase Estimation**, estimating an unknown rotation angle using n counting qubits.

### Garbage_take_out.ipynb
Demonstrates **reversible computing and uncomputation**. Shows why ancilla qubits must be uncomputed after use (the "garbage take-out" pattern) and numerically verifies that the V_f† ∘ copy ∘ V_f circuit restores the ancilla to |0⟩ without disturbing the output.
