"""
Main application entry point for Logisim Clone.
"""
import flet as ft
from circuit_model import Circuit
from simulation_engine import SimulationEngine
from file_handler import FileHandler
from ui.circuit_canvas import CircuitCanvas
from ui.calculator_tab import CalculatorTab


class LogisimApp:
    """Main application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Logisim Clone - Симулятор цифровых схем"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        
        # Initialize core components
        self.circuit = Circuit("Новая схема")
        self.simulation = SimulationEngine(self.circuit)
        
        # Initialize UI components
        self.canvas = CircuitCanvas(self.circuit, self.simulation, self.page)
        self.calculator_tab = CalculatorTab(on_build_circuit=self.build_circuit_from_form)
        
        # Build UI
        self.build_ui()
    
    def build_ui(self):
        """Build the main UI layout."""
        # Simplified menu bar
        menubar = ft.Row(
            controls=[
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text="Новая схема", on_click=self.new_circuit),
                        ft.PopupMenuItem(text="Открыть", on_click=self.open_circuit),
                        ft.PopupMenuItem(text="Сохранить", on_click=self.save_circuit),
                        ft.PopupMenuItem(),  # Divider
                        ft.PopupMenuItem(text="Выход", on_click=lambda _: self.page.window_close()),
                    ],
                    content=ft.Row([ft.Icon(ft.Icons.MENU), ft.Text("Файл")]),
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text="Очистить схему", on_click=self.clear_circuit),
                    ],
                    content=ft.Row([ft.Icon(ft.Icons.EDIT), ft.Text("Правка")]),
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text="О программе", on_click=self.show_about),
                    ],
                    content=ft.Row([ft.Icon(ft.Icons.INFO), ft.Text("Справка")]),
                ),
            ],
            spacing=10,
        )
        
        # Tabs for different views
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Калькулятор",
                    icon=ft.Icons.CALCULATE,
                    content=self.calculator_tab.container,
                ),
                ft.Tab(
                    text="Просмотр схемы",
                    icon=ft.Icons.ACCOUNT_TREE,
                    content=self.canvas.container,
                ),
            ],
            expand=True,
        )
        
        # Complete layout
        self.page.add(
            ft.Column(
                controls=[
                    ft.Container(content=menubar, padding=10, bgcolor="#2d2d2d"),
                    ft.Divider(height=1),
                    tabs,
                ],
                spacing=0,
                expand=True,
            )
        )
    
    def on_circuit_updated(self):
        """Handle circuit update from prompt."""
        self.canvas.update_canvas()
        # Auto-run simulation steps
        self.simulation.step()
        self.simulation.step()
        self.simulation.step()
        self.canvas.update_canvas()
    
    def on_page_resize(self, e):
        """Handle page resize."""
        # Calculate available height for canvas
        # Window height - menu bar (approx 60) - tab header (approx 50) - zoom controls (approx 50) - padding
        available_height = self.page.height - 160
        available_width = self.page.width
        
        if available_height < 400:
            available_height = 400
            
        self.canvas.resize(available_width, available_height)
    
    def new_circuit(self, e):
        """Create a new circuit."""
        self.circuit.clear()
        self.simulation.reset()
        self.canvas.update_canvas()
        self.show_status("New circuit created")
    
    def open_circuit(self, e):
        """Open a circuit file."""
        def on_result(e: ft.FilePickerResultEvent):
            if e.files:
                file_path = e.files[0].path
                try:
                    circuit = FileHandler.load_circuit(file_path)
                    if circuit:
                        self.circuit = circuit
                        self.simulation = SimulationEngine(self.circuit)
                        # self.parser = PromptParser(self.circuit)  # Removed
                        self.canvas.circuit = self.circuit
                        self.canvas.simulation = self.simulation
                        self.canvas.update_canvas()
                        self.show_status(f"Открыто: {file_path}")
                    else:
                        self.show_status("Ошибка открытия файла")
                except Exception as ex:
                    self.show_status(f"Ошибка: {str(ex)}")
        
        # Create file picker if not exists
        if not hasattr(self, 'file_picker'):
            self.file_picker = ft.FilePicker(on_result=on_result)
            self.page.overlay.append(self.file_picker)
            self.page.update()
        
        self.file_picker.pick_files(
            allowed_extensions=["lgsim", "json"],
            dialog_title="Открыть схему"
        )
    
    def save_circuit(self, e):
        """Save the current circuit."""
        def on_result(e: ft.FilePickerResultEvent):
            if e.path:
                file_path = e.path
                if not file_path.endswith('.lgsim'):
                    file_path += '.lgsim'
                
                try:
                    if FileHandler.save_circuit(self.circuit, file_path):
                        self.show_status(f"Сохранено: {file_path}")
                    else:
                        self.show_status("Ошибка сохранения")
                except Exception as ex:
                    self.show_status(f"Ошибка: {str(ex)}")
        
        # Create save file picker if not exists
        if not hasattr(self, 'save_file_picker'):
            self.save_file_picker = ft.FilePicker(on_result=on_result)
            self.page.overlay.append(self.save_file_picker)
            self.page.update()
        
        self.save_file_picker.save_file(
            allowed_extensions=["lgsim"],
            dialog_title="Сохранить схему",
            file_name="circuit.lgsim"
        )
    
    def save_circuit_as(self, e):
        """Save circuit with a new name."""
        # In a real implementation, this would open a file picker
        self.save_circuit(e)
    
    def clear_circuit(self, e):
        """Clear the entire circuit."""
        self.canvas.clear_canvas()
        self.show_status("Схема очищена")
    
    def show_about(self, e):
        """Show about dialog."""
        dialog = ft.AlertDialog(
            title=ft.Text("О программе Logisim Clone"),
            content=ft.Text(
                "Симулятор цифровых схем\n\n"
                "Возможности:\n"
                "• Визуальный редактор схем\n"
                "• Логические вентили и компоненты\n"
                "• Симуляция в реальном времени\n"
                "• Генерация схем по промптам\n"
                "• Сохранение/загрузка схем\n\n"
                "Создано на Python и Flet"
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=lambda _: self.close_dialog(dialog))
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        """Close a dialog."""
        dialog.open = False
        self.page.update()
    
    def show_status(self, message: str):
        """Show a status message."""
        # In a real implementation, this would show in a status bar
        print(f"Status: {message}")
    
    def build_circuit_from_form(self, expression: str, form_type: str):
        """Build circuit from boolean form (PDNF or PCNF)."""
        from utils.circuit_from_form import CircuitFromBooleanForm
        from utils.boolean_algebra import BooleanExpression
        
        try:
            # Clear existing circuit first
            self.circuit.clear()
            self.simulation.reset()
            
            # Extract variables from expression
            bool_expr = BooleanExpression(expression)
            variables = bool_expr.variables
            
            # Create circuit builder
            builder = CircuitFromBooleanForm(self.circuit)
            
            # Build circuit
            if form_type.lower() == 'pdnf':
                success = builder.build_from_pdnf(expression, variables)
            else:  # pcnf
                success = builder.build_from_pcnf(expression, variables)
            
            if success:
                self.on_circuit_updated()
                self.show_status(f"Схема построена из {form_type.upper()} по алгоритму скобок")
            else:
                self.show_status(f"Ошибка построения из {form_type.upper()}")
        except Exception as e:
            self.show_status(f"Ошибка: {str(e)}")


def main(page: ft.Page):
    """Main entry point."""
    app = LogisimApp(page)
    
    # Register resize handler
    page.on_resized = app.on_page_resize
    
    # Trigger initial resize
    app.on_page_resize(None)


if __name__ == "__main__":
    ft.app(target=main)
