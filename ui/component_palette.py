"""
Component palette for selecting components to place.
"""
import flet as ft
from components.registry import ComponentRegistry


def create_component_palette(on_component_selected):
    """Create component selection palette."""
    categories = ComponentRegistry.get_categories()
    
    # Create tabs for each category
    tabs = []
    
    for category_name, components in categories.items():
        # Create buttons for each component
        component_buttons = []
        for comp_type in components:
            btn = ft.ElevatedButton(
                text=comp_type.upper(),
                on_click=lambda e, ct=comp_type: on_component_selected(ct),
                width=120,
            )
            component_buttons.append(btn)
        
        # Wrap in a column
        tab_content = ft.Column(
            controls=component_buttons,
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
        )
        
        tab = ft.Tab(
            text=category_name,
            content=ft.Container(
                content=tab_content,
                padding=10,
            )
        )
        tabs.append(tab)
    
    # Create tabs container
    tabs_container = ft.Tabs(
        tabs=tabs,
        animation_duration=300,
    )
    
    return ft.Container(
        content=tabs_container,
        width=200,
        bgcolor="#2d2d2d",
        padding=5,
    )
