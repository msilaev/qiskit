# qiskit
This repository contains Jupyter notebooks with demos and homeworks for the Introduction to Quantum Computing course:
- https://sisu.jyu.fi/student/courseunit/otm-7f81baf5-90e5-45dc-bd46-c4d04e511313/brochure
- https://sites.google.com/view/qcintro

All code targets IBM quantum processors using the Qiskit SDK: https://qiskit.org/

---

## Notebooks

### Grover2Qbit.ipynb
Implements **Grover's search algorithm** on a 2-qubit system. Constructs the oracle and diffusion (Grover) operator, runs the amplitude amplification circuit, and verifies that the target basis state is found with near-certainty after one iteration. Includes both local simulation (AerSimulator) and IBM cloud execution via `SamplerV2`.

### Quantum Teleportation.ipynb
Full implementation of the **quantum teleportation protocol**: transmits an arbitrary qubit state |ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩ from Alice to Bob using a pre-shared Bell pair and 2 classical bits. Verifies that Bob's measurement statistics match the original state. Supports both local simulation and real IBM hardware via `QiskitRuntimeService`.

### ToffoliTest1.ipynb
Tests the **Toffoli (CCX) gate** — the 3-qubit universal reversible gate. Constructs the Toffoli from primitive gates (H, CNOT, T, T†), verifies its truth table on all input states using the local AerSimulator, and demonstrates that the target qubit flips only when both controls are |1⟩.

### Simon.ipynb
Implements **Simon's algorithm** for finding the hidden period of a 2-to-1 function with period `s`. Demonstrates exponential speedup over classical approaches: finds the secret string `s` with certainty using O(n) quantum queries and classical post-processing (Gaussian elimination). Verifies the result against the known secret string.

### QFT.ipynb
Implements the **Quantum Fourier Transform** — the quantum analogue of the discrete Fourier transform, used as a subroutine in Shor's algorithm and quantum phase estimation. Verifies the circuit output against a classical DFT on random complex state vectors. Also includes a **Quantum Phase Estimation** experiment that estimates an unknown rotation angle using n counting qubits.

### Garbage_take_out.ipynb
Demonstrates **reversible computing and uncomputation** ("garbage take-out"). Shows why ancilla qubits must be uncomputed after use to avoid entanglement with the output. Implements the full V_f† ∘ copy ∘ V_f pattern and numerically verifies that the ancilla is restored to |0⟩ while the output matches the ideal U_f computation.

---

## Interactive App — app.py

A **Streamlit web application** that provides two interfaces for running quantum experiments.

### Widget mode (always available)
A dropdown-based UI for running simulations without writing code. Supported experiments:
- **Deutsch's Algorithm** — tests whether a black-box function is constant or balanced
- **Grover's Search** — searches a 2-qubit space for a target state
- **Simon's Algorithm** — finds the hidden period of a 2-to-1 function
- **Quantum Teleportation** — teleports a qubit state parameterised by a θ slider

Each experiment returns a circuit diagram and a measurement histogram rendered side-by-side.

### Chat mode (requires OpenAI API key)
A conversational interface powered by an OpenAI-backed agent. Accepts natural-language prompts such as `"Run Grover for |11⟩"` or `"Teleport theta=pi/3"` and dispatches the appropriate quantum simulation tool, returning results with explanations. The API key can be set via `.env` or entered in the sidebar.

To run:
```bash
streamlit run app.py
```
