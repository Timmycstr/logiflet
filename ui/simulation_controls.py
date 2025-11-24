"""
Simulation controls for running and stepping through simulations.
"""
import flet as ft
from simulation_engine import SimulationEngine


class SimulationControls:
    """Simulation control panel."""
    
    def __init__(self, simulation_engine: SimulationEngine, on_step_callback=None):
        self.simulation = simulation_engine
        self.on_step_callback = on_step_callback
        self.running = False
        
        # Create UI elements
        self.start_button = ft.ElevatedButton(
            text="Start",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.start_simulation,
        )
        
        self.stop_button = ft.ElevatedButton(
            text="Stop",
            icon=ft.Icons.STOP,
            on_click=self.stop_simulation,
            disabled=True,
        )
        
        self.step_button = ft.ElevatedButton(
            text="Step",
            icon=ft.Icons.SKIP_NEXT,
            on_click=self.step_simulation,
        )
        
        self.reset_button = ft.ElevatedButton(
            text="Reset",
            icon=ft.Icons.REFRESH,
            on_click=self.reset_simulation,
        )
        
        self.tick_text = ft.Text(
            value="Ticks: 0",
            size=14,
        )
        
        self.container = ft.Container(
            content=ft.Row(
                controls=[
                    self.start_button,
                    self.stop_button,
                    self.step_button,
                    self.reset_button,
                    ft.VerticalDivider(),
                    self.tick_text,
                ],
                spacing=10,
            ),
            padding=10,
            bgcolor="#2d2d2d",
        )
    
    def start_simulation(self, e):
        """Start continuous simulation."""
        self.simulation.start()
        self.running = True
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.start_button.update()
        self.stop_button.update()
    
    def stop_simulation(self, e):
        """Stop simulation."""
        self.simulation.stop()
        self.running = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.start_button.update()
        self.stop_button.update()
    
    def step_simulation(self, e):
        """Execute one simulation step."""
        self.simulation.step()
        self.tick_text.value = f"Ticks: {self.simulation.tick_count}"
        self.tick_text.update()
        
        if self.on_step_callback:
            self.on_step_callback()
    
    def reset_simulation(self, e):
        """Reset simulation."""
        self.simulation.reset()
        self.tick_text.value = "Ticks: 0"
        self.running = False
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.tick_text.update()
        self.start_button.update()
        self.stop_button.update()
        
        if self.on_step_callback:
            self.on_step_callback()
