import asyncio
import logging
import os
import struct
import time
from typing import Dict, Optional, Tuple

from network.raknet import RakNetEndpoint
from world import World
from player import Player


class BedrockServer:
	"""High-level server coordinating RakNet endpoint and gameplay state."""

	def __init__(self, bind_host: str, bind_port: int, motd_primary: str, motd_secondary: str, max_players: int, gamemode: str) -> None:
		self.bind_host = bind_host
		self.bind_port = bind_port
		self.motd_primary = motd_primary
		self.motd_secondary = motd_secondary
		self.max_players = max_players
		self.gamemode = gamemode
		self.logger = logging.getLogger("bedrock")
		logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")

		self.loop = asyncio.get_event_loop()
		self.transport: Optional[asyncio.DatagramTransport] = None
		self.endpoint: Optional[RakNetEndpoint] = None
		self.world = World(os.path.join(os.getcwd(), "world.json"))
		self.players: Dict[Tuple[str, int], Player] = {}
		self.is_running = True
		self._closed = asyncio.Event()

	async def start(self) -> None:
		self.logger.info(f"Starting Bedrock server on {self.bind_host}:{self.bind_port}")
		self.world.load_or_generate()
		self.endpoint = RakNetEndpoint(self.bind_host, self.bind_port, self.motd_primary, self.motd_secondary, self.max_players, self.on_datagram_highlevel)
		await self.endpoint.start()
		self.logger.info("RakNet endpoint started.")

	async def wait_closed(self) -> None:
		await self._closed.wait()

	async def stop(self) -> None:
		if self.endpoint:
			await self.endpoint.stop()
		self.world.save()
		self._closed.set()
		self.logger.info("Server stopped.")

	def request_stop(self, reason: str) -> None:
		self.logger.info(f"Stop requested: {reason}")
		self.is_running = False
		self.loop.create_task(self.stop())

	# Console integrations
	def console_say(self, text: str) -> None:
		self.logger.info(f"[CONSOLE] {text}")
		# TODO: broadcast chat packet once protocol layer implemented

	def console_kick(self, name: str) -> None:
		self.logger.info(f"Kick requested for: {name}")
		# TODO: implement

	def console_list(self) -> None:
		names = ", ".join(p.username for p in self.players.values()) or "<no players>"
		print(f"Players ({len(self.players)}/{self.max_players}): {names}")

	# Gameplay hooks from network layer
	def on_datagram_highlevel(self, addr: Tuple[str, int], payload: bytes) -> None:
		"""Handle high-level MCPE packets once RakNet reliability is added.

		For the MVP phase-1 (ping/handshake), we may not receive these yet.
		"""
		self.logger.debug(f"High-level payload from {addr}: {len(payload)} bytes (stub)")