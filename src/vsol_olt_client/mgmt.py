import re
from vsol_olt_client.connection import Connection
from enum import Enum

class CLI_MODE(Enum):
    PRI = '> '
    ALT = '# '
    CONF = '(config)# '

def enable_pri_mode(conn: Connection):
    p = conn.get_shell_prompt()
    if not p.endswith(CLI_MODE.PRI.value):
        # `exit` command doesn't work.
        conn.logout()
    conn.login()

def enable_alt_mode(conn: Connection):
    p = conn.get_shell_prompt()
    if p.endswith(CLI_MODE.CONF.value):
        conn.send('exit')
        conn.expect([CLI_MODE.ALT.value])
    if p.endswith(CLI_MODE.PRI.value):
        conn.send('enable')
        conn.expect(['Password: '])
        conn.send(conn.password)

def enable_conf_mode(conn: Connection):
    p = conn.get_shell_prompt()
    if CLI_MODE.CONF.value in p:
        return

    if p.endswith(CLI_MODE.PRI.value):
        conn.send('enable')
        conn.expect(['Password: '])
        conn.send(conn.password)
        conn.expect([CLI_MODE.ALT.value])

    conn.send('configure terminal')
    conn.expect([CLI_MODE.CONF.value])

def disable_paging(conn: Connection):
    enable_pri_mode(conn)
    conn.send('terminal length 0')
    conn.expect(CLI_MODE.PRI.value)

def get_hostname(conn: Connection) -> str:
    p = conn.get_shell_prompt()
    return re.sub('> |\(config\)# |# ','', p)

def get_running_config(conn: Connection) -> str:
    disable_paging(conn)
    enable_alt_mode(conn)
    conn.send('show running-config')
    _, res = conn.expect([CLI_MODE.ALT.value])
    return res


