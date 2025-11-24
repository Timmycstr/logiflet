"""
Boolean algebra utilities for truth tables, PDNF, PCNF, and Zhegalkin polynomials.
"""
import re
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from itertools import product


@dataclass
class TruthTableRow:
    """Single row in a truth table."""
    inputs: Dict[str, bool]
    output: bool
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {**self.inputs, 'F': self.output}


class TruthTable:
    """Truth table for a boolean function."""
    
    def __init__(self, variables: List[str], rows: List[TruthTableRow]):
        self.variables = variables
        self.rows = rows
    
    def get_minterms(self) -> List[TruthTableRow]:
        """Get rows where output is True (for PDNF)."""
        return [row for row in self.rows if row.output]
    
    def get_maxterms(self) -> List[TruthTableRow]:
        """Get rows where output is False (for PCNF)."""
        return [row for row in self.rows if not row.output]
    
    def to_list(self) -> List[Dict]:
        """Convert to list of dictionaries for display."""
        return [row.to_dict() for row in self.rows]


class BooleanExpression:
    """Parser and evaluator for boolean expressions."""
    
    # Operator mappings
    AND_OPS = ['&', '•', '∧', '*', 'and', 'AND']
    OR_OPS = ['|', '∨', '+', 'or', 'OR']
    NOT_OPS = ['!', '¬', '~', 'not', 'NOT']
    XOR_OPS = ['^', '⊕', 'xor', 'XOR']
    IMPL_OPS = ['->', '→', '=>', 'impl', 'IMPL']
    EQ_OPS = ['=', '≡', '~', '<->', '<=>', 'eq', 'EQ']
    NAND_OPS = ['↑', 'nand', 'NAND']
    NOR_OPS = ['↓', 'nor', 'NOR']
    
    def __init__(self, expression: str):
        self.original = expression
        self.normalized = self._normalize(expression)
        self.variables = self._extract_variables()
    
    def _normalize(self, expr: str) -> str:
        """Normalize expression to use standard operators."""
        expr = expr.strip()
        
        # Replace multi-character operators first
        for op in self.IMPL_OPS:
            if len(op) > 1:
                expr = expr.replace(op, '→')
        
        for op in self.EQ_OPS:
            if len(op) > 1:
                expr = expr.replace(op, '≡')
        
        # Replace single character operators
        for op in self.AND_OPS:
            if op != '&':
                expr = expr.replace(op, '&')
        
        for op in self.OR_OPS:
            if op != '|':
                expr = expr.replace(op, '|')
        
        for op in self.NOT_OPS:
            if op != '!':
                expr = expr.replace(op, '!')
        
        for op in self.XOR_OPS:
            if op != '^':
                expr = expr.replace(op, '^')
        
        for op in self.NAND_OPS:
            if op != '↑':
                expr = expr.replace(op, '↑')
        
        for op in self.NOR_OPS:
            if op != '↓':
                expr = expr.replace(op, '↓')
        
        return expr
    
    def _extract_variables(self) -> List[str]:
        """Extract variable names from expression."""
        # Remove operators and parentheses
        cleaned = self.normalized
        for op in ['&', '|', '!', '^', '→', '≡', '↑', '↓', '(', ')', ' ']:
            cleaned = cleaned.replace(op, ' ')
        
        # Extract unique variable names
        variables = set()
        for token in cleaned.split():
            if token and token[0].isalpha():
                variables.add(token)
        
        return sorted(list(variables))
    
    def evaluate(self, values: Dict[str, bool]) -> bool:
        """Evaluate expression with given variable values."""
        expr = self.normalized
        
        # Replace variables with their values
        for var, val in values.items():
            # Use word boundaries to avoid partial replacements
            expr = re.sub(r'\b' + re.escape(var) + r'\b', 
                         'True' if val else 'False', expr)
        
        # Replace operators with Python equivalents
        expr = expr.replace('&', ' and ')
        expr = expr.replace('|', ' or ')
        expr = expr.replace('!', ' not ')
        expr = expr.replace('^', ' != ')  # XOR as inequality
        
        # Handle implication: A→B = !A|B
        while '→' in expr:
            # Find implication
            match = re.search(r'(\w+|True|False)\s*→\s*(\w+|True|False)', expr)
            if match:
                a, b = match.groups()
                replacement = f'(not {a} or {b})'
                expr = expr[:match.start()] + replacement + expr[match.end():]
            else:
                break
        
        # Handle equivalence: A≡B = (A&B)|(!A&!B)
        while '≡' in expr:
            match = re.search(r'(\w+|True|False)\s*≡\s*(\w+|True|False)', expr)
            if match:
                a, b = match.groups()
                replacement = f'(({a} and {b}) or (not {a} and not {b}))'
                expr = expr[:match.start()] + replacement + expr[match.end():]
            else:
                break
        
        # Handle NAND: A↑B = !(A&B)
        while '↑' in expr:
            match = re.search(r'(\w+|True|False)\s*↑\s*(\w+|True|False)', expr)
            if match:
                a, b = match.groups()
                replacement = f'not ({a} and {b})'
                expr = expr[:match.start()] + replacement + expr[match.end():]
            else:
                break
        
        # Handle NOR: A↓B = !(A|B)
        while '↓' in expr:
            match = re.search(r'(\w+|True|False)\s*↓\s*(\w+|True|False)', expr)
            if match:
                a, b = match.groups()
                replacement = f'not ({a} or {b})'
                expr = expr[:match.start()] + replacement + expr[match.end():]
            else:
                break
        
        try:
            return bool(eval(expr))
        except Exception as e:
            raise ValueError(f"Error evaluating expression: {e}")


