# quantum_maze_solver.py
import tkinter as tk
import random
from qiskit import QuantumCircuit, transpile
from qiskit.providers.aer import AerSimulator
from qiskit.providers.ibmq import IBMQ
from qiskit.tools.monitor import job_monitor

# --- Qiskit Grover's Search Functions ---
def build_grover_oracle(target, n):
    qc = QuantumCircuit(n)
    for i, bit in enumerate(target):
        if bit == '0':
            qc.x(i)
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    for i, bit in enumerate(target):
        if bit == '0':
            qc.x(i)
    qc.name = "Oracle"
    return qc

def build_diffusion_operator(n):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
    qc.name = "Diffusion"
    return qc

def build_grover_circuit(target_index, n=4, iterations=1):
    target_bin = format(target_index, f'0{n}b')
    qc = QuantumCircuit(n)
    qc.h(range(n))
    oracle = build_grover_oracle(target_bin, n)
    diffusion = build_diffusion_operator(n)
    for _ in range(iterations):
        qc.append(oracle, range(n))
        qc.append(diffusion, range(n))
    qc.measure_all()
    return qc

def quantum_search(target_index, n=4, iterations=1, use_hardware=False):
    qc = build_grover_circuit(target_index, n, iterations)
    if use_hardware:
        # --- Run on IBM Quantum hardware ---
        IBMQ.load_account()  # load IBMQ account 
        provider = IBMQ.get_provider(hub='ibm-q')
        backend = provider.get_backend('ibmq_qasm_simulator')  #IBM simulator
    else:
        # Run on local AerSimulator
        backend = AerSimulator()
    
    transpiled_circuit = transpile(qc, backend)
    job = backend.run(transpiled_circuit, shots=1024)
    
    if use_hardware:
        job_monitor(job)
    
    result = job.result()
    counts = result.get_counts()
    result_bitstr = max(counts, key=counts.get)
    return int(result_bitstr, 2)

# --- Tkinter Maze GUI ---
class MazeApp:
    def __init__(self, master, grid_size=4, cell_size=100):
        self.master = master
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.canvas = tk.Canvas(master, width=grid_size*cell_size, height=grid_size*cell_size)
        self.canvas.pack(padx=10, pady=10)
        self.draw_grid()
        self.goal_index = random.randint(0, grid_size*grid_size - 1)
        self.goal_row = self.goal_index // grid_size
        self.goal_col = self.goal_index % grid_size
        self.draw_goal()
        self.solve_button = tk.Button(master, text="Quantum Solve (Simulator)", command=self.quantum_solve_simulator)
        self.solve_button.pack(pady=5)
        self.status_label = tk.Label(master, text="Press the button to solve the maze")
        self.status_label.pack(pady=5)

    def draw_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="white")

    def draw_goal(self):
        x0 = self.goal_col * self.cell_size
        y0 = self.goal_row * self.cell_size
        x1 = x0 + self.cell_size
        y1 = y0 + self.cell_size
        self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", fill="red")

    def quantum_solve_simulator(self):
        # Run quantum search on local simulator
        result_index = quantum_search(self.goal_index, n=4, iterations=1, use_hardware=False)
        if result_index == self.goal_index:
            self.status_label.config(text=f"Quantum simulator found goal: index {result_index} "
                                          f"(row {result_index // self.grid_size}, col {result_index % self.grid_size})")
        else:
            self.status_label.config(text=f"Error: Got {result_index} instead of {self.goal_index}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quantum Maze Solver Demo")
    app = MazeApp(root, grid_size=4, cell_size=100)
    root.mainloop()
