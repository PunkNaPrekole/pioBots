from dataclasses import dataclass, field
from cargo import Cargo


@dataclass
class Pioneer:
    id: int
    is_cargo: bool
    is_shooting: bool
    cargo: Cargo() = field(default_factory=Cargo)
    position: list[int] = field(default_factory=list)
