"""
Memory components: D Flip-Flop, JK Flip-Flop, SR Latch, Register.
"""
from components.base import BaseFlipFlop
from circuit_model import Component, Pin, PinType, Signal, SignalState
from utils.geometry import Point


class DFlipFlop(BaseFlipFlop):
    """D Flip-Flop component."""
    
    def __init__(self, component_id: str = "", label: str = "D-FF", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup pins."""
        # D input
        self.add_pin(Pin("D", PinType.INPUT, Point(0, 10)))
        # Clock input
        self.add_pin(Pin("CLK", PinType.INPUT, Point(0, 30)))
        # Q output
        self.add_pin(Pin("Q", PinType.OUTPUT, Point(60, 10)))
        # Q' output
        self.add_pin(Pin("Q'", PinType.OUTPUT, Point(60, 30)))
    
    def evaluate(self):
        """Evaluate D flip-flop logic."""
        d_pin = self.get_pin("D")
        clk_pin = self.get_pin("CLK")
        q_pin = self.get_pin("Q")
        qn_pin = self.get_pin("Q'")
        
        clock = clk_pin.signal.state == SignalState.HIGH
        
        # On rising edge, capture D input
        if self.detect_rising_edge(clock):
            self.state = d_pin.signal.state == SignalState.HIGH
        
        # Output current state
        q_pin.set_signal(Signal.from_bool(self.state))
        qn_pin.set_signal(Signal.from_bool(not self.state))
    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 60, 50)


class JKFlipFlop(BaseFlipFlop):
    """JK Flip-Flop component."""
    
    def __init__(self, component_id: str = "", label: str = "JK-FF", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup pins."""
        self.add_pin(Pin("J", PinType.INPUT, Point(0, 10)))
        self.add_pin(Pin("K", PinType.INPUT, Point(0, 20)))
        self.add_pin(Pin("CLK", PinType.INPUT, Point(0, 40)))
        self.add_pin(Pin("Q", PinType.OUTPUT, Point(60, 10)))
        self.add_pin(Pin("Q'", PinType.OUTPUT, Point(60, 40)))
    
    def evaluate(self):
        """Evaluate JK flip-flop logic."""
        j_pin = self.get_pin("J")
        k_pin = self.get_pin("K")
        clk_pin = self.get_pin("CLK")
        q_pin = self.get_pin("Q")
        qn_pin = self.get_pin("Q'")
        
        j = j_pin.signal.state == SignalState.HIGH
        k = k_pin.signal.state == SignalState.HIGH
        clock = clk_pin.signal.state == SignalState.HIGH
        
        # On rising edge
        if self.detect_rising_edge(clock):
            if j and k:
                self.state = not self.state  # Toggle
            elif j:
                self.state = True  # Set
            elif k:
                self.state = False  # Reset
            # else: hold current state
        
        q_pin.set_signal(Signal.from_bool(self.state))
        qn_pin.set_signal(Signal.from_bool(not self.state))
    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 60, 60)


class SRLatch(Component):
    """SR Latch component."""
    
    def __init__(self, component_id: str = "", label: str = "SR Latch", position: Point = None):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.state = False
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup pins."""
        self.add_pin(Pin("S", PinType.INPUT, Point(0, 10)))
        self.add_pin(Pin("R", PinType.INPUT, Point(0, 30)))
        self.add_pin(Pin("Q", PinType.OUTPUT, Point(60, 10)))
        self.add_pin(Pin("Q'", PinType.OUTPUT, Point(60, 30)))
    
    def evaluate(self):
        """Evaluate SR latch logic."""
        s_pin = self.get_pin("S")
        r_pin = self.get_pin("R")
        q_pin = self.get_pin("Q")
        qn_pin = self.get_pin("Q'")
        
        s = s_pin.signal.state == SignalState.HIGH
        r = r_pin.signal.state == SignalState.HIGH
        
        if s and not r:
            self.state = True  # Set
        elif r and not s:
            self.state = False  # Reset
        # If both S and R are high, state is undefined (we'll keep current state)
        # If both are low, hold current state
        
        q_pin.set_signal(Signal.from_bool(self.state))
        qn_pin.set_signal(Signal.from_bool(not self.state))
    
    def get_bounds(self):
        """Get bounding box."""
        return (self.position.x, self.position.y, 60, 50)


class Register(Component):
    """Multi-bit register component."""
    
    def __init__(self, component_id: str = "", label: str = "Register", position: Point = None, bit_width: int = 4):
        if position is None:
            position = Point(0, 0)
        super().__init__(component_id, label, position)
        self.bit_width = bit_width
        self.value = 0
        self.last_clock = False
        self._setup_pins()
    
    def _setup_pins(self):
        """Setup pins."""
        # Data inputs
        for i in range(self.bit_width):
            self.add_pin(Pin(f"D{i}", PinType.INPUT, Point(0, 10 + i * 10)))
        
        # Clock input
        self.add_pin(Pin("CLK", PinType.INPUT, Point(0, 10 + self.bit_width * 10)))
        
        # Data outputs
        for i in range(self.bit_width):
            self.add_pin(Pin(f"Q{i}", PinType.OUTPUT, Point(80, 10 + i * 10)))
    
    def evaluate(self):
        """Evaluate register logic."""
        clk_pin = self.get_pin("CLK")
        clock = clk_pin.signal.state == SignalState.HIGH
        
        # Detect rising edge
        rising_edge = not self.last_clock and clock
        self.last_clock = clock
        
        # On rising edge, capture inputs
        if rising_edge:
            self.value = 0
            for i in range(self.bit_width):
                d_pin = self.get_pin(f"D{i}")
                if d_pin.signal.state == SignalState.HIGH:
                    self.value |= (1 << i)
        
        # Output current value
        for i in range(self.bit_width):
            q_pin = self.get_pin(f"Q{i}")
            bit_value = (self.value >> i) & 1
            q_pin.set_signal(Signal.from_bool(bool(bit_value)))
    
    def get_bounds(self):
        """Get bounding box."""
        height = max(60, 20 + self.bit_width * 10)
        return (self.position.x, self.position.y, 80, height)
