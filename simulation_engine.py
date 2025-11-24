"""
Simulation engine for circuit evaluation and signal propagation.
"""
from typing import List, Set, Dict
from collections import deque
from circuit_model import Circuit, Component, Wire, Signal, SignalState, PinType
from utils.constants import SIM_MAX_PROPAGATION_DEPTH


class SimulationEngine:
    """Manages circuit simulation and signal propagation."""
    
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.running = False
        self.tick_count = 0
        self.propagation_queue: deque = deque()
        self.evaluated_components: Set[str] = set()
    
    def reset(self):
        """Reset simulation state."""
        self.tick_count = 0
        self.propagation_queue.clear()
        self.evaluated_components.clear()
        
        # Reset all signals to unknown
        for component in self.circuit.components.values():
            for pin in component.pins.values():
                pin.signal = Signal(SignalState.UNKNOWN)
        
        for wire in self.circuit.wires.values():
            wire.signal = Signal(SignalState.UNKNOWN)
    
    def start(self):
        """Start continuous simulation."""
        self.running = True
        self.reset()
    
    def stop(self):
        """Stop simulation."""
        self.running = False
    
    def step(self):
        """Execute one simulation step."""
        self.tick_count += 1
        self.evaluated_components.clear()
        
        # Propagate signals through wires FIRST
        self._propagate_signals()
        
        # Then evaluate all components
        self._evaluate_circuit()
        
        # Propagate again after evaluation
        self._propagate_signals()
    
    def _evaluate_circuit(self):
        """Evaluate all components in the circuit."""
        # Build dependency graph and evaluate in topological order
        # For simplicity, we'll use iterative evaluation with a fixed number of passes
        
        max_iterations = SIM_MAX_PROPAGATION_DEPTH
        iteration = 0
        
        while iteration < max_iterations:
            changed = False
            
            for component in self.circuit.components.values():
                try:
                    # Store old output values
                    old_outputs = {}
                    for pin in component.get_output_pins():
                        old_outputs[pin.name] = pin.signal.state
                    
                    # Evaluate component
                    component.evaluate()
                    
                    # Check if outputs changed
                    for pin in component.get_output_pins():
                        if old_outputs.get(pin.name) != pin.signal.state:
                            changed = True
                    
                except Exception as e:
                    print(f"Error evaluating component {component.id}: {e}")
            
            iteration += 1
            
            # If nothing changed, we've reached steady state
            if not changed:
                break
        
        if iteration >= max_iterations:
            print(f"Warning: Simulation did not converge after {max_iterations} iterations")
    
    def _propagate_signals(self):
        """Propagate signals through all wires."""
        for wire in self.circuit.wires.values():
            wire.propagate()
    
    def set_input(self, component_id: str, pin_name: str, value: bool):
        """Set an input value (for switches, buttons, etc.)."""
        component = self.circuit.get_component(component_id)
        if component:
            pin = component.get_pin(pin_name)
            if pin and pin.pin_type == PinType.INPUT:
                pin.signal = Signal.from_bool(value)
    
    def get_output(self, component_id: str, pin_name: str) -> Signal:
        """Get an output signal value."""
        component = self.circuit.get_component(component_id)
        if component:
            pin = component.get_pin(pin_name)
            if pin:
                return pin.signal
        return Signal(SignalState.UNKNOWN)
    
    def toggle_input(self, component_id: str, pin_name: str):
        """Toggle an input value."""
        component = self.circuit.get_component(component_id)
        if component:
            pin = component.get_pin(pin_name)
            if pin and pin.pin_type == PinType.INPUT:
                current = pin.signal.state == SignalState.HIGH
                pin.signal = Signal.from_bool(not current)
