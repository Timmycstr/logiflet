"""
Complex components: Multiplexer, Decoder, Adder, etc.
"""
from circuit_model import Component, Pin, PinType, Signal, SignalState
from utils.geometry import Point


class Multiplexer(Component):
    """Multiplexer component."""
    
    def __init__(self, component_id: str = "", label: str = "MUX", position: Point = None, num_inputs: int = 4):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.num_inputs = num_inputs
        self.num_select = (num_inputs - 1).bit_length()  # log2(num_inputs)
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup pins."""
        # Data inputs
        for i in range(self.num_inputs):
            self.add_pin(Pin(f"D{i}", PinType.INPUT, Point(0, 10 + i * 15)))
        
        # Select inputs
        for i in range(self.num_select):
            self.add_pin(Pin(f"S{i}", PinType.INPUT, Point(20, 10 + self.num_inputs * 15 + i * 15)))
        
        # Output
        self.add_pin(Pin("OUT", PinType.OUTPUT, Point(80, 10 + (self.num_inputs * 15) // 2)))
    
    def evaluate(self):
        """Evaluate multiplexer logic."""
        # Read select inputs
        select_value = 0
        for i in range(self.num_select):
            s_pin = self.get_pin(f"S{i}")
            if s_pin.signal.state == SignalState.HIGH:
                select_value |= (1 << i)
        
        # Output selected input
        if select_value < self.num_inputs:
            d_pin = self.get_pin(f"D{select_value}")
            self.get_pin("OUT").set_signal(d_pin.signal)
        else:
            self.get_pin("OUT").set_signal(Signal.from_bool(False))
    
    def get_bounds(self):
        """Get bounding box."""
        height = max(60, 20 + (self.num_inputs + self.num_select) * 15)
        return (self.position.x, self.position.y, 80, height)


class Decoder(Component):
    """Decoder component."""
    
    def __init__(self, component_id: str = "", label: str = "Decoder", position: Point = None, num_inputs: int = 2):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.num_inputs = num_inputs
        self.num_outputs = 2 ** num_inputs
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup pins."""
        # Inputs
        for i in range(self.num_inputs):
            self.add_pin(Pin(f"I{i}", PinType.INPUT, Point(0, 10 + i * 15)))
        
        # Outputs
        for i in range(self.num_outputs):
            self.add_pin(Pin(f"O{i}", PinType.OUTPUT, Point(80, 10 + i * 15)))
    
    def evaluate(self):
        """Evaluate decoder logic."""
        # Read input value
        input_value = 0
        for i in range(self.num_inputs):
            i_pin = self.get_pin(f"I{i}")
            if i_pin.signal.state == SignalState.HIGH:
                input_value |= (1 << i)
        
        # Set outputs
        for i in range(self.num_outputs):
            o_pin = self.get_pin(f"O{i}")
            o_pin.set_signal(Signal.from_bool(i == input_value))
    
    def get_bounds(self):
        """Get bounding box."""
        height = max(60, 20 + self.num_outputs * 15)
        return (self.position.x, self.position.y, 80, height)


class HalfAdder(Component):
    """Half adder component."""
    
    def __init__(self, component_id: str = "", label: str = "Half Adder", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup pins."""
        self.add_pin(Pin("A", PinType.INPUT, Point(0, 10)))
        self.add_pin(Pin("B", PinType.INPUT, Point(0, 30)))
        self.add_pin(Pin("SUM", PinType.OUTPUT, Point(80, 10)))
        self.add_pin(Pin("CARRY", PinType.OUTPUT, Point(80, 30)))
    
    def evaluate(self):
        """Evaluate half adder logic."""
        a = self.get_pin("A").signal.state == SignalState.HIGH
        b = self.get_pin("B").signal.state == SignalState.HIGH
        
        sum_out = a ^ b  # XOR
        carry_out = a and b  # AND
        
        self.get_pin("SUM").set_signal(Signal.from_bool(sum_out))
        self.get_pin("CARRY").set_signal(Signal.from_bool(carry_out))
    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 80, 50)


class FullAdder(Component):
    """Full adder component."""
    
    def __init__(self, component_id: str = "", label: str = "Full Adder", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup pins."""
        self.add_pin(Pin("A", PinType.INPUT, Point(0, 10)))
        self.add_pin(Pin("B", PinType.INPUT, Point(0, 25)))
        self.add_pin(Pin("CIN", PinType.INPUT, Point(0, 40)))
        self.add_pin(Pin("SUM", PinType.OUTPUT, Point(80, 15)))
        self.add_pin(Pin("COUT", PinType.OUTPUT, Point(80, 35)))
    
    def evaluate(self):
        """Evaluate full adder logic."""
        a = self.get_pin("A").signal.state == SignalState.HIGH
        b = self.get_pin("B").signal.state == SignalState.HIGH
        cin = self.get_pin("CIN").signal.state == SignalState.HIGH
        
        sum_out = a ^ b ^ cin
        carry_out = (a and b) or (cin and (a ^ b))
        
        self.get_pin("SUM").set_signal(Signal.from_bool(sum_out))
        self.get_pin("COUT").set_signal(Signal.from_bool(carry_out))
    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 80, 60)


class Comparator(Component):
    """Comparator component."""
    
    def __init__(self, component_id: str = "", label: str = "Comparator", position: Point = None, bit_width: int = 4):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.bit_width = bit_width
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup pins."""
        # A inputs
        for i in range(self.bit_width):
            self.add_pin(Pin(f"A{i}", PinType.INPUT, Point(0, 10 + i * 10)))
        
        # B inputs
        for i in range(self.bit_width):
            self.add_pin(Pin(f"B{i}", PinType.INPUT, Point(0, 20 + self.bit_width * 10 + i * 10)))
        
        # Outputs
        self.add_pin(Pin("EQ", PinType.OUTPUT, Point(80, 10)))  # A == B
        self.add_pin(Pin("GT", PinType.OUTPUT, Point(80, 30)))  # A > B
        self.add_pin(Pin("LT", PinType.OUTPUT, Point(80, 50)))  # A < B
    
    def evaluate(self):
        """Evaluate comparator logic."""
        # Read A value
        a_value = 0
        for i in range(self.bit_width):
            a_pin = self.get_pin(f"A{i}")
            if a_pin.signal.state == SignalState.HIGH:
                a_value |= (1 << i)
        
        # Read B value
        b_value = 0
        for i in range(self.bit_width):
            b_pin = self.get_pin(f"B{i}")
            if b_pin.signal.state == SignalState.HIGH:
                b_value |= (1 << i)
        
        # Set outputs
        self.get_pin("EQ").set_signal(Signal.from_bool(a_value == b_value))
        self.get_pin("GT").set_signal(Signal.from_bool(a_value > b_value))
        self.get_pin("LT").set_signal(Signal.from_bool(a_value < b_value))
    
    def get_bounds(self):
        """Get bounding box."""
        height = max(80, 30 + self.bit_width * 20)
        return (self.position.x, self.position.y, 80, height)
