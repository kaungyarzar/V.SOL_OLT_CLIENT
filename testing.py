from vsol_olt_client.connection import TNET, SSH
from vsol_olt_client.mgmt import (
    get_hostname, get_running_config,enable_pri_mode,enable_alt_mode,
    enable_conf_mode
)

host = 'localhost'
username = 'admin'
password = 'admin'

conn = TNET(host, username, password)
# conn = SSH(host, username, password)
conn.login()
print("hostname: ", get_hostname(conn))
enable_alt_mode(conn)
print("current prompt: ", conn.get_shell_prompt())
enable_conf_mode(conn)
print("current prompt: ", conn.get_shell_prompt())
enable_pri_mode(conn)
print("current prompt: ", conn.get_shell_prompt())
print("running config >>>")
print(get_running_config(conn))
conn.logout()