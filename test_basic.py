"""
Test script to verify basic functionality.
"""
from circuit_model import Circuit, Wire, Signal, SignalState
from components.gates import ANDGate, ORGate, NOTGate
from components.io import Switch, LED
from simulation_engine import SimulationEngine
from utils.geometry import Point
from prompt_parser.parser import PromptParser


def test_basic_gates():
    """Test basic logic gates."""
    print("Testing basic gates...")
    
    # Create circuit
    circuit = Circuit("Test Circuit")
    
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
    
    # Test simulation
    sim = SimulationEngine(circuit)
    sim.start()
    
    # Test case 1: Both switches off
    switch1.set_state(False)
    switch2.set_state(False)
    sim.step()
    sim.step()  # Extra step to ensure propagation
    assert not led.lit, "LED should be off when both inputs are off"
    print("✓ Test 1 passed: 0 AND 0 = 0")
    
    # Test case 2: One switch on
    switch1.set_state(True)
    switch2.set_state(False)
    sim.step()
    sim.step()  # Extra step to ensure propagation
    assert not led.lit, "LED should be off when one input is off"
    print("✓ Test 2 passed: 1 AND 0 = 0")
    
    # Test case 3: Both switches on
    switch1.set_state(True)
    switch2.set_state(True)
    sim.step()
    sim.step()  # Extra step to ensure propagation
    sim.step()  # One more for LED to see the result
    assert led.lit, "LED should be on when both inputs are on"
    print("✓ Test 3 passed: 1 AND 1 = 1")
    
    print("✅ All basic gate tests passed!\n")




def test_prompt_parser():
    """Test prompt parser."""
    print("Testing prompt parser...")
    
    circuit = Circuit("Prompt Test")
    parser = PromptParser(circuit)
    
    # Test adding component
    success, msg = parser.parse_and_execute("add switch")
    assert success, f"Failed to add switch: {msg}"
    print(f"✓ Test 1 passed: {msg}")
    
    # Test creating component
    success, msg = parser.parse_and_execute("create led")
    assert success, f"Failed to create LED: {msg}"
    print(f"✓ Test 2 passed: {msg}")
    
    # Test template
    success, msg = parser.parse_and_execute("half adder")
    assert success, f"Failed to create half adder: {msg}"
    print(f"✓ Test 3 passed: {msg}")
    
    # Test list command
    success, msg = parser.parse_and_execute("list")
    assert success, f"Failed to list components: {msg}"
    print(f"✓ Test 4 passed: List command works")
    
    # Test clear
    success, msg = parser.parse_and_execute("clear")
    assert success, f"Failed to clear circuit: {msg}"
    assert len(circuit.components) == 0, "Circuit should be empty after clear"
    print(f"✓ Test 5 passed: {msg}")
    
    print("✅ All prompt parser tests passed!\n")


def test_file_operations():
    """Test file save/load."""
    print("Testing file operations...")
    
    from file_handler import FileHandler
    
    # Create a simple circuit
    circuit = Circuit("Save Test")
    switch = Switch("s1", "Input", Point(50, 50))
    led = LED("l1", "Output", Point(150, 50))
    
    circuit.add_component(switch)
    circuit.add_component(led)
    
    wire = Wire("w1", switch.get_pin("out"), led.get_pin("in"))
    circuit.add_wire(wire)
    
    # Save
    filename = "/tmp/test_circuit.lgsim"
    success = FileHandler.save_circuit(circuit, filename)
    assert success, "Failed to save circuit"
    print(f"✓ Test 1 passed: Circuit saved to {filename}")
    
    # Load
    loaded_circuit = FileHandler.load_circuit(filename)
    assert loaded_circuit is not None, "Failed to load circuit"
    assert len(loaded_circuit.components) == 2, "Loaded circuit should have 2 components"
    assert len(loaded_circuit.wires) == 1, "Loaded circuit should have 1 wire"
    print(f"✓ Test 2 passed: Circuit loaded successfully")
    
    print("✅ All file operation tests passed!\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Logisim Clone - Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_basic_gates()
        test_prompt_parser()
        test_file_operations()
        
        print("=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
