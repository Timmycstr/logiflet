"""
Logic gate components: AND, OR, NOT, XOR, NAND, NOR, XNOR, Buffer.
"""
from components.base import BaseGate
from circuit_model import Signal, SignalState
from utils.geometry import Point


class ANDGate(BaseGate):
    """AND gate component."""
    
    def __init__(self, component_id: str = "", label: str = "AND", position: Point = None, num_inputs: int = 2):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position, num_inputs)
    
    def evaluate(self):
        """Evaluate AND logic."""
        inputs = self.get_input_values()
        result = all(inputs) if inputs else False
        self.get_pin("out").set_signal(Signal.from_bool(result))


class ORGate(BaseGate):
    """OR gate component."""
    
    def __init__(self, component_id: str = "", label: str = "OR", position: Point = None, num_inputs: int = 2):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position, num_inputs)
    
    def evaluate(self):
        """Evaluate OR logic."""
        inputs = self.get_input_values()
        result = any(inputs) if inputs else False
        self.get_pin("out").set_signal(Signal.from_bool(result))


class NOTGate(BaseGate):
    """NOT gate (inverter) component."""
    
    def __init__(self, component_id: str = "", label: str = "NOT", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position, num_inputs=1)
    
    def evaluate(self):
        """Evaluate NOT logic."""
        inputs = self.get_input_values()
        result = not inputs[0] if inputs else True
        self.get_pin("out").set_signal(Signal.from_bool(result))


class XORGate(BaseGate):
    """XOR gate component."""
    
    def __init__(self, component_id: str = "", label: str = "XOR", position: Point = None, num_inputs: int = 2):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position, num_inputs)
    
    def evaluate(self):
        """Evaluate XOR logic."""
        inputs = self.get_input_values()
        result = sum(inputs) % 2 == 1 if inputs else False
        self.get_pin("out").set_signal(Signal.from_bool(result))


class NANDGate(BaseGate):
    """NAND gate component."""
    
    def __init__(self, component_id: str = "", label: str = "NAND", position: Point = None, num_inputs: int = 2):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position, num_inputs)
    
    def evaluate(self):
        """Evaluate NAND logic."""
        inputs = self.get_input_values()
        result = not all(inputs) if inputs else True
        self.get_pin("out").set_signal(Signal.from_bool(result))


class NORGate(BaseGate):
    """NOR gate component."""
    
    def __init__(self, component_id: str = "", label: str = "NOR", position: Point = None, num_inputs: int = 2):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position, num_inputs)
    
    def evaluate(self):
        """Evaluate NOR logic."""
        inputs = self.get_input_values()
        result = not any(inputs) if inputs else True
        self.get_pin("out").set_signal(Signal.from_bool(result))


class XNORGate(BaseGate):
    """XNOR gate component."""
    
    def __init__(self, component_id: str = "", label: str = "XNOR", position: Point = None, num_inputs: int = 2):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position, num_inputs)
    
    def evaluate(self):
        """Evaluate XNOR logic."""
        inputs = self.get_input_values()
        result = sum(inputs) % 2 == 0 if inputs else True
        self.get_pin("out").set_signal(Signal.from_bool(result))


class BufferGate(BaseGate):
    """Buffer gate component."""
    
    def __init__(self, component_id: str = "", label: str = "BUF", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position, num_inputs=1)
    
    def evaluate(self):
        """Evaluate buffer logic (pass-through)."""
        inputs = self.get_input_values()
        result = inputs[0] if inputs else False
        self.get_pin("out").set_signal(Signal.from_bool(result))
