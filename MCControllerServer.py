from mcstatus import MinecraftServer  # imports
import asyncio
import websockets
import json
import os
import time
import psutil


def GetSysInfo():  # Get the system info and return the data
    return psutil.cpu_percent(.1), psutil.virtual_memory()[2], psutil.disk_io_counters()[5]


def GetPlayers(ServerNumber):  # Get the names of all the players in the server and return them as a list
    if ServerNumber == 1:  # Check the server number
        if Server1Status == True:  # check if the server is on or not
            print("GETTING PLAYER NAMES FOR SERVER 1")
            server = MinecraftServer("rossnation.ddns.me",25565)  # Set the server instance
            response = server.query()  # query the server
            return response.players.names
        else: return []  # return the list of players

    elif ServerNumber == 2:
        if Server2Status == True:
            print("GETTING PLAYER NAMES FOR SERVER 2")
            server = MinecraftServer("rossnation.ddns.me",25566)
            response = server.query()
            return response.players.names
        else: return []


def GetMotd(ServerNumber):  # Get the message of the day for the servers
    print("GETTING MOTD FOR SERVER 1")
    if ServerNumber == 1:  # check the server number
        if Server1Status == True:  # check if the server is on or not
            server = MinecraftServer("rossnation.ddns.me",25565)  # set the server instance
            response = server.query()  # query the server
            return response.motd  # return the MOTD of the server
        else: return 'Server Offline'  # If the server is offline set the MOTD to Server Offline

    elif ServerNumber == 2:
        if Server2Status == True:
            print("GETTING MOTD FOR SERVER 2")
            server = MinecraftServer("rossnation.ddns.me",25566)
            response = server.query()
            return response.motd
        else: return 'Server Offline'


def CheckOnline(ServerNumber):  # Check if a server is active with players
    if ServerNumber == 1:  # Check the server number
        if Server1Status == True:  # check if the server is on or not
            server = MinecraftServer("rossnation.ddns.me",25565)  # Set the server instance
            status = server.status()  # Get the server status
            PlayersActive = None  # Set the server activity variable

            if status.players.online == 0:  PlayersActive = False  # Set the server to inactive if the number of players is 0
            else: PlayersActive = True  # If player count is not 0 the server is active
            return PlayersActive  # Return the state of the server
        else: return False

    elif ServerNumber == 2:
        if Server2Status == True:
            server = MinecraftServer("rossnation.ddns.me",25566)
            status = server.status()
            PlayersActive = None

            if status.players.online == 0:  PlayersActive = False
            else: PlayersActive = True
            return PlayersActive
        else: return False

def CheckStatus(ServerNumber):
    if ServerNumber == 1:
        server = MinecraftServer("rossnation.ddns.me",25565)
        try:
            response = server.ping()
            if type(response) == float: ServerActive = True
        except ConnectionRefusedError: ServerActive = False
        return ServerActive

    elif ServerNumber == 2:
        server = MinecraftServer("rossnation.ddns.me",25566)
        try:
            response = server.ping()
            if type(response) == float: ServerActive = True
        except ConnectionRefusedError: ServerActive = False
        return ServerActive


def CheckPlayers(ServerNumber):  # Check how many players are online in a server
    if ServerNumber == 1:  # Check the server number
        if Server1Status == True:  # Check if the server is active on or off
            print("CHECKING PLAYER NUMBER ON SERVER 1")
            server = MinecraftServer("rossnation.ddns.me",25565)  # Set the server instance
            status = server.status()  # Get the server status
            return status.players.online  # Return the number of players in the server
        else: return 0  # else return 0 (inactive)

    elif ServerNumber == 2:
        if Server2Status == True:
            print("CHECKING PLAYER NUMBER ON SERVER 2")
            server = MinecraftServer("rossnation.ddns.me",25566)
            status = server.status()
            return status.players.online
        else: return 0


def Control(ServerNumber, state):  # Function to shutdown the servers using schtasks to control task scheduler
    if ServerNumber == 1:
        if state == True:
            # os.system('start cmd /k "schtasks /run /TN BootMinecraftServer && exit"')
            return True
            print("S1 ON")
        else:
            # os.system('start cmd /k "schtasks /end /TN BootMinecraftServer && exit"')
            print("S1 OFF")
            return False

    elif ServerNumber == 2:
        if state == True:
            # os.system('start cmd /k "schtasks /run /TN BootMinecraftServer2 && exit"')
            print("S2 ON")
            return True
        else:
            # os.system('start cmd /k "schtasks /end /TN BootMinecraftServer2 && exit"')
            print("S2 OFF")
            return False


