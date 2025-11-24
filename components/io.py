"""
Input/Output components: Switch, Button, LED, Input Pin, Output Pin.
"""
from circuit_model import Component, Pin, PinType, Signal, SignalState
from utils.geometry import Point


class Switch(Component):
    """Toggle switch component."""
    
    def __init__(self, component_id: str = "", label: str = "Switch", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.state = False
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup output pin."""
        pin = Pin(
            name="out",
            pin_type=PinType.OUTPUT,
            position=Point(30, 15)
        )
        self.add_pin(pin)
    
    def evaluate(self):
        """Output current switch state."""
        self.get_pin("out").set_signal(Signal.from_bool(self.state))
    
    def toggle(self):
        """Toggle switch state."""
        self.state = not self.state
        self.evaluate()
    
    def set_state(self, state: bool):
        """Set switch state."""
        self.state = state
        self.evaluate()
    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 30, 30)


class Button(Component):
    """Push button component."""
    
    def __init__(self, component_id: str = "", label: str = "Button", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.pressed = False
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup output pin."""
        pin = Pin(
            name="out",
            pin_type=PinType.OUTPUT,
            position=Point(30, 15)
        )
        self.add_pin(pin)
    
    def evaluate(self):
        """Output current button state."""
        self.get_pin("out").set_signal(Signal.from_bool(self.pressed))
    
    def press(self):
        """Press button."""
        self.pressed = True
        self.evaluate()
    
    def release(self):
        """Release button."""
        self.pressed = False
        self.evaluate()
    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 30, 30)


class LED(Component):
    """LED indicator component."""
    
    def __init__(self, component_id: str = "", label: str = "LED", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.lit = False
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup input pin."""
        pin = Pin(
            name="in",
            pin_type=PinType.INPUT,
            position=Point(0, 15)
        )
        self.add_pin(pin)
    
    def evaluate(self):
        """Update LED state based on input."""
        input_pin = self.get_pin("in")
        self.lit = input_pin.signal.state == SignalState.HIGH

    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 30, 30)


class InputPin(Component):
    """Input pin component for circuit inputs."""
    
    def __init__(self, component_id: str = "", label: str = "In", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.value = False
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup output pin."""
        pin = Pin(
            name="out",
            pin_type=PinType.OUTPUT,
            position=Point(20, 10)
        )
        self.add_pin(pin)
    
    def evaluate(self):
        """Output current value."""
        self.get_pin("out").set_signal(Signal.from_bool(self.value))
    
    def set_value(self, value: bool):
        """Set input value."""
        self.value = value
        self.evaluate()
    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 20, 20)


class OutputPin(Component):
    """Output pin component for circuit outputs."""
    
    def __init__(self, component_id: str = "", label: str = "Out", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.value = False
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup input pin."""
        pin = Pin(
            name="in",
            pin_type=PinType.INPUT,
            position=Point(0, 10)
        )
        self.add_pin(pin)
    
    def evaluate(self):
        """Read input value."""
        input_pin = self.get_pin("in")
        self.value = input_pin.signal.state == SignalState.HIGH
    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 20, 20)


class Clock(Component):
    """Clock signal generator."""
    
    def __init__(self, component_id: str = "", label: str = "Clock", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.state = False
        self.tick_count = 0
        self.frequency = 1  # Ticks per toggle
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup output pin."""
        pin = Pin(
            name="out",
            pin_type=PinType.OUTPUT,
            position=Point(30, 15)
        )
        self.add_pin(pin)
    
    def evaluate(self):
        """Generate clock signal."""
        self.tick_count += 1
        if self.tick_count >= self.frequency:
            self.state = not self.state
            self.tick_count = 0
        self.get_pin("out").set_signal(Signal.from_bool(self.state))
    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 30, 30)
