"""
Geometry utilities for circuit layout and wire routing.
"""
from typing import Tuple, List
import math


class Point:
    """Represents a 2D point."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    
    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple."""
        return (self.x, self.y)
    
    @staticmethod
    def from_tuple(t: Tuple[float, float]) -> 'Point':
        """Create point from tuple."""
        return Point(t[0], t[1])


class Rect:
    """Represents a rectangle."""
    
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def contains_point(self, point: Point) -> bool:
        """Check if point is inside rectangle."""
        return (self.x <= point.x <= self.x + self.width and
                self.y <= point.y <= self.y + self.height)
    
    def intersects(self, other: 'Rect') -> bool:
        """Check if this rectangle intersects with another."""
        return not (self.x + self.width < other.x or
                   other.x + other.width < self.x or
                   self.y + self.height < other.y or
                   other.y + other.height < self.y)
    
    def center(self) -> Point:
        """Get center point of rectangle."""
        return Point(self.x + self.width / 2, self.y + self.height / 2)


def snap_to_grid(x: float, y: float, grid_size: int) -> Tuple[float, float]:
    """Snap coordinates to grid."""
    return (round(x / grid_size) * grid_size,
            round(y / grid_size) * grid_size)


def manhattan_distance(p1: Point, p2: Point) -> float:
    """Calculate Manhattan distance between two points."""
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)


def route_wire(start: Point, end: Point) -> List[Point]:
    """
    Route a wire between two points using Manhattan routing.
    Returns list of points forming the wire path.
    """
    # Simple L-shaped routing
    mid_x = (start.x + end.x) / 2
    
    if abs(start.y - end.y) < 5:
        # Horizontal line
        return [start, end]
    elif abs(start.x - end.x) < 5:
        # Vertical line
        return [start, end]
    else:
        # L-shape with midpoint
        return [
            start,
            Point(mid_x, start.y),
            Point(mid_x, end.y),
            end
        ]


def point_to_line_distance(point: Point, line_start: Point, line_end: Point) -> float:
    """
    Calculate the shortest distance from a point to a line segment.
    """
    # Vector from line_start to line_end
    dx = line_end.x - line_start.x
    dy = line_end.y - line_start.y
    
    if dx == 0 and dy == 0:
        # Line segment is actually a point
        return point.distance_to(line_start)
    
    # Parameter t of the projection of point onto the line
    t = max(0, min(1, ((point.x - line_start.x) * dx + (point.y - line_start.y) * dy) / (dx * dx + dy * dy)))
    
    # Closest point on the line segment
    closest = Point(line_start.x + t * dx, line_start.y + t * dy)
    
    return point.distance_to(closest)
