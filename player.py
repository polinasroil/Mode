from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Player:
	address: Tuple[str, int]
	uuid: str
	username: str
	x: float = 0.0
	y: float = 64.0
	z: float = 0.0
	pitch: float = 0.0
	yaw: float = 0.0
	world_dimension: int = 0
	entity_id: int = field(default_factory=lambda: 0)