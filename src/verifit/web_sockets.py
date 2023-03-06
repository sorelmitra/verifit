import asyncio
import json

import websockets

from .config import get_store_reader

get_env = get_store_reader()


def ws_send_and_receive(a_dict):
    log_type = "[WebSockets]"
    wait_ms = int(get_env('WEBSOCKETS_WAIT_MS'))

    def with_server(server):
        def with_ignore_list(ignore_list):
            async def receive_async():
                async with websockets.connect(server) as websocket:
                    received = False
                    while not received:
                        data = await websocket.recv()
                        if data in ignore_list:
                            print(f"Ignoring received data <{data}>")
                        else:
                            received = True
                return data

            async def receive_async_with_timeout():
                seconds = wait_ms / 1000
                data = await asyncio.wait_for(
                    receive_async(),
                    seconds
                )
                print(f"{log_type} Received <{data}>")
                return data

            def start_receiving():
                print(f"{log_type} Waiting {wait_ms} ms for packets from {server}")
                return asyncio.ensure_future(receive_async_with_timeout())

            def end_receiving(a_handle):
                data = asyncio.get_event_loop().run_until_complete(a_handle)
                print(f"{log_type} Finished waiting for packets from {server}, received {data}")
                return json.loads(data)

            async def send_async(data):
                async with websockets.connect(server) as websocket:
                    await websocket.send(data)
                    print(f"Sent data <{data}>")

            def send_sync(data):
                asyncio.get_event_loop().run_until_complete(send_async(data))

            handle = start_receiving()
            to_send = json.dumps(a_dict)
            send_sync(to_send)
            return end_receiving(handle)
        return with_ignore_list
    return with_server

