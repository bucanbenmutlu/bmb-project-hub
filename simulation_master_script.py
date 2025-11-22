# simulations/quantum_teleportation.py

from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram

def build_teleportation_circuit(theta=0.8, phi=0.3):
    """
    Build a quantum teleportation circuit.
    
    We teleport an arbitrary single-qubit state:
        |ψ⟩ = cos(theta/2)|0⟩ + e^{iφ} sin(theta/2)|1⟩
    
    Qubit meanings:
        q0 : Alice's message qubit (state |ψ⟩ lives here initially)
        q1 : Alice's half of the Bell pair
        q2 : Bob's half of the Bell pair (target of teleportation)
    """

    qc = QuantumCircuit(3, 2)  # 3 qubits, 2 classical bits for Alice's measurements

    # --- 1. Prepare the input state |ψ⟩ on qubit 0 ---
    # Start in |0⟩ and rotate into some arbitrary state
    # RY(theta) sets amplitudes, RZ(phi) adds relative phase.
    qc.ry(theta, 0)
    qc.rz(phi, 0)

    # --- 2. Create a Bell pair between qubit 1 and 2 (Alice-Bob entanglement) ---
    qc.h(1)
    qc.cx(1, 2)

    # --- 3. Bell-state measurement on qubits 0 and 1 (Alice's qubits) ---
    qc.cx(0, 1)
    qc.h(0)

    # Measure Alice's two qubits
    qc.measure(0, 0)
    qc.measure(1, 1)

    # --- 4. Conditional corrections on Bob's qubit (classical feed-forward) ---
    # If the second bit (c1) is 1 → apply X
    qc.x(2).c_if(qc.cregs[0], 0b10)
    qc.x(2).c_if(qc.cregs[0], 0b11)
    # If the first bit (c0) is 1 → apply Z
    qc.z(2).c_if(qc.cregs[0], 0b01)
    qc.z(2).c_if(qc.cregs[0], 0b11)

    # Note: In a more explicit version you’d decode the bit patterns more cleanly,
    # but this keeps it simple in one classical register.

    return qc


def run_teleportation(theta=0.8, phi=0.3, shots=1024, draw=False):
    """
    Build and run the teleportation circuit on a local simulator.

    Returns:
        result: Qiskit Result object
        circuit: the QuantumCircuit used
    """
    qc = build_teleportation_circuit(theta, phi)

    # Use the qasm simulator
    backend = Aer.get_backend("qasm_simulator")
    job = execute(qc, backend=backend, shots=shots)
    result = job.result()

    if draw:
        print(qc.draw())

    return result, qc


def analyze_results(result):
    """
    Print measurement results and explain what you're seeing.
    """
    counts = result.get_counts()
    print("Measurement outcomes (on Alice's classical bits):")
    print(counts)
    print(
        "\nInterpretation:\n"
        "- The two classical bits just tell you which corrections Bob applied.\n"
        "- Regardless of the bits, Bob's final qubit (q2) ends up in the original state |ψ⟩.\n"
        "- To fully verify, you’d usually run statevector simulations or tomography.\n"
    )
    return counts


if __name__ == "__main__":
    # Example: run teleportation for a specific state
    theta = 0.8
    phi = 0.3

    result, qc = run_teleportation(theta=theta, phi=phi, shots=1024, draw=True)
    counts = analyze_results(result)

    # Optional: show a histogram if you're in a notebook / environment that supports it
    try:
        import matplotlib.pyplot as plt
        histogram = plot_histogram(counts)
        plt.show()
    except Exception as e:
        print("\nCould not display histogram (no GUI backend). This is normal in some environments.")
        print(f"Error: {e}")
