import os
from vsol_olt_client.client import PROTO, VOLTClient
from vsol_olt_client.commands import get_hostname, get_running_config, get_versions
from dotenv import load_dotenv

load_dotenv()
host = os.getenv("host")
username = os.getenv("username")
password = os.getenv("password")

client = VOLTClient(host, username, password, proto=PROTO.ssh)
print("Client: ", id(client.mutex))
client2 = VOLTClient(host, username, password, proto=PROTO.telnet)
print("Client2: ", id(client2.mutex))
client.connect()

print("Client: ", get_hostname(client))
print("Client: ", get_versions(client))

client2.connect()

print("Client: ", get_hostname(client2))
print("Client: ", get_versions(client2))

client.disconnect()
client2.disconnect()
