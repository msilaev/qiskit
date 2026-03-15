import io
import json
import base64
import numpy as np
from math import pi

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram


def _fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return b64


def _result(counts, circuit_fig, hist_fig, summary: str) -> str:
    return json.dumps({
        "summary": summary,
        "counts": counts,
        "circuit_img": _fig_to_b64(circuit_fig),
        "histogram_img": _fig_to_b64(hist_fig),
    })


def run_deutsch(oracle_type: str) -> str:
    """Run Deutsch's algorithm to determine if an oracle is constant or balanced
    with a single query. oracle_type must be one of:
      'constant_0'         — f(0)=f(1)=0
      'constant_1'         — f(0)=f(1)=1
      'balanced_identity'  — f(x)=x
      'balanced_not'       — f(x)=NOT x
    Measurement result |0⟩ means constant, |1⟩ means balanced.
    """
    valid = {'constant_0', 'constant_1', 'balanced_identity', 'balanced_not'}
    if oracle_type not in valid:
        return json.dumps({"error": f"oracle_type must be one of {valid}"})

    qc = QuantumCircuit(2, 1)
    qc.x(1)           # ancilla |1⟩
    qc.h([0, 1])
    qc.barrier(label='Init')

    if oracle_type == 'constant_0':
        pass
    elif oracle_type == 'constant_1':
        qc.x(1)
    elif oracle_type == 'balanced_identity':
        qc.cx(0, 1)
    elif oracle_type == 'balanced_not':
        qc.cx(0, 1)
        qc.x(1)

    qc.barrier(label='Oracle')
    qc.h(0)
    qc.measure(0, 0)

    backend = AerSimulator()
    counts = backend.run(transpile(qc, backend), shots=1024).result().get_counts()

    is_constant = oracle_type.startswith('constant')
    detected = 'constant' if counts.get('0', 0) > counts.get('1', 0) else 'balanced'
    correct = '✓' if (detected == 'constant') == is_constant else '✗'
    summary = (
        f"Oracle '{oracle_type}' ({('constant' if is_constant else 'balanced')}) — "
        f"detected: {detected} {correct}. "
        f"Counts: {counts}."
    )

    circuit_fig = qc.draw('mpl')
    hist_fig = plot_histogram(counts, title=f"Deutsch: {oracle_type}")
    return _result(counts, circuit_fig, hist_fig, summary)


def run_grover(target_state: str) -> str:
    """Run Grover's search algorithm on 2 qubits to find a marked state.
    One iteration gives ~100% success for N=4.
    target_state: one of '00', '01', '10', '11'.
    """
    if target_state not in {'00', '01', '10', '11'}:
        return json.dumps({"error": "target_state must be one of '00', '01', '10', '11'"})

    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    qc = QuantumCircuit(qr, cr)

    qc.h(qr)
    qc.barrier(label='H')

    # Oracle: phase-flip target state
    # In Qiskit counts, target_state[0]=qubit1 (MSB), target_state[1]=qubit0 (LSB)
    if target_state[1] == '0':
        qc.x(qr[0])
    if target_state[0] == '0':
        qc.x(qr[1])
    qc.h(qr[0])
    qc.cx(qr[1], qr[0])
    qc.h(qr[0])
    if target_state[1] == '0':
        qc.x(qr[0])
    if target_state[0] == '0':
        qc.x(qr[1])
    qc.barrier(label='Oracle')

    # Diffusion operator: 2|ψ⟩⟨ψ| - I
    qc.h(qr)
    qc.x(qr)
    qc.h(qr[0])
    qc.cx(qr[1], qr[0])
    qc.h(qr[0])
    qc.x(qr)
    qc.h(qr)
    qc.barrier(label='Diffusion')

    qc.measure(qr, cr)

    backend = AerSimulator()
    counts = backend.run(transpile(qc, backend), shots=1024).result().get_counts()

    top = max(counts, key=counts.get)
    pct = counts[top] / 10.24
    summary = (
        f"Grover search for |{target_state}⟩: "
        f"top result |{top}⟩ with {counts[top]}/1024 shots ({pct:.1f}%). "
        f"{'Success ✓' if top == target_state else 'Unexpected result ✗'}. "
        f"Full counts: {counts}."
    )

    circuit_fig = qc.draw('mpl')
    hist_fig = plot_histogram(counts, title=f"Grover: target |{target_state}⟩")
    return _result(counts, circuit_fig, hist_fig, summary)


