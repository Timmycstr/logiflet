"""
Core circuit model: Signal, Pin, Wire, Component, and Circuit classes.
"""
from typing import List, Dict, Optional, Set, Any
from enum import Enum
from dataclasses import dataclass, field
from utils.geometry import Point
from utils.constants import SIGNAL_LOW, SIGNAL_HIGH, SIGNAL_UNKNOWN, SIGNAL_HIGHZ


class SignalState(Enum):
    """Signal state enumeration."""
    LOW = SIGNAL_LOW
    HIGH = SIGNAL_HIGH
    UNKNOWN = SIGNAL_UNKNOWN
    HIGHZ = SIGNAL_HIGHZ


@dataclass
class Signal:
    """Represents a logic signal value."""
    state: SignalState = SignalState.UNKNOWN
    bit_width: int = 1
    value: int = 0  # For multi-bit signals
    
    def __bool__(self):
        return self.state == SignalState.HIGH
    
    def __int__(self):
        if self.state == SignalState.HIGH:
            return 1
        elif self.state == SignalState.LOW:
            return 0
        else:
            return -1
    
    @staticmethod
    def from_bool(value: bool) -> 'Signal':
        """Create signal from boolean value."""
        return Signal(SignalState.HIGH if value else SignalState.LOW, 1, 1 if value else 0)
    
    @staticmethod
    def from_int(value: int, bit_width: int = 1) -> 'Signal':
        """Create signal from integer value."""
        if value == 0:
            return Signal(SignalState.LOW, bit_width, 0)
        else:
            return Signal(SignalState.HIGH, bit_width, value)


class PinType(Enum):
    """Pin type enumeration."""
    INPUT = "input"
    OUTPUT = "output"
    INOUT = "inout"


@dataclass
class Pin:
    """Represents a component pin (connection point)."""
    name: str
    pin_type: PinType
    position: Point  # Relative to component
    signal: Signal = field(default_factory=lambda: Signal())
    bit_width: int = 1
    connected_wires: List['Wire'] = field(default_factory=list)
    
    def set_signal(self, signal: Signal):
        """Set the signal value on this pin."""
        self.signal = signal
    
    def get_signal(self) -> Signal:
        """Get the current signal value."""
        return self.signal


class Component:
    """Base class for all circuit components."""
    
    def __init__(self, component_id: str, label: str, position: Point):
        self.id = component_id
        self.label = label
        self.position = position
        self.pins: Dict[str, Pin] = {}
        self.properties: Dict[str, Any] = {}
        self.selected = False
    
    def add_pin(self, pin: Pin):
        """Add a pin to this component."""
        self.pins[pin.name] = pin
    
    def get_pin(self, name: str) -> Optional[Pin]:
        """Get a pin by name."""
        return self.pins.get(name)
    
    def get_input_pins(self) -> List[Pin]:
        """Get all input pins."""
        return [p for p in self.pins.values() if p.pin_type == PinType.INPUT]
    
    def get_output_pins(self) -> List[Pin]:
        """Get all output pins."""
        return [p for p in self.pins.values() if p.pin_type == PinType.OUTPUT]
    
    def evaluate(self):
        """
        Evaluate component logic and update output pins.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement evaluate()")
    
    def get_bounds(self) -> tuple:
        """Get bounding box (x, y, width, height)."""
        # Default implementation, can be overridden
        return (self.position.x, self.position.y, 60, 40)
    
    def to_dict(self) -> dict:
        """Serialize component to dictionary."""
        return {
            'id': self.id,
            'type': self.__class__.__name__,
            'label': self.label,
            'position': {'x': self.position.x, 'y': self.position.y},
            'properties': self.properties
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Component':
        """Deserialize component from dictionary."""
        # Will be implemented with component registry
        raise NotImplementedError()


@dataclass
class Wire:
    """Represents a wire connection between pins."""
    wire_id: str
    start_pin: Pin
    end_pin: Pin
    points: List[Point] = field(default_factory=list)
    signal: Signal = field(default_factory=lambda: Signal())
    
    def propagate(self):
        """Propagate signal from source to destination."""
        # Get signal from output pin
        if self.start_pin.pin_type == PinType.OUTPUT:
            self.signal = self.start_pin.signal
            self.end_pin.signal = self.signal
        elif self.end_pin.pin_type == PinType.OUTPUT:
            self.signal = self.end_pin.signal
            self.start_pin.signal = self.signal
    
    def to_dict(self) -> dict:
        """Serialize wire to dictionary."""
        return {
            'id': self.wire_id,
            'start_pin': self.start_pin.name,
            'end_pin': self.end_pin.name,
            'points': [{'x': p.x, 'y': p.y} for p in self.points]
        }


class Circuit:
    """Represents a complete circuit with components and wires."""
    
    def __init__(self, name: str = "Untitled"):
        self.name = name
        self.components: Dict[str, Component] = {}
        self.wires: Dict[str, Wire] = {}
        self._next_component_id = 0
        self._next_wire_id = 0
    
    def add_component(self, component: Component) -> str:
        """Add a component to the circuit."""
        if not component.id:
            component.id = f"comp_{self._next_component_id}"
            self._next_component_id += 1
        self.components[component.id] = component
        return component.id
    
    def remove_component(self, component_id: str):
        """Remove a component from the circuit."""
        if component_id in self.components:
            # Remove all connected wires
            component = self.components[component_id]
            wires_to_remove = []
            for wire_id, wire in self.wires.items():
                if wire.start_pin in component.pins.values() or wire.end_pin in component.pins.values():
                    wires_to_remove.append(wire_id)
            
            for wire_id in wires_to_remove:
                self.remove_wire(wire_id)
            
            del self.components[component_id]
    
    def add_wire(self, wire: Wire) -> str:
        """Add a wire to the circuit."""
        if not wire.wire_id:
            wire.wire_id = f"wire_{self._next_wire_id}"
            self._next_wire_id += 1
        
        self.wires[wire.wire_id] = wire
        wire.start_pin.connected_wires.append(wire)
        wire.end_pin.connected_wires.append(wire)
        return wire.wire_id
    
    def remove_wire(self, wire_id: str):
        """Remove a wire from the circuit."""
        if wire_id in self.wires:
            wire = self.wires[wire_id]
            if wire in wire.start_pin.connected_wires:
                wire.start_pin.connected_wires.remove(wire)
            if wire in wire.end_pin.connected_wires:
                wire.end_pin.connected_wires.remove(wire)
            del self.wires[wire_id]
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """Get a component by ID."""
        return self.components.get(component_id)
    
    def clear(self):
        """Clear all components and wires."""
        self.components.clear()
        self.wires.clear()
        self._next_component_id = 0
        self._next_wire_id = 0
    
    def to_dict(self) -> dict:
        """Serialize circuit to dictionary."""
        return {
            'name': self.name,
            'components': [comp.to_dict() for comp in self.components.values()],
            'wires': [wire.to_dict() for wire in self.wires.values()]
        }
