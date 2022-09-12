import asyncio
import websockets
import json
from random import randint


async def read(ws, path):
    while True:
        message = await ws.recv()
        print(json.loads(message))

async def write(ws, path):
    while True:
        cpu = randint(1, 100)
        ram = randint(1, 100)
        serverinfo = [{'online':True, 'players':2, 'names':['TakingFire','PrivacyPolicy'], 'motd':'§6The §k§4||§l§9CubeCraft§k§4||§f §6Network §a[NA 1.12.2+]'},
                      {'online':False, 'players':0, 'names':[], 'motd':'Example Description'}, {'cpu':cpu, 'ram':ram, 'disc':309}, 'Password']
        await ws.send(json.dumps(serverinfo))
        await asyncio.sleep(2)

async def handler(ws, path):
    consumer = asyncio.ensure_future(read(ws, path))
    producer = asyncio.ensure_future(write(ws, path))
    done, pending = await asyncio.wait([consumer, producer])

server = websockets.serve(handler, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()