def run_simon(secret_string: str) -> str:
    """Run Simon's algorithm to find the hidden period string b.
    Measurement results z satisfy z·b = 0 (mod 2).
    secret_string: binary string e.g. '11', '101', '110'.
    """
    if not secret_string or not all(c in '01' for c in secret_string):
        return json.dumps({"error": "secret_string must be a non-empty binary string like '11' or '101'"})

    b = secret_string
    n = len(b)

    def simon_oracle(b):
        qc = QuantumCircuit(2 * n)
        for i in range(n):
            qc.cx(i, n + i)
        for i, bit in enumerate(b):
            if bit == '1':
                qc.cx(0, n + i)
        return qc

    qc = QuantumCircuit(n * 2, n)
    qc.h(range(n))
    qc.barrier(label='H')
    qc = qc.compose(simon_oracle(b))
    qc.barrier(label='Oracle')
    qc.h(range(n))
    qc.measure(range(n), range(n))

    backend = AerSimulator()
    counts = backend.run(transpile(qc, backend), shots=1024).result().get_counts()

    b_vec = [int(c) for c in b]
    violations = [
        z for z in counts
        if sum(int(zi) * bi for zi, bi in zip(z, b_vec)) % 2 != 0
    ]
    summary = (
        f"Simon's algorithm with b='{b}': {len(counts)} distinct outcomes. "
        f"All satisfy z·b=0 (mod 2): {'✓' if not violations else '✗ violations: ' + str(violations)}. "
        f"Counts: {counts}."
    )

    circuit_fig = qc.draw('mpl', justify='none')
    hist_fig = plot_histogram(counts, title=f"Simon's algorithm: b='{b}'")
    return _result(counts, circuit_fig, hist_fig, summary)


def run_teleportation(theta_over_pi: float) -> str:
    """Run the quantum teleportation protocol.
    Teleports the state cos(θ/2)|0⟩ + sin(θ/2)|1⟩ from Alice to Bob.
    theta_over_pi: angle θ as a fraction of π. E.g. 0.333 → θ=π/3, 0.5 → θ=π/2.
    Bob's qubit should reproduce the original state with P(|0⟩)=cos²(θ/2).
    """
    theta = float(theta_over_pi) * pi

    qr = QuantumRegister(3, 'q')
    cr = ClassicalRegister(2, 'c')
    cr_bob = ClassicalRegister(1, 'bob')
    qc = QuantumCircuit(qr, cr, cr_bob)

    # Prepare message state
    qc.ry(theta, qr[0])
    qc.barrier(label='Prepare |ψ⟩')

    # Bell pair between Alice (q1) and Bob (q2)
    qc.h(qr[1])
    qc.cx(qr[1], qr[2])
    qc.barrier(label='Bell pair')

    # Alice's Bell measurement
    qc.cx(qr[0], qr[1])
    qc.h(qr[0])
    qc.barrier(label='Bell meas.')
    qc.measure(qr[0], cr[0])
    qc.measure(qr[1], cr[1])
    qc.barrier(label='Corrections')

    # Bob's corrections (Qiskit 1.x: use if_test instead of c_if)
    with qc.if_test((cr[1], 1)):
        qc.x(qr[2])
    with qc.if_test((cr[0], 1)):
        qc.z(qr[2])
    qc.measure(qr[2], cr_bob[0])

    backend = AerSimulator()
    counts = backend.run(transpile(qc, backend), shots=2048).result().get_counts()

    p0_exp = np.cos(theta / 2) ** 2
    p1_exp = np.sin(theta / 2) ** 2
    bob_0 = sum(v for k, v in counts.items() if k.split(' ')[0] == '0')
    bob_1 = sum(v for k, v in counts.items() if k.split(' ')[0] == '1')
    total = bob_0 + bob_1

    success = abs(bob_0 / total - p0_exp) < 0.05
    summary = (
        f"Teleportation of θ={theta_over_pi:.3f}π state: "
        f"expected P(|0⟩)={p0_exp:.3f}, measured={bob_0/total:.3f}. "
        f"{'Successful ✓' if success else 'Outside 5% tolerance — try more shots.'}."
    )

    circuit_fig = qc.draw('mpl')
    hist_fig = plot_histogram(counts, title=f"Teleportation θ={theta_over_pi:.2f}π")
    return _result(counts, circuit_fig, hist_fig, summary)
