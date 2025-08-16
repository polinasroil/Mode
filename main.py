#!/usr/bin/env python3
import asyncio
import signal
import sys
import threading
from server import BedrockServer


def run_console(server: BedrockServer) -> None:
	"""Simple blocking console for admin commands running in a separate thread."""
	while server.is_running:
		try:
			line = sys.stdin.readline()
			if not line:
				break
			line = line.strip()
			if not line:
				continue
			cmd, *rest = line.split(" ", 1)
			arg = rest[0] if rest else ""
			if cmd == "stop":
				server.request_stop("shutdown by console")
				break
			elif cmd == "say":
				server.console_say(arg)
			elif cmd == "kick":
				server.console_kick(arg)
			elif cmd == "list":
				server.console_list()
			else:
				print(f"Unknown command: {cmd}")
		except Exception as exc:
			print(f"Console error: {exc}")


async def main() -> None:
	server = BedrockServer(
		bind_host="0.0.0.0",
		bind_port=19132,
		motd_primary="Python Bedrock MVP",
		motd_secondary="MVP",
		max_players=10,
		gamemode="creative",
	)

	# Start console thread
	console_thread = threading.Thread(target=run_console, args=(server,), daemon=True)
	console_thread.start()

	# Handle signals for graceful shutdown
	loop = asyncio.get_running_loop()
	for sig in (signal.SIGINT, signal.SIGTERM):
		try:
			loop.add_signal_handler(sig, lambda s=sig: server.request_stop(f"signal {s.name}"))
		except NotImplementedError:
			# Not available on some platforms
			pass

	await server.start()
	try:
		await server.wait_closed()
	finally:
		await server.stop()


if __name__ == "__main__":
	asyncio.run(main())