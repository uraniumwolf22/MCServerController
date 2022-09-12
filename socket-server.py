from mcstatus import MinecraftServer
import configparser
import websockets
import asyncio
import psutil
import json
import os

# Read config file and distribute to variables
config = configparser.ConfigParser()
config.read('config.ini')

hostAddress = config['General']['hostAddress']
password = config['General']['clientPassword']
refresh = config['General'].getfloat('refresh')
autoShutoff = config['General'].getboolean('autoShutoff')
shutoffInterval = config['General'].getint('shutoffInterval')
print(hostAddress, refresh, autoShutoff, shutoffInterval)

serverList = []

for section in config:
    if section not in ['DEFAULT', 'General']:
        serverList.append((int(config[section]['port']), config[section]['directory'], section))
print(serverList)


# Return server status as bool
async def ServerPing(server):
    conn = MinecraftServer(hostAddress, server[0])
    try:
        ping = await conn.async_ping(tries=1)
        return True, ping
    except ConnectionRefusedError:
        return False, 0


# Do one async call and return most server details
async def ServerInfo(server):
    conn = MinecraftServer(hostAddress, server[0])
    info = await conn.async_query(tries=1)
    return [info.players.online,
            info.players.max,
            info.players.names,
            info.motd]


# Return system information
async def SystemInfo():
    return [psutil.cpu_percent(),
            psutil.virtual_memory()[2],
            psutil.disk_usage('/')[3]]


# Issue command to state controller
async def ServerControl(server, state):
    command = '-start' if state else '-stop'
    os.system(f'start cmd /k "ServerController.exe {command} {server[1]} {server[0] + 10} && exit"')
    await asyncio.sleep(0.5)


# Stop servers after inactivity
async def AutoShutoff():
    while autoShutoff:
        await asyncio.sleep(shutoffInterval * 60)
        for server in serverList:
            info = await ServerInfo(server)
            if info[0] == 0: await ServerControl(server, False)


# Format and send server/system details to the web client until close
async def ClientWrite(ws, path):
    while True:
        packet = []
        for server in serverList:
            active, ping = await ServerPing(server)
            if active:
                info = await ServerInfo(server)
                packet.append({'name':server[2], 'ping':round(ping), 'active':active, 'online':info[0], 'max':info[1], 'names':info[2], 'motd':info[3]})
            else:
                packet.append({'name':server[2], 'ping':round(ping), 'active':False, 'online':0, 'max':'?', 'names':['Server Offline'], 'motd':'Server Offline'})

        system = await SystemInfo()
        packet.append({'cpu':system[0], 'ram':system[1], 'disc':system[2]})
        packet.append(password)

        await ws.send(json.dumps(packet))
        await asyncio.sleep(refresh)


# Listen for web client messages
async def ClientRead(ws, path):
    while True:
        message = await ws.recv()
        command = json.loads(message)
        print(command)
        if type(command) is list:
            await ServerControl(serverList[command[0]], command[1])


# Handle read/write on client connection
async def SocketHandler(ws, path):
    read = asyncio.create_task(ClientRead(ws, path))
    write = asyncio.create_task(ClientWrite(ws, path))
    auto = asyncio.create_task(AutoShutoff())
    done, pending = await asyncio.wait([read, write, auto])

if __name__ == "__main__":
    server = websockets.serve(SocketHandler, "0.0.0.0", 8765)

    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
