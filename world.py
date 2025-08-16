import json
import math
import os
import random
from typing import Dict, Tuple

# Simple block IDs (subset of Bedrock numeric IDs)
BLOCK_AIR = 0
BLOCK_STONE = 1
BLOCK_GRASS = 2
BLOCK_DIRT = 3


class World:
	"""Very small flat world with chunked storage and JSON persistence.

	Chunk size: 16x16x128 (height truncated for MVP).
	"""

	def __init__(self, path: str) -> None:
		self.path = path
		self.seed = random.randint(0, 2**31 - 1)
		self.chunks: Dict[Tuple[int, int], bytes] = {}

	def load_or_generate(self) -> None:
		if os.path.exists(self.path):
			try:
				with open(self.path, 'r', encoding='utf-8') as f:
					data = json.load(f)
				self.seed = data.get('seed', self.seed)
				for k, v in data.get('chunks', {}).items():
					cx, cz = map(int, k.split(','))
					self.chunks[(cx, cz)] = bytes.fromhex(v)
				return
			except Exception:
				pass
		# Generate a few chunks around spawn
		for cx in range(-2, 3):
			for cz in range(-2, 3):
				self.chunks[(cx, cz)] = self._generate_flat_chunk()

	def save(self) -> None:
		data = {
			'seed': self.seed,
			'chunks': {f"{cx},{cz}": buf.hex() for (cx, cz), buf in self.chunks.items()},
		}
		with open(self.path, 'w', encoding='utf-8') as f:
			json.dump(data, f)

	def _generate_flat_chunk(self) -> bytes:
		# 16x16x128 simple flat: y=0..59 stone, 60..62 dirt, 63 grass, above air
		width = 16
		length = 16
		height = 128
		buf = bytearray(width * length * height)
		for y in range(height):
			block_id = BLOCK_AIR
			if y <= 59:
				block_id = BLOCK_STONE
			elif y <= 62:
				block_id = BLOCK_DIRT
			elif y == 63:
				block_id = BLOCK_GRASS
			for z in range(length):
				for x in range(width):
					index = y * width * length + z * width + x
					buf[index] = block_id
		return bytes(buf)

	def get_chunk(self, cx: int, cz: int) -> bytes:
		if (cx, cz) not in self.chunks:
			self.chunks[(cx, cz)] = self._generate_flat_chunk()
		return self.chunks[(cx, cz)]