import sounddevice as sd
import numpy as np
from speech import listen
import threading
from process import volProcess, loadConfig
from server import EchoServerClientProtocol
import asyncio
import sys

def print_sound(indata, outdata, frames, time, status):
    volume_norm = np.linalg.norm(indata)*10
    volProcess(volume_norm)

class VolumeThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.shouldEnd = False
        
    def stopStream(self):
        self.shouldEnd = True

    def run(self):
        with sd.Stream(callback=print_sound):
            while not self.shouldEnd:
                sd.sleep(1000)
            sd.CallbackStop()

class ControllerThread (threading.Thread):
    def __init__(self, vol, server, loop):
        threading.Thread.__init__(self)
        self.vol = vol
        self.server = server
        self.loop = loop

    def run(self):
        listen()
        self.vol.stopStream()
        self.server.close()

try:
    loadConfig("./config.json")

    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    coro = loop.create_server(EchoServerClientProtocol, '127.0.0.1', 8888)
    server = loop.run_until_complete(coro)

    volumeThread = VolumeThread()
    controller = ControllerThread(volumeThread, server, loop)

    controller.start()
    volumeThread.start()
    print('Serving on {}'.format(server.sockets[0].getsockname()))

    loop.run_until_complete(server.wait_closed())
except Exception as e:
    print("exception")
    sys.exit()
except KeyboardInterrupt:
    print("interupt")
    server.close()
    sys.exit()