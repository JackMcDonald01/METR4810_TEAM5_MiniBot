import asyncio
from bleak import BleakScanner

async def run():
    scanner = BleakScanner()
    devices = await scanner.discover()
    for device in devices:
        print(device)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
