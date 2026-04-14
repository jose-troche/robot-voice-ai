from typing import Iterable, Sequence


def build_polygon(points: Iterable[Sequence[float]]):
    return [[float(x), float(y)] for x, y in points]
