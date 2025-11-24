"""
Component registry for creating components by name.
"""
from typing import Type, Dict
from circuit_model import Component
from utils.geometry import Point

# Import all component types
from components.gates import (
    ANDGate, ORGate, NOTGate, XORGate, NANDGate, NORGate, XNORGate, BufferGate
)
from components.io import Switch, Button, LED, InputPin, OutputPin, Clock
from components.memory import DFlipFlop, JKFlipFlop, SRLatch, Register
from components.complex import Multiplexer, Decoder, HalfAdder, FullAdder, Comparator


class ComponentRegistry:
    """Registry for all available component types."""
    
    _registry: Dict[str, Type[Component]] = {}
    
    @classmethod
    def register(cls, name: str, component_class: Type[Component]):
        """Register a component type."""
        cls._registry[name.lower()] = component_class
    
    @classmethod
    def create(cls, component_type: str, component_id: str = "", label: str = "", 
               position: Point = None, **kwargs) -> Component:
        """Create a component by type name."""
        component_type_lower = component_type.lower()
        
        if component_type_lower not in cls._registry:
            raise ValueError(f"Unknown component type: {component_type}")
        
        component_class = cls._registry[component_type_lower]
        
        if position is None:
            position = Point(0, 0)
        
        # Create component with appropriate parameters
        if label == "":
            label = component_type
        
        return component_class(component_id=component_id, label=label, position=position, **kwargs)
    
    @classmethod
    def get_all_types(cls) -> list:
        """Get list of all registered component types."""
        return sorted(cls._registry.keys())
    
    @classmethod
    def get_categories(cls) -> Dict[str, list]:
        """Get components organized by category."""
        return {
            "Gates": ["and", "or", "not", "xor", "nand", "nor", "xnor", "buffer"],
            "Input/Output": ["switch", "button", "led", "inputpin", "outputpin", "clock"],
            "Memory": ["dflipflop", "jkflipflop", "srlatch", "register"],
            "Complex": ["multiplexer", "decoder", "halfadder", "fulladder", "comparator"]
        }


# Register all component types
ComponentRegistry.register("and", ANDGate)
ComponentRegistry.register("or", ORGate)
ComponentRegistry.register("not", NOTGate)
ComponentRegistry.register("xor", XORGate)
ComponentRegistry.register("nand", NANDGate)
ComponentRegistry.register("nor", NORGate)
ComponentRegistry.register("xnor", XNORGate)
ComponentRegistry.register("buffer", BufferGate)

ComponentRegistry.register("switch", Switch)
ComponentRegistry.register("button", Button)
ComponentRegistry.register("led", LED)
ComponentRegistry.register("inputpin", InputPin)
ComponentRegistry.register("outputpin", OutputPin)
ComponentRegistry.register("clock", Clock)

ComponentRegistry.register("dflipflop", DFlipFlop)
ComponentRegistry.register("jkflipflop", JKFlipFlop)
ComponentRegistry.register("srlatch", SRLatch)
ComponentRegistry.register("register", Register)

ComponentRegistry.register("multiplexer", Multiplexer)
ComponentRegistry.register("mux", Multiplexer)
ComponentRegistry.register("decoder", Decoder)
ComponentRegistry.register("halfadder", HalfAdder)
ComponentRegistry.register("fulladder", FullAdder)
ComponentRegistry.register("comparator", Comparator)
