"""
Circuit canvas for drawing and interacting with circuits.
"""
import flet as ft
from typing import Optional, Tuple
from circuit_model import Circuit, Component
from components.io import Switch, Button, LED
from simulation_engine import SimulationEngine
from utils.geometry import Point, Rect, snap_to_grid
from utils.constants import *


class CircuitCanvas:
    """Interactive canvas for circuit editing."""
    
    def __init__(self, circuit: Circuit, simulation_engine: SimulationEngine, page: ft.Page):
        self.circuit = circuit
        self.simulation = simulation_engine
        self.page = page
        self.selected_component: Optional[Component] = None
        self.component_to_place: Optional[str] = None
        self.canvas_width = 800
        self.canvas_height = 600
        
        # Zoom and pan
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        
        # Create canvas container with gesture detector
        self.canvas_stack = ft.Stack(
            controls=[],
            width=self.canvas_width,
            height=self.canvas_height,
        )
        
        # Wrap in GestureDetector for interactions
        self.gesture_detector = ft.GestureDetector(
            content=self.canvas_stack,
            on_tap=self.on_tap,
            on_scroll=self.on_scroll,
            on_pan_start=self.on_pan_start,
            on_pan_update=self.on_pan_update,
            on_pan_end=self.on_pan_end,
            drag_interval=10,
        )
        
        # Zoom controls
        self.zoom_text = ft.Text(f"{int(self.zoom * 100)}%", size=12, width=50)
        
        self.zoom_slider = ft.Slider(
            min=30,
            max=300,
            value=100,
            divisions=27,
            label="{value}%",
            on_change=self.on_zoom_slider_change,
            width=200,
        )
        
        zoom_controls = ft.Row(
            controls=[
                ft.Text("Зум:", size=12),
                self.zoom_slider,
                self.zoom_text,
                ft.IconButton(
                    icon=ft.Icons.CENTER_FOCUS_STRONG,
                    tooltip="Сбросить вид (100%)",
                    on_click=self.reset_view,
                    icon_size=20,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # Main container
        self.canvas_container = ft.Container(
            content=self.gesture_detector,
            bgcolor=COLOR_BACKGROUND,
            border=ft.border.all(1, COLOR_GRID),
            width=self.canvas_width,
            height=self.canvas_height,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        self.container = ft.Column(
            controls=[
                self.canvas_container,
                ft.Container(
                    content=zoom_controls,
                    padding=5,
                    bgcolor="#2d2d2d",
                ),
            ],
            spacing=0,
            expand=True,  # Expand column to fill parent
        )
    
    def resize(self, width, height):
        """Resize the canvas."""
        self.canvas_width = width
        self.canvas_height = height
        
        self.canvas_stack.width = width
        self.canvas_stack.height = height
        
        self.canvas_container.width = width
        self.canvas_container.height = height
        
        self.container.update()
    
    def on_tap(self, e):
        """Handle tap events."""
        # Handle different event types (Flet API changes)
        if hasattr(e, 'local_x'):
            x, y = e.local_x, e.local_y
        elif hasattr(e, 'global_x'):
            x, y = e.global_x, e.global_y
        else:
            # Fallback - try to get coordinates from control
            return
        
        # If we have a component to place, place it
        if self.component_to_place:
            self.place_component(x, y)
            return
        
        # Check if we clicked on a component
        clicked_component = self.find_component_at(x, y)
        
        if clicked_component:
            # Handle interactive components
            if isinstance(clicked_component, Switch):
                clicked_component.toggle()
                self.simulation.step()
                self.simulation.step()
                self.simulation.step()
                self.update_canvas()
            elif isinstance(clicked_component, Button):
                clicked_component.press()
                self.simulation.step()
                self.simulation.step()
                self.simulation.step()
                self.update_canvas()
    
    def find_component_at(self, x: float, y: float) -> Optional[Component]:
        """Find component at given coordinates."""
        point = Point(x, y)
        
        for component in self.circuit.components.values():
            bounds = component.get_bounds()
            rect = Rect(bounds[0], bounds[1], bounds[2], bounds[3])
            if rect.contains_point(point):
                return component
        
        return None
    
    def place_component(self, x: float, y: float):
        """Place a new component."""
        if not self.component_to_place:
            return
        
        from components.registry import ComponentRegistry
        
        # Snap to grid
        if GRID_SNAP:
            x, y = snap_to_grid(x, y, GRID_SIZE)
        
        try:
            component = ComponentRegistry.create(
                self.component_to_place,
                label=self.component_to_place.upper(),
                position=Point(x, y)
            )
            self.circuit.add_component(component)
            self.component_to_place = None
            self.update_canvas()
        except Exception as e:
            print(f"Error placing component: {e}")
    
    def set_component_to_place(self, component_type: str):
        """Set the component type to place on next click."""
        self.component_to_place = component_type
    
    def update_canvas(self):
        """Redraw the canvas."""
        print(f"DEBUG: update_canvas called. Components: {len(self.circuit.components)}, Wires: {len(self.circuit.wires)}")
        self.canvas_stack.controls.clear()
        
        # 1. Draw Grid (Background)
        self._draw_grid()
        
        # 2. Draw Wires (Middle Layer)
        self._draw_wires()
        
        # 3. Draw Components (Top Layer)
        for component in self.circuit.components.values():
            self.render_component(component)
        
        self.canvas_stack.update()
        print("DEBUG: Canvas updated")

    def _draw_grid(self):
        """Draw background grid."""
        import flet.canvas as cv
        
        # Draw origin marker (cross at 0,0)
        screen_x, screen_y = self.world_to_screen(0, 0)
        
        grid_canvas = cv.Canvas(
            shapes=[
                cv.Line(screen_x - 10, screen_y, screen_x + 10, screen_y, paint=ft.Paint(color="red", stroke_width=2)),
                cv.Line(screen_x, screen_y - 10, screen_x, screen_y + 10, paint=ft.Paint(color="red", stroke_width=2)),
            ],
            expand=True,
        )
        self.canvas_stack.controls.append(grid_canvas)

    def _draw_wires(self):
        """Draw all wires."""
        wire_shapes = []
        for wire in self.circuit.wires.values():
            shape = self.create_wire_shape(wire)
            if shape:
                wire_shapes.append(shape)
        
        if wire_shapes:
            print(f"DEBUG: Drawing {len(wire_shapes)} wires")
            import flet.canvas as cv
            wire_canvas = cv.Canvas(
                shapes=wire_shapes,
                expand=True,
            )
            self.canvas_stack.controls.append(wire_canvas)

    def render_component(self, component: Component):
        """Draw a component on the canvas."""
        bounds = component.get_bounds()
        x, y, w, h = bounds
        print(f"DEBUG: Rendering component {component.label} at ({x}, {y}) size ({w}, {h})")
        
        # Apply zoom and offset
        screen_x, screen_y = self.world_to_screen(x, y)
        screen_w = w * self.zoom
        screen_h = h * self.zoom
        
        # Determine color based on component type and state
        fill_color = COLOR_COMPONENT_FILL
        stroke_color = COLOR_COMPONENT_STROKE
        
        # Special rendering for different component types
        if isinstance(component, LED):
            # Draw LED as circle
            color = COLOR_LED_ON if component.lit else COLOR_LED_OFF
            circle = ft.Container(
                left=screen_x,
                top=screen_y,
                width=screen_w,
                height=screen_h,
                bgcolor=color,
                border=ft.border.all(2, stroke_color),
                border_radius=screen_w // 2,
            )
            self.canvas_stack.controls.append(circle)
        
        elif isinstance(component, Switch):
            # Draw switch as rounded rectangle
            color = COLOR_WIRE_ON if component.state else COLOR_WIRE_OFF
            switch_rect = ft.Container(
                left=screen_x,
                top=screen_y,
                width=screen_w,
                height=screen_h,
                bgcolor=color,
                border=ft.border.all(2, stroke_color),
                border_radius=5,
            )
            self.canvas_stack.controls.append(switch_rect)
        
        elif isinstance(component, Button):
            # Draw button
            color = COLOR_WIRE_ON if component.pressed else COLOR_WIRE_OFF
            button_rect = ft.Container(
                left=screen_x,
                top=screen_y,
                width=screen_w,
                height=screen_h,
                bgcolor=color,
                border=ft.border.all(2, stroke_color),
                border_radius=3,
            )
            self.canvas_stack.controls.append(button_rect)
        
        else:
            # Draw generic component as rectangle
            comp_rect = ft.Container(
                left=screen_x,
                top=screen_y,
                width=screen_w,
                height=screen_h,
                bgcolor=fill_color,
                border=ft.border.all(2, stroke_color),
                border_radius=3,
            )
            self.canvas_stack.controls.append(comp_rect)
        
        # Draw label
        label_text = ft.Text(
            component.label,
            size=max(8, int(10 * self.zoom)),
            color=COLOR_TEXT,
            text_align=ft.TextAlign.CENTER,
        )
        label_container = ft.Container(
            content=label_text,
            left=screen_x,
            top=screen_y + screen_h + 2,
            width=screen_w,
        )
        self.canvas_stack.controls.append(label_container)
    def create_wire_shape(self, wire):
        """Create a shape for a wire."""
        from circuit_model import SignalState, PinType
        import flet.canvas as cv
        
        # Get absolute positions of pins
        start_comp = None
        end_comp = None
        
        # Find components that own these pins
        for component in self.circuit.components.values():
            if wire.start_pin in component.pins.values():
                start_comp = component
            if wire.end_pin in component.pins.values():
                end_comp = component
        
        if not start_comp or not end_comp:
            return None
        
        # Calculate pin positions
        start_bounds = start_comp.get_bounds()
        end_bounds = end_comp.get_bounds()
        
        start_x = start_bounds[0] + start_bounds[2] / 2
        start_y = start_bounds[1] + start_bounds[3] / 2
        end_x = end_bounds[0] + end_bounds[2] / 2
        end_y = end_bounds[1] + end_bounds[3] / 2
        
        # Validate coordinates
        if start_x <= 0 or start_y <= 0 or end_x <= 0 or end_y <= 0:
            return None
        
        # Apply zoom and offset
        screen_start_x, screen_start_y = self.world_to_screen(start_x, start_y)
        screen_end_x, screen_end_y = self.world_to_screen(end_x, end_y)
        
        # Determine wire color
        if wire.signal.state == SignalState.HIGH:
            color = COLOR_WIRE_ON
        elif wire.signal.state == SignalState.LOW:
            color = COLOR_WIRE_OFF
        else:
            color = COLOR_WIRE_UNKNOWN
        
        # Draw L-shaped wire
        mid_x = (screen_start_x + screen_end_x) / 2
        
        line_path = cv.Path([
            cv.Path.MoveTo(screen_start_x, screen_start_y),
            cv.Path.LineTo(mid_x, screen_start_y),
            cv.Path.LineTo(mid_x, screen_end_y),
            cv.Path.LineTo(screen_end_x, screen_end_y),
        ])
        
        return cv.Path(
            elements=line_path.elements,
            paint=ft.Paint(
                stroke_width=2,
                style=ft.PaintingStyle.STROKE,
                color=color,
            ),
        )
    
    def clear_canvas(self):
        """Clear the canvas."""
        self.circuit.clear()
        self.selected_component = None
        self.update_canvas()
    
    def on_scroll(self, e: ft.ScrollEvent):
        """Handle scroll for zoom."""
        if e.scroll_delta_y < 0:
            # Scroll up - zoom in
            self.zoom = min(3.0, self.zoom * 1.1)
        else:
            # Scroll down - zoom out
            self.zoom = max(0.3, self.zoom * 0.9)
        
        # Update slider and text
        self.zoom_slider.value = self.zoom * 100
        self.zoom_text.value = f"{int(self.zoom * 100)}%"
        self.zoom_slider.update()
        self.zoom_text.update()
        self.update_canvas()
    
    def zoom_in(self, e):
        """Zoom in."""
        self.zoom = min(self.zoom * 1.2, 3.0)
        self.zoom_text.value = f"Zoom: {int(self.zoom * 100)}%"
        self.zoom_text.update()
        self.update_canvas()
    
    def zoom_out(self, e):
        """Zoom out."""
        self.zoom = max(self.zoom / 1.2, 0.3)
        self.zoom_text.value = f"Zoom: {int(self.zoom * 100)}%"
        self.zoom_text.update()
        self.update_canvas()
    
    def on_zoom_slider_change(self, e):
        """Handle zoom slider change."""
        self.zoom = e.control.value / 100.0
        self.zoom_text.value = f"{int(self.zoom * 100)}%"
        self.zoom_text.update()
        self.update_canvas()
    
    def reset_view(self, e):
        """Reset zoom and pan to default."""
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.zoom_slider.value = 100
        self.zoom_text.value = "100%"
        self.zoom_slider.update()
        self.zoom_text.update()
        self.update_canvas()
    
    def on_pan_start(self, e):
        """Start panning."""
        self.is_panning = True
        if hasattr(e, 'local_x'):
            self.pan_start_x = e.local_x
            self.pan_start_y = e.local_y
        elif hasattr(e, 'global_x'):
            self.pan_start_x = e.global_x
            self.pan_start_y = e.global_y
        else:
            self.pan_start_x = 0
            self.pan_start_y = 0
    
    def on_pan_update(self, e: ft.DragUpdateEvent):
        """Update pan position."""
        if self.is_panning:
            dx = e.delta_x
            dy = e.delta_y
            self.offset_x += dx
            self.offset_y += dy
            self.update_canvas()
    
    def on_pan_end(self, e):
        """End panning."""
        self.is_panning = False
    
    def screen_to_world(self, x: float, y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        world_x = (x - self.offset_x) / self.zoom
        world_y = (y - self.offset_y) / self.zoom
        return world_x, world_y
    
    def world_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates."""
        screen_x = x * self.zoom + self.offset_x
        screen_y = y * self.zoom + self.offset_y
        return screen_x, screen_y
