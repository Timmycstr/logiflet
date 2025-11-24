"""
File handler for saving and loading circuits.
"""
import json
from typing import Optional
from circuit_model import Circuit, Wire, Signal, SignalState, PinType
from components.registry import ComponentRegistry
from utils.geometry import Point
from utils.constants import FILE_VERSION


class FileHandler:
    """Handle saving and loading circuit files."""
    
    @staticmethod
    def save_circuit(circuit: Circuit, filename: str) -> bool:
        """Save circuit to JSON file."""
        try:
            data = {
                'version': FILE_VERSION,
                'name': circuit.name,
                'components': [],
                'wires': []
            }
            
            # Serialize components
            for comp_id, component in circuit.components.items():
                comp_data = {
                    'id': comp_id,
                    'type': component.__class__.__name__,
                    'label': component.label,
                    'position': {
                        'x': component.position.x,
                        'y': component.position.y
                    },
                    'properties': component.properties
                }
                data['components'].append(comp_data)
            
            # Serialize wires
            for wire_id, wire in circuit.wires.items():
                # Find component IDs for pins
                start_comp_id = None
                end_comp_id = None
                
                for comp_id, comp in circuit.components.items():
                    if wire.start_pin in comp.pins.values():
                        start_comp_id = comp_id
                    if wire.end_pin in comp.pins.values():
                        end_comp_id = comp_id
                
                if start_comp_id and end_comp_id:
                    wire_data = {
                        'id': wire_id,
                        'start_component': start_comp_id,
                        'start_pin': wire.start_pin.name,
                        'end_component': end_comp_id,
                        'end_pin': wire.end_pin.name
                    }
                    data['wires'].append(wire_data)
            
            # Write to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving circuit: {e}")
            return False
    
    @staticmethod
    def load_circuit(filename: str) -> Optional[Circuit]:
        """Load circuit from JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Create circuit
            circuit = Circuit(data.get('name', 'Untitled'))
            
            # Create components
            component_map = {}
            for comp_data in data.get('components', []):
                comp_type = comp_data['type']
                comp_id = comp_data['id']
                label = comp_data['label']
                pos = comp_data['position']
                position = Point(pos['x'], pos['y'])
                
                # Map class names to registry names
                type_mapping = {
                    'ANDGate': 'and',
                    'ORGate': 'or',
                    'NOTGate': 'not',
                    'XORGate': 'xor',
                    'NANDGate': 'nand',
                    'NORGate': 'nor',
                    'XNORGate': 'xnor',
                    'BufferGate': 'buffer',
                    'Switch': 'switch',
                    'Button': 'button',
                    'LED': 'led',
                    'InputPin': 'inputpin',
                    'OutputPin': 'outputpin',
                    'Clock': 'clock',
                    'DFlipFlop': 'dflipflop',
                    'JKFlipFlop': 'jkflipflop',
                    'SRLatch': 'srlatch',
                    'Register': 'register',
                    'Multiplexer': 'multiplexer',
                    'Decoder': 'decoder',
                    'HalfAdder': 'halfadder',
                    'FullAdder': 'fulladder',
                    'Comparator': 'comparator'
                }
                
                registry_name = type_mapping.get(comp_type, comp_type.lower())
                
                try:
                    component = ComponentRegistry.create(
                        registry_name,
                        component_id=comp_id,
                        label=label,
                        position=position
                    )
                    component.properties = comp_data.get('properties', {})
                    circuit.add_component(component)
                    component_map[comp_id] = component
                except Exception as e:
                    print(f"Error creating component {comp_type}: {e}")
            
            # Create wires
            for wire_data in data.get('wires', []):
                start_comp_id = wire_data['start_component']
                start_pin_name = wire_data['start_pin']
                end_comp_id = wire_data['end_component']
                end_pin_name = wire_data['end_pin']
                
                if start_comp_id in component_map and end_comp_id in component_map:
                    start_comp = component_map[start_comp_id]
                    end_comp = component_map[end_comp_id]
                    
                    start_pin = start_comp.get_pin(start_pin_name)
                    end_pin = end_comp.get_pin(end_pin_name)
                    
                    if start_pin and end_pin:
                        wire = Wire(wire_data['id'], start_pin, end_pin)
                        circuit.add_wire(wire)
            
            return circuit
        
        except Exception as e:
            print(f"Error loading circuit: {e}")
            return None
