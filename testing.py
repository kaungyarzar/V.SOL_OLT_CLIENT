import os
from enum import Enum

from dotenv import load_dotenv

from vsol_olt_client.client import PROTO, VOLTClient
from vsol_olt_client.command import get_versions, get_hostname

load_dotenv()

host = os.getenv("host")
username = os.getenv("username")
password = os.getenv("password")
proto = PROTO.ssh if os.getenv("proto") == 'ssh' else PROTO.telnet

if __name__ == "__main__":
    client = VOLTClient(host, username, password, proto=proto)
    client.connect()
    for _ in range(5):
        print(get_versions(client))
        # print(get_hostname(client))
    client.disconnect()
