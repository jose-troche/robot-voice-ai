from typing import Iterable, List, Sequence, Tuple


Point = Tuple[float, float]
Polygon = Sequence[Point]


def centroid(polygon: Polygon) -> Point:
    if not polygon:
        return (0.0, 0.0)
    x_sum = sum(point[0] for point in polygon)
    y_sum = sum(point[1] for point in polygon)
    count = float(len(polygon))
    return (x_sum / count, y_sum / count)


def point_in_polygon(point: Point, polygon: Polygon) -> bool:
    if len(polygon) < 3:
        return False
    x, y = point
    inside = False
    x1, y1 = polygon[0]
    for i in range(1, len(polygon) + 1):
        x2, y2 = polygon[i % len(polygon)]
        intersects = ((y1 > y) != (y2 > y)) and (
            x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-9) + x1
        )
        if intersects:
            inside = not inside
        x1, y1 = x2, y2
    return inside


def normalize_polygon(raw_points: Iterable[Sequence[float]]) -> List[Point]:
    return [(float(x), float(y)) for x, y in raw_points]
