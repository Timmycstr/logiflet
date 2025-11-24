"""
Calculator tab for boolean function analysis.
"""
import flet as ft
from typing import Optional, Callable
from utils.boolean_algebra import analyze_boolean_function, generate_truth_table


class CalculatorTab:
    """Calculator tab for truth tables and boolean forms."""
    
    def __init__(self, on_build_circuit: Optional[Callable] = None):
        self.on_build_circuit = on_build_circuit
        self.current_result = None
        
        # Input field
        self.expression_input = ft.TextField(
            label="Boolean Function",
            hint_text="Example: A&B | ~C, (A|B)&C, A^B",
            on_submit=self.calculate,
        )
        
        # Operator buttons
        operator_buttons = ft.Row(
            controls=[
                ft.ElevatedButton("∧ (AND)", on_click=lambda e: self.insert_operator("&"), tooltip="Конъюнкция"),
                ft.ElevatedButton("∨ (OR)", on_click=lambda e: self.insert_operator("|"), tooltip="Дизъюнкция"),
                ft.ElevatedButton("¬ (NOT)", on_click=lambda e: self.insert_operator("!"), tooltip="Отрицание"),
                ft.ElevatedButton("⊕ (XOR)", on_click=lambda e: self.insert_operator("^"), tooltip="Исключающее ИЛИ"),
                ft.ElevatedButton("→ (IMPL)", on_click=lambda e: self.insert_operator("->"), tooltip="Импликация"),
                ft.ElevatedButton("≡ (EQ)", on_click=lambda e: self.insert_operator("="), tooltip="Эквивалентность"),
            ],
            wrap=True,
            spacing=5,
        )
        
        # Calculate button
        calculate_btn = ft.ElevatedButton(
            "Вычислить",
            icon=ft.Icons.CALCULATE,
            on_click=self.calculate,
        )
        
        # Clear button
        clear_btn = ft.OutlinedButton(
            "Очистить",
            icon=ft.Icons.CLEAR,
            on_click=self.clear,
        )
        
        # Truth table
        self.truth_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(""))],  # Placeholder column
            rows=[],
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
        )
        
        self.truth_table_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Таблица истинности", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=self.truth_table,
                        bgcolor=ft.Colors.BLACK,
                        padding=10,
                        border_radius=5,
                    ),
                ],
                spacing=10,
            ),
            visible=False,
        )
        
        # Results
        self.pdnf_text = ft.TextField(
            label="СДНФ (Совершенная ДНФ)",
            multiline=True,
            read_only=True,
            min_lines=2,
            max_lines=4,
        )
        
        self.pcnf_text = ft.TextField(
            label="СКНФ (Совершенная КНФ)",
            multiline=True,
            read_only=True,
            min_lines=2,
            max_lines=4,
        )
        
        self.zhegalkin_text = ft.TextField(
            label="Полином Жегалкина (АНФ)",
            read_only=True,
        )
        
        self.results_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Результаты", size=16, weight=ft.FontWeight.BOLD),
                    self.pdnf_text,
                    self.pcnf_text,
                    self.zhegalkin_text,
                    ft.Text(
                        "💡 Схема автоматически построена из СДНФ",
                        size=11,
                        color=ft.Colors.BLUE_400,
                        italic=True,
                    ),
                ],
                spacing=10,
            ),
            visible=False,
        )
        
        # Status text
        self.status_text = ft.Text(
            "Введите булеву функцию и нажмите 'Вычислить'",
            size=12,
            color=ft.Colors.GREY_400,
        )
        
        # Main container
        self.container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text("🧮 Калькулятор булевых функций", size=20, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    "Поддерживаемые операторы: & (AND), | (OR), ! (NOT), ^ (XOR), -> (IMPL), = (EQ)",
                                    size=11,
                                    color=ft.Colors.GREY_400,
                                ),
                            ],
                            spacing=5,
                        ),
                        padding=10,
                        bgcolor=ft.Colors.BLACK,
                        border_radius=5,
                    ),
                    ft.Row(
                        controls=[self.expression_input, calculate_btn, clear_btn],
                        spacing=10,
                    ),
                    operator_buttons,
                    self.status_text,
                    self.truth_table_container,
                    self.results_container,
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
        )
    
    def on_input_change(self, e):
        """Handle input change."""
        # Explicitly update value to ensure it's synced
        self.expression_input.value = e.control.value

    def insert_operator(self, operator: str):
        """Insert operator at cursor position."""
        current = self.expression_input.value or ""
        self.expression_input.value = current + operator
        self.expression_input.update()
        # self.expression_input.focus()  # Removed to prevent language reset issues
    
    def calculate(self, e):
        """Calculate truth table and forms."""
        expression = self.expression_input.value
        
        if not expression:
            self.status_text.value = "⚠ Введите булеву функцию"
            self.status_text.color = ft.Colors.ORANGE
            self.status_text.update()
            return
        
        try:
            # Analyze function
            result = analyze_boolean_function(expression)
            self.current_result = result
            
            # Update truth table
            self._update_truth_table(result)
            
            # Update results
            self.pdnf_text.value = result['pdnf']
            self.pcnf_text.value = result['pcnf']
            self.zhegalkin_text.value = result['zhegalkin']
            
            # Show results
            self.truth_table_container.visible = True
            self.results_container.visible = True
            
            self.status_text.value = f"✓ Успешно вычислено для {len(result['variables'])} переменных. Схема построена!"
            self.status_text.color = ft.Colors.GREEN
            
            # Update UI
            self.truth_table_container.update()
            self.results_container.update()
            self.pdnf_text.update()
            self.pcnf_text.update()
            self.zhegalkin_text.update()
            self.status_text.update()
            
            # Automatically build circuit from PDNF
            if self.on_build_circuit:
                # Clear previous circuit first
                from circuit_model import Circuit
                # Note: We need to clear the circuit in main app
                # For now, just build - user can clear manually if needed
                self.build_from_pdnf(None)
            
        except Exception as ex:
            self.status_text.value = f"✗ Ошибка: {str(ex)}"
            self.status_text.color = ft.Colors.RED
            self.status_text.update()
    
    def _update_truth_table(self, result):
        """Update truth table display."""
        variables = result['variables']
        truth_table = result['truth_table']
        
        # Create columns
        columns = [ft.DataColumn(ft.Text(var, weight=ft.FontWeight.BOLD)) for var in variables]
        columns.append(ft.DataColumn(ft.Text("F", weight=ft.FontWeight.BOLD)))
        
        # Create rows
        rows = []
        for row_data in truth_table:
            cells = []
            for var in variables:
                value = row_data[var]
                cells.append(ft.DataCell(ft.Text(str(int(value)))))
            
            # Output cell with color
            output = row_data['F']
            output_cell = ft.DataCell(
                ft.Container(
                    content=ft.Text(
                        str(int(output)),
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN if output else ft.Colors.GREY,
                    ),
                    bgcolor=ft.Colors.GREEN_100 if output else None,
                    padding=5,
                    border_radius=3,
                )
            )
            cells.append(output_cell)
            
            rows.append(ft.DataRow(cells=cells))
        
        self.truth_table.columns = columns
        self.truth_table.rows = rows
        self.truth_table.update()
    
    def clear(self, e):
        """Clear all fields."""
        self.expression_input.value = ""
        self.truth_table_container.visible = False
        self.results_container.visible = False
        self.status_text.value = "Введите булеву функцию и нажмите 'Вычислить'"
        self.status_text.color = ft.Colors.GREY_400
        
        self.expression_input.update()
        self.truth_table_container.update()
        self.results_container.update()
        self.status_text.update()
    
    def build_from_pdnf(self, e):
        """Build circuit from PDNF."""
        if self.current_result and self.on_build_circuit:
            self.on_build_circuit(self.current_result['pdnf'], 'pdnf')
    
    def build_from_pcnf(self, e):
        """Build circuit from PCNF."""
        if self.current_result and self.on_build_circuit:
            self.on_build_circuit(self.current_result['pcnf'], 'pcnf')
