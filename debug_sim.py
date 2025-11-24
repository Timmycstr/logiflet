"""
Debug script to trace signal propagation.
"""
from circuit_model import Circuit, Wire, Signal, SignalState
from components.gates import ANDGate
from components.io import Switch, LED
from simulation_engine import SimulationEngine
from utils.geometry import Point


# Create circuit
circuit = Circuit("Debug Circuit")

# Create components
switch1 = Switch("s1", "A", Point(0, 0))
switch2 = Switch("s2", "B", Point(0, 50))
and_gate = ANDGate("and1", "AND", Point(100, 25))
led = LED("led1", "Output", Point(200, 25))

# Add to circuit
circuit.add_component(switch1)
circuit.add_component(switch2)
circuit.add_component(and_gate)
circuit.add_component(led)

# Create wires
wire1 = Wire("w1", switch1.get_pin("out"), and_gate.get_pin("in0"))
wire2 = Wire("w2", switch2.get_pin("out"), and_gate.get_pin("in1"))
wire3 = Wire("w3", and_gate.get_pin("out"), led.get_pin("in"))

circuit.add_wire(wire1)
circuit.add_wire(wire2)
circuit.add_wire(wire3)

# Set both switches on
switch1.set_state(True)
switch2.set_state(True)

print("After setting switches:")
print(f"Switch1 out: {switch1.get_pin('out').signal.state}")
print(f"Switch2 out: {switch2.get_pin('out').signal.state}")
print(f"AND in0: {and_gate.get_pin('in0').signal.state}")
print(f"AND in1: {and_gate.get_pin('in1').signal.state}")
print(f"AND out: {and_gate.get_pin('out').signal.state}")
print(f"LED in: {led.get_pin('in').signal.state}")
print(f"LED lit: {led.lit}")
print()

# Run simulation
sim = SimulationEngine(circuit)
sim.start()
sim.step()

print("After first step:")
print(f"Switch1 out: {switch1.get_pin('out').signal.state}")
print(f"Switch2 out: {switch2.get_pin('out').signal.state}")
print(f"AND in0: {and_gate.get_pin('in0').signal.state}")
print(f"AND in1: {and_gate.get_pin('in1').signal.state}")
print(f"AND out: {and_gate.get_pin('out').signal.state}")
print(f"LED in: {led.get_pin('in').signal.state}")
print(f"LED lit: {led.lit}")
print()

sim.step()

print("After second step:")
print(f"Switch1 out: {switch1.get_pin('out').signal.state}")
print(f"Switch2 out: {switch2.get_pin('out').signal.state}")
print(f"AND in0: {and_gate.get_pin('in0').signal.state}")
print(f"AND in1: {and_gate.get_pin('in1').signal.state}")
print(f"AND out: {and_gate.get_pin('out').signal.state}")
print(f"LED in: {led.get_pin('in').signal.state}")
print(f"LED lit: {led.lit}")