def generate_truth_table(expression: str) -> TruthTable:
    """
    Generate truth table for a boolean expression.
    
    Args:
        expression: Boolean expression (e.g., "A&B|~C")
    
    Returns:
        TruthTable object
    """
    bool_expr = BooleanExpression(expression)
    variables = bool_expr.variables
    
    if not variables:
        raise ValueError("No variables found in expression")
    
    rows = []
    
    # Generate all possible combinations
    for combination in product([False, True], repeat=len(variables)):
        values = dict(zip(variables, combination))
        output = bool_expr.evaluate(values)
        rows.append(TruthTableRow(values, output))
    
    return TruthTable(variables, rows)


def calculate_pdnf(truth_table: TruthTable) -> str:
    """
    Calculate Perfect Disjunctive Normal Form (PDNF/СДНФ).
    
    Args:
        truth_table: Truth table to convert
    
    Returns:
        PDNF as string
    """
    minterms = truth_table.get_minterms()
    
    if not minterms:
        return "0"  # Function is always false
    
    terms = []
    for row in minterms:
        # Create conjunction for this row
        literals = []
        for var in truth_table.variables:
            if row.inputs[var]:
                literals.append(var)
            else:
                literals.append(f"!{var}")
        terms.append("(" + "&".join(literals) + ")")
    
    return " | ".join(terms)


def calculate_pcnf(truth_table: TruthTable) -> str:
    """
    Calculate Perfect Conjunctive Normal Form (PCNF/СКНФ).
    
    Args:
        truth_table: Truth table to convert
    
    Returns:
        PCNF as string
    """
    maxterms = truth_table.get_maxterms()
    
    if not maxterms:
        return "1"  # Function is always true
    
    terms = []
    for row in maxterms:
        # Create disjunction for this row
        literals = []
        for var in truth_table.variables:
            if row.inputs[var]:
                literals.append(f"!{var}")
            else:
                literals.append(var)
        terms.append("(" + "|".join(literals) + ")")
    
    return " & ".join(terms)


def calculate_zhegalkin(truth_table: TruthTable) -> str:
    """
    Calculate Zhegalkin polynomial (ANF) using triangle method.
    
    Args:
        truth_table: Truth table to convert
    
    Returns:
        Zhegalkin polynomial as string
    """
    # Get output column
    outputs = [int(row.output) for row in truth_table.rows]
    n = len(truth_table.variables)
    
    # Build triangle
    triangle = [outputs]
    for i in range(n):
        new_row = []
        prev_row = triangle[-1]
        for j in range(len(prev_row) - 1):
            new_row.append((prev_row[j] + prev_row[j + 1]) % 2)
        triangle.append(new_row)
    
    # Extract coefficients (diagonal)
    coefficients = [triangle[i][0] for i in range(len(triangle))]
    
    # Build polynomial
    terms = []
    for i, coef in enumerate(coefficients):
        if coef == 1:
            if i == 0:
                terms.append("1")
            else:
                # Determine which variables to include
                var_indices = []
                for j in range(n):
                    if (i >> j) & 1:
                        var_indices.append(j)
                
                if var_indices:
                    var_term = "&".join([truth_table.variables[j] for j in var_indices])
                    terms.append(var_term)
    
    if not terms:
        return "0"
    
    return " ⊕ ".join(terms)


# Convenience function for quick testing
def analyze_boolean_function(expression: str) -> Dict:
    """
    Analyze a boolean function and return all forms.
    
    Args:
        expression: Boolean expression
    
    Returns:
        Dictionary with truth table, PDNF, PCNF, and Zhegalkin polynomial
    """
    truth_table = generate_truth_table(expression)
    
    return {
        'expression': expression,
        'variables': truth_table.variables,
        'truth_table': truth_table.to_list(),
        'pdnf': calculate_pdnf(truth_table),
        'pcnf': calculate_pcnf(truth_table),
        'zhegalkin': calculate_zhegalkin(truth_table)
    }
