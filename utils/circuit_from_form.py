"""
Circuit builder from boolean forms (PDNF/PCNF) using bracket grouping algorithm.
Based on the flowchart algorithm for efficient circuit construction.
"""
from typing import List, Dict, Tuple, Set
from circuit_model import Circuit, Wire
from components.registry import ComponentRegistry
from utils.geometry import Point
from utils.boolean_algebra import TruthTable, calculate_pdnf, calculate_pcnf
import re


class CircuitFromBooleanForm:
    """Build circuits from PDNF or PCNF using bracket grouping."""
    
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.component_counter = 0
        self.current_x = 80
        self.current_y = 80
        self.spacing_x = 150  # Increased horizontal spacing
        self.spacing_y = 100  # Increased vertical spacing
    
    def build_from_pdnf(self, pdnf: str, variables: List[str]) -> bool:
        """
        Build circuit from PDNF (Perfect Disjunctive Normal Form).
        
        Algorithm (from flowchart):
        1. Create input switches for each variable
        2. Create NOT gates for negated variables
        3. Group terms by brackets (скобки)
        4. For each bracket: create AND gate
        5. Final AND gate combines all brackets
        
        Args:
            pdnf: PDNF expression like "(!A&B) | (A&!B)"
            variables: List of variables ['A', 'B', ...]
        
        Returns:
            True if successful
        """
        try:
            # Parse PDNF into terms
            terms = self._parse_dnf_terms(pdnf)
            
            if not terms:
                return False
            
            # Step 1: Create input switches
            input_switches = self._create_input_switches(variables)
            
            # Step 2: Create NOT gates for negated inputs
            not_gates = self._create_not_gates(variables, input_switches)
            
            # Step 3-4: Create AND gates for each term (bracket)
            and_gates = []
            for i, term in enumerate(terms):
                and_gate = self._create_term_and_gate(
                    term, variables, input_switches, not_gates, i
                )
                if and_gate:
                    and_gates.append(and_gate)
            
            # Step 5: Create final OR gate (if multiple terms)
            if len(and_gates) > 1:
                final_or = self._create_final_or_gate(and_gates)
            elif len(and_gates) == 1:
                final_or = and_gates[0]
            else:
                return False
            
            # Create output LED
            self._create_output_led(final_or)
            
            return True
            
        except Exception as e:
            print(f"Error building from PDNF: {e}")
            return False
    
    def build_from_pcnf(self, pcnf: str, variables: List[str]) -> bool:
        """
        Build circuit from PCNF (Perfect Conjunctive Normal Form).
        
        Similar to PDNF but with OR gates for terms and final AND gate.
        
        Args:
            pcnf: PCNF expression like "(A|B) & (A|!B)"
            variables: List of variables
        
        Returns:
            True if successful
        """
        try:
            # Parse PCNF into clauses
            clauses = self._parse_cnf_clauses(pcnf)
            
            if not clauses:
                return False
            
            # Create input switches
            input_switches = self._create_input_switches(variables)
            
            # Create NOT gates
            not_gates = self._create_not_gates(variables, input_switches)
            
            # Create OR gates for each clause
            or_gates = []
            for i, clause in enumerate(clauses):
                or_gate = self._create_clause_or_gate(
                    clause, variables, input_switches, not_gates, i
                )
                if or_gate:
                    or_gates.append(or_gate)
            
            # Create final AND gate
            if len(or_gates) > 1:
                final_and = self._create_final_and_gate(or_gates)
            elif len(or_gates) == 1:
                final_and = or_gates[0]
            else:
                return False
            
            # Create output LED
            self._create_output_led(final_and)
            
            return True
            
        except Exception as e:
            print(f"Error building from PCNF: {e}")
            return False
    
    def _parse_dnf_terms(self, dnf: str) -> List[List[Tuple[str, bool]]]:
        """
        Parse DNF into terms.
        
        Example: "(!A&B) | (A&!B)" -> [[('A', False), ('B', True)], [('A', True), ('B', False)]]
        """
        terms = []
        
        # Split by OR (|)
        term_strings = re.split(r'\s*\|\s*', dnf)
        
        for term_str in term_strings:
            # Remove parentheses
            term_str = term_str.strip().strip('()')
            
            # Split by AND (&)
            literals = re.split(r'\s*&\s*', term_str)
            
            term = []
            for lit in literals:
                lit = lit.strip()
                if lit.startswith('!') or lit.startswith('~') or lit.startswith('¬'):
                    # Negated variable
                    var = lit[1:].strip()
                    term.append((var, False))
                else:
                    # Positive variable
                    term.append((lit, True))
            
            if term:
                terms.append(term)
        
        return terms
    
    def _parse_cnf_clauses(self, cnf: str) -> List[List[Tuple[str, bool]]]:
        """
        Parse CNF into clauses.
        
        Example: "(A|B) & (A|!B)" -> [[('A', True), ('B', True)], [('A', True), ('B', False)]]
        """
        clauses = []
        
        # Split by AND (&)
        clause_strings = re.split(r'\s*&\s*', cnf)
        
        for clause_str in clause_strings:
            # Remove parentheses
            clause_str = clause_str.strip().strip('()')
            
            # Split by OR (|)
            literals = re.split(r'\s*\|\s*', clause_str)
            
            clause = []
            for lit in literals:
                lit = lit.strip()
                if lit.startswith('!') or lit.startswith('~') or lit.startswith('¬'):
                    # Negated variable
                    var = lit[1:].strip()
                    clause.append((var, False))
                else:
                    # Positive variable
                    clause.append((lit, True))
            
            if clause:
                clauses.append(clause)
        
        return clauses
    
    def _create_input_switches(self, variables: List[str]) -> Dict:
        """Create input switches for each variable."""
        switches = {}
        
        for i, var in enumerate(variables):
            switch = ComponentRegistry.create(
                "switch",
                label=var,
                position=Point(self.current_x, self.current_y + i * self.spacing_y)
            )
            self.circuit.add_component(switch)
            switches[var] = switch
        
        return switches
    
    def _create_not_gates(self, variables: List[str], input_switches: Dict) -> Dict:
        """Create NOT gates for each input."""
        not_gates = {}
        
        for i, var in enumerate(variables):
            not_gate = ComponentRegistry.create(
                "not",
                label=f"NOT_{var}",
                position=Point(
                    self.current_x + self.spacing_x,
                    self.current_y + i * self.spacing_y
                )
            )
            self.circuit.add_component(not_gate)
            
            # Wire from switch to NOT
            switch_pin = input_switches[var].get_pin("out")
            not_pin = not_gate.get_pin("in0")  # NOT gate uses in0, not in
            
            if switch_pin and not_pin:
                wire = Wire("", switch_pin, not_pin)
                self.circuit.add_wire(wire)
            
            not_gates[var] = not_gate
        
        return not_gates
    
    def _create_term_and_gate(self, term: List[Tuple[str, bool]], 
                             variables: List[str],
                             input_switches: Dict,
                             not_gates: Dict,
                             term_index: int):
        """Create AND gate for a DNF term (bracket)."""
        
        # Calculate Y position with proper spacing
        y_pos = self.current_y + (term_index * self.spacing_y)
        
        # Create AND gate
        and_gate = ComponentRegistry.create(
            "and",
            label=f"AND{term_index + 1}",
            position=Point(
                self.current_x + 2 * self.spacing_x,
                y_pos
            )
        )
        self.circuit.add_component(and_gate)
        
        # Wire inputs to AND gate
        for i, (var, is_positive) in enumerate(term):
            if i >= 2:  # AND gates typically have 2 inputs
                break
            
            source_component = input_switches[var] if is_positive else not_gates[var]
            source_pin = source_component.get_pin("out")
            dest_pin = and_gate.get_pin(f"in{i}")
            
            if source_pin and dest_pin:
                wire = Wire("", source_pin, dest_pin)
                self.circuit.add_wire(wire)
        
        return and_gate
    
    def _create_clause_or_gate(self, clause: List[Tuple[str, bool]],
                               variables: List[str],
                               input_switches: Dict,
                               not_gates: Dict,
                               clause_index: int):
        """Create OR gate for a CNF clause."""
        
        # Create OR gate
        or_gate = ComponentRegistry.create(
            "or",
            label=f"OR{clause_index + 1}",
            position=Point(
                self.current_x + 2 * self.spacing_x,
                self.current_y + clause_index * self.spacing_y
            )
        )
        self.circuit.add_component(or_gate)
        
        # Wire inputs to OR gate
        for i, (var, is_positive) in enumerate(clause):
            if i >= 2:  # OR gates typically have 2 inputs
                break
            
            source_component = input_switches[var] if is_positive else not_gates[var]
            source_pin = source_component.get_pin("out")
            dest_pin = or_gate.get_pin(f"in{i}")
            
            wire = Wire("", source_pin, dest_pin)
            self.circuit.add_wire(wire)
        
        return or_gate
    
    def _create_final_or_gate(self, and_gates: List) -> object:
        """Create final OR gate combining all AND gates."""
        
        # Calculate center Y position based on number of AND gates
        if len(and_gates) > 0:
            first_gate_y = and_gates[0].position.y
            last_gate_y = and_gates[-1].position.y if len(and_gates) > 1 else first_gate_y
            center_y = (first_gate_y + last_gate_y) / 2
        else:
            center_y = self.current_y
        
        final_or = ComponentRegistry.create(
            "or",
            label="OR_FINAL",
            position=Point(
                self.current_x + 3 * self.spacing_x,
                center_y
            )
        )
        self.circuit.add_component(final_or)
        
        # Wire AND gates to final OR
        for i, and_gate in enumerate(and_gates[:2]):  # Limit to 2 inputs
            wire = Wire(
                "",
                and_gate.get_pin("out"),
                final_or.get_pin(f"in{i}")
            )
            self.circuit.add_wire(wire)
        
        return final_or
    
    def _create_final_and_gate(self, or_gates: List) -> object:
        """Create final AND gate combining all OR gates."""
        
        final_and = ComponentRegistry.create(
            "and",
            label="AND_FINAL",
            position=Point(
                self.current_x + 3 * self.spacing_x,
                self.current_y + len(or_gates) * self.spacing_y // 2
            )
        )
        self.circuit.add_component(final_and)
        
        # Wire OR gates to final AND
        for i, or_gate in enumerate(or_gates[:2]):  # Limit to 2 inputs
            wire = Wire(
                "",
                or_gate.get_pin("out"),
                final_and.get_pin(f"in{i}")
            )
            self.circuit.add_wire(wire)
        
        return final_and
    
    def _create_output_led(self, final_gate) -> None:
        """Create output LED."""
        
        led = ComponentRegistry.create(
            "led",
            label="Output",
            position=Point(
                self.current_x + 4 * self.spacing_x,
                final_gate.position.y
            )
        )
        self.circuit.add_component(led)
        
        # Wire final gate to LED
        wire = Wire(
            "",
            final_gate.get_pin("out"),
            led.get_pin("in")
        )
        self.circuit.add_wire(wire)


def build_circuit_from_truth_table(circuit: Circuit, truth_table: TruthTable, 
                                   use_pdnf: bool = True) -> bool:
    """
    Build circuit from truth table using PDNF or PCNF.
    
    Args:
        circuit: Circuit to build into
        truth_table: Truth table
        use_pdnf: If True, use PDNF; otherwise use PCNF
    
    Returns:
        True if successful
    """
    builder = CircuitFromBooleanForm(circuit)
    
    if use_pdnf:
        pdnf = calculate_pdnf(truth_table)
        return builder.build_from_pdnf(pdnf, truth_table.variables)
    else:
        pcnf = calculate_pcnf(truth_table)
        return builder.build_from_pcnf(pcnf, truth_table.variables)
