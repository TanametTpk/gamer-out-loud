import json
import asyncio
from speech import duplexRegister

isRegister = False

class EchoServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        duplexRegister(self.on_received_data, self.localRegister)

    def localRegister(self, callback):
        global isRegister
        isRegister = True
        self.send_data_to_speech = callback
        
    def on_received_data(self, event, data):
        payload = json.dumps({"event":event, "msg": data})

        if not self.transport.is_closing():
            self.transport.write(payload.encode())

    def data_received(self, data):
        message = data.decode()
        payload = json.loads(message)
        if isRegister:
            self.send_data_to_speech(payload)


    def connection_lost(self, exc):
        print("Connection closed")
        self.transport.close()
