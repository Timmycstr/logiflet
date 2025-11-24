"""
Base component classes and utilities.
"""
from circuit_model import Component, Pin, PinType, Signal, SignalState
from utils.geometry import Point
from typing import Dict, Any


class BaseGate(Component):
    """Base class for logic gates."""
    
    def __init__(self, component_id: str, label: str, position: Point, num_inputs: int = 2):
        super().__init__(component_id, label, position)
        self.num_inputs = num_inputs
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup input and output pins."""
        # Create input pins on the left
        for i in range(self.num_inputs):
            y_offset = 10 + (i * 20) if self.num_inputs > 1 else 20
            pin = Pin(
                name=f"in{i}",
                pin_type=PinType.INPUT,
                position=Point(0, y_offset)
            )
            self.add_pin(pin)
        
        # Create output pin on the right
        output_pin = Pin(
            name="out",
            pin_type=PinType.OUTPUT,
            position=Point(60, 20)
        )
        self.add_pin(output_pin)
    
    def get_input_values(self) -> list:
        """Get boolean values of all inputs."""
        values = []
        for i in range(self.num_inputs):
            pin = self.get_pin(f"in{i}")
            if pin:
                values.append(pin.signal.state == SignalState.HIGH)
            else:
                values.append(False)
        return values


class BaseFlipFlop(Component):
    """Base class for flip-flops."""
    
    def __init__(self, component_id: str, label: str, position: Point):
        super().__init__(component_id, label, position)
        self.state = False
        self.last_clock = False
    
    def detect_rising_edge(self, clock_signal: bool) -> bool:
        """Detect rising edge of clock signal."""
        rising = not self.last_clock and clock_signal
        self.last_clock = clock_signal
        return rising
    
    def detect_falling_edge(self, clock_signal: bool) -> bool:
        """Detect falling edge of clock signal."""
        falling = self.last_clock and not clock_signal
        self.last_clock = clock_signal
        return falling