def GetCurrentTime():  # Get the current system time in hours and return the value
    return round(time.time()/60,0)


# async def read(ws, path):                                               #define async function
#     message = await ws.recv()                                           #Await a message from the web socket
#     print(message)
#     while True:                                                         #main loop to send the server status to the JS Web app
#         sysInfo = GetSysInfo()                                          #get and store the current system information
#         serverInfo = [{'online': CheckOnline(1), 'players':CheckPlayers(1), 'names':GetPlayers(1), 'motd':GetMotd(1)},          #Server 1 info
#                             {'online':CheckOnline(2), 'players':CheckPlayers(2), 'names':GetPlayers(2), 'motd':GetMotd(2)},     #Server 2 info
#                             {'cpu':sysInfo[0], 'ram':sysInfo[1], 'disc':sysInfo[2]}]                                            #System info
#         await ws.send(json.dumps(serverInfo))                           #Send the server information as a JSON dump across the web socket
#         await asyncio.sleep(1)                                          #sleep for 1 second letting async do other tasks


async def Read(ws, path):
    global Server1Status
    global Server2Status
    print("SET SERVER GLOBALS")
    Server1Status = CheckStatus(1)
    Server2Status = CheckStatus(2)
    print("SET SERVER STATUSES INITIAL")

    while True:
        message = await ws.recv()
        print("GOT MESSAGE")
        command = json.loads(message)
        print("UNLOADED MESSAGE")
        print("COMMAND" + str(command[1]))

        if type(command) == list:
            print("CHECKED IF COMMAND WAS LIST")
            if command[0] == 1: Server1Status = Control(command[0], command[1])
            elif command[0] == 2: Server2Status = Control(command[0], command[1])
            print("CHECKED IF COMMAND WAS SERVER 2")


async def Write(ws, path):
    while True:  # main loop to send the server status to the JS Web app
        sysInfo = GetSysInfo()  # get and store the current system information
        print("GOT SYSTEM INFO")
        # Server1Status = CheckStatus(1)
        # Server2Status = CheckStatus(2)
        print("GOT SERVER INFORMATION INTO VARS")
        serverInfo = [{'online': Server1Status, 'players':CheckPlayers(1), 'names':GetPlayers(1), 'motd':GetMotd(1)},  # Server 1 info
                      {'online':Server2Status, 'players':CheckPlayers(2), 'names':GetPlayers(2), 'motd':GetMotd(2)},  # Server 2 info
                      {'cpu':sysInfo[0], 'ram':sysInfo[1], 'disc':sysInfo[2]}, 'Smokey222']  # System info

        await ws.send(json.dumps(serverInfo))
        print("SENT DATA TO WEB SERVER")
        print(Server1Status, Server2Status)

        await asyncio.sleep(1)
        print("SLEPT 1 SECOND")

async def SocketHandler(ws, path):
    while True:
        consumer = asyncio.ensure_future(Read(ws, path))
        print("SET CONSUMER")
        producer = asyncio.ensure_future(Write(ws, path))
        print("SENT PRODUCER")
        done, pending = await asyncio.wait([consumer, producer])
        print("SET DONE PENDING?")


async def ServerTimeout():  # Define Async function for shutting down idle server                                         #Set the Server2Status variable to determine if the server is on or off as a global variable

    HourCheck = GetCurrentTime()  # Set the hour checkpoint as the current time
    print("SET HOUR CHECKPOINT")

    MainLoop = True  # Debug var to disable the main loop if needed
    CheckInterval = 30  # How often (in minutes) the program checks if any of the servers are inactive

    while MainLoop == True:  # Main loop for server timeout

        print("CHECKING IF TIME TO STOP")
        if HourCheck + CheckInterval == GetCurrentTime():  # Checks if the current time is the time that the program should be checking for server inactivity
            HourCheck = GetCurrentTime()  # Reset the hour checkpoint to the current time
            print("CHECKING SERVER STATUS",'/n')
            if Server1Status:  # Only check the server status if the server is on
                if CheckOnline(1) == False:  # If the server is empty shut it down
                    Shutdown(1)
                    print("SERVER 1 SHUTDOWN DUE TO INACTIVITY",'/n')

            if Server2Status:
                if CheckOnline(2) == False:
                    Shutdown(2)
                    print("SERVER 2 SHUTDOWN DUE TO INACTIVITY",'/n')
        await asyncio.sleep(2)  # Async sleep 2 seconds to give other operations to happen
        print("SLEPT 2 SECONDS ASYNC")

async def main():
    server = websockets.serve(SocketHandler, "0.0.0.0", 8765)
    await asyncio.gather(ServerTimeout(), server)


asyncio.run(main())
