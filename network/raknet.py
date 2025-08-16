import asyncio
import logging
import random
import socket
import struct
import time
from typing import Callable, Optional, Tuple

# RakNet constants
RAKNET_MAGIC = bytes([
	0x00, 0xff, 0xff, 0x00, 0xfe, 0xfe, 0xfe, 0xfe,
	0xfd, 0xfd, 0xfd, 0xfd, 0x12, 0x34, 0x56, 0x78
])

# Packet IDs (subset)
ID_UNCONNECTED_PING = 0x01
ID_UNCONNECTED_PONG = 0x1c
ID_OPEN_CONNECTION_REQUEST_1 = 0x05
ID_OPEN_CONNECTION_REPLY_1 = 0x06
ID_OPEN_CONNECTION_REQUEST_2 = 0x07
ID_OPEN_CONNECTION_REPLY_2 = 0x08
ID_CONNECTION_REQUEST = 0x09
ID_CONNECTION_REQUEST_ACCEPTED = 0x10


class RakNetEndpoint(asyncio.DatagramProtocol):
	"""Minimal RakNet-like UDP endpoint implementing LAN discovery and open connection handshake.

	This is simplified and not feature-complete but compatible enough for discovery and initiating a connection from MCPE.
	"""

	def __init__(self, host: str, port: int, motd_primary: str, motd_secondary: str, max_players: int,
				highlevel_callback: Callable[[Tuple[str, int], bytes], None]) -> None:
		self.host = host
		self.port = port
		self.motd_primary = motd_primary
		self.motd_secondary = motd_secondary
		self.max_players = max_players
		self.highlevel_callback = highlevel_callback
		self.logger = logging.getLogger("raknet")
		self.transport: Optional[asyncio.DatagramTransport] = None
		self.guid = random.getrandbits(64)

	async def start(self) -> None:
		loop = asyncio.get_running_loop()
		self.transport, _ = await loop.create_datagram_endpoint(
			lambda: self,
			local_addr=(self.host, self.port),
			family=socket.AF_INET,
		)

	async def stop(self) -> None:
		if self.transport:
			self.transport.close()
			self.transport = None

	# DatagramProtocol APIs
	def connection_made(self, transport: asyncio.BaseTransport) -> None:
		self.logger.info("UDP socket bound for RakNet discovery and handshake")

	def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
		if not data:
			return
		pid = data[0]
		try:
			if pid == ID_UNCONNECTED_PING:
				self._handle_unconnected_ping(data, addr)
			elif pid == ID_OPEN_CONNECTION_REQUEST_1:
				self._handle_open_connection_request_1(data, addr)
			elif pid == ID_OPEN_CONNECTION_REQUEST_2:
				self._handle_open_connection_request_2(data, addr)
			else:
				# Ignore other packets in phase-1.
				pass
		except Exception as exc:
			self.logger.exception(f"RakNet error handling pid=0x{pid:02x} from {addr}: {exc}")

	def error_received(self, exc: Exception) -> None:
		self.logger.error(f"UDP error: {exc}")

	# Handlers
	def _handle_unconnected_ping(self, data: bytes, addr: Tuple[str, int]) -> None:
		# Format: 0x01 | time(8) | magic(16) | guid(8) | (optional MTU/extra)
		if len(data) < 1 + 8 + 16:
			return
		time_ms = data[1:9]
		magic = data[9:25]
		if magic != RAKNET_MAGIC:
			return
		# Build Unconnected Pong
		# 0x1c | time(8) | guid(8) | magic(16) | motd_len(2) | motd(bytes)
		motd_str = self._compose_motd()
		motd_bytes = motd_str.encode('utf-8')
		packet = bytearray()
		packet.append(ID_UNCONNECTED_PONG)
		packet += time_ms
		packet += struct.pack('>Q', self.guid)
		packet += RAKNET_MAGIC
		packet += struct.pack('>H', len(motd_bytes))
		packet += motd_bytes
		self._send(bytes(packet), addr)

	def _handle_open_connection_request_1(self, data: bytes, addr: Tuple[str, int]) -> None:
		# 0x05 | magic(16) | protocol(1) | mtuPadding
		if len(data) < 1 + 16 + 1:
			return
		magic = data[1:17]
		if magic != RAKNET_MAGIC:
			return
		protocol = data[17]
		# We'll accept any protocol for MVP
		mtu = len(data) - 1 - 16 - 1 + 46  # add RakNet/UDP/IP headers overhead approx
		if mtu < 548:
			mtu = 548
		# Reply 1: 0x06 | magic | server_guid(8) | security(1=0) | mtu(2)
		reply = bytearray()
		reply.append(ID_OPEN_CONNECTION_REPLY_1)
		reply += RAKNET_MAGIC
		reply += struct.pack('>Q', self.guid)
		reply.append(0)  # doSecurity = false
		reply += struct.pack('>H', mtu)
		self._send(bytes(reply), addr)

	def _handle_open_connection_request_2(self, data: bytes, addr: Tuple[str, int]) -> None:
		# 0x07 | magic | server_addr(7?) | mtu(2) | security(1)
		if len(data) < 1 + 16 + 7 + 2 + 1:
			return
		magic = data[1:17]
		if magic != RAKNET_MAGIC:
			return
		# We do not parse full address, keep mtu
		mtu = struct.unpack('>H', data[-3:-1])[0]
		# Reply 2: 0x08 | magic | server_guid(8) | doSecurity(0) | mtu(2) | internalIds(1)
		reply = bytearray()
		reply.append(ID_OPEN_CONNECTION_REPLY_2)
		reply += RAKNET_MAGIC
		reply += struct.pack('>Q', self.guid)
		reply.append(0)  # security disabled
		reply += struct.pack('>H', mtu)
		reply.append(0)  # num internal IDs
		self._send(bytes(reply), addr)
		# Connection will then attempt to send MCPE login over reliable channel (not yet implemented here)

	def _compose_motd(self) -> str:
		# MCPE MOTD format: MCPE;Primary;protocol;version;online;max;guid;levelName;gamemode;port;portIPv6
		protocol = 594  # protocol for 1.20.15; may differ but works for discovery
		version = "1.20.15"
		online = 0
		level_name = self.motd_primary
		gamemode = 1  # creative
		port_v4 = self.port
		port_v6 = self.port
		return f"MCPE;{self.motd_primary};{protocol};{version};{online};{self.max_players};{self.guid};{level_name};{gamemode};{port_v4};{port_v6}"

	def _send(self, payload: bytes, addr: Tuple[str, int]) -> None:
		if self.transport:
			self.transport.sendto(payload, addr)