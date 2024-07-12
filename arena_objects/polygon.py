from dataclasses import dataclass, field
from cargo import Cargo


@dataclass
class Polygon:
    id: int
    role: str
    position: list[float] = field(default_factory=list)
    is_cargo: bool = False
    num_cargo: int = 0
    cargo: Cargo() = field(default_factory=Cargo)
