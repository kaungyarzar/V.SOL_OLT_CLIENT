import asyncio
import os
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from dotenv import load_dotenv

from vsol_olt_client.client import PROTO, VOLTClient
from vsol_olt_client.command import get_versions, get_hostname

load_dotenv()

host = os.getenv("host")
username = os.getenv("username")
password = os.getenv("password")
proto = PROTO.ssh if os.getenv("proto") == 'ssh' else PROTO.telnet

def blkTask(n, client):
    print(f"Task {n} is starting. ThreadID {id(client.mutex)}")
    res = get_versions(client)
    # res = get_hostname(client)
    print(f"Task {n} is completed. ThreadID {id(client.mutex)}")
    return res


async def main():
    print(f"Proto : {proto}")
    loop = asyncio.get_running_loop()
    client = VOLTClient(host, username, password, proto=proto)
    client.connect()
    with ThreadPoolExecutor(max_workers=2) as executor:
        tasks = [
            loop.run_in_executor(executor, blkTask, i, client) for i in range(5)
        ]
        results = await asyncio.gather(*tasks)
        print("Results: ", results)
    client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
