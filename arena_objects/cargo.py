from dataclasses import dataclass, field


@dataclass
class Cargo:
    name: str = None
    color_led: list[int] = field(default_factory=list)
