from vsol_olt_client.client import PROTO, VOLTClient
from vsol_olt_client.commands import get_hostname, get_running_config, get_versions

host = "localhost"
username = "frontiir"
password = "frontiir"

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
# print(get_running_config(client))
client.disconnect()
client2.disconnect()
