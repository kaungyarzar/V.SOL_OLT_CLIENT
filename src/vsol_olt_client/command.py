import re

from vsol_olt_client.client import VOLTClient
from vsol_olt_client.parser import parse_show_version_output


def get_hostname(client: VOLTClient) -> str:
    p = client.send_pri_cmd("")
    return re.sub("> |\(config\)# |# ", "", p)


def get_running_config(client: VOLTClient) -> str:
    res = client.send_alt_cmd("show running-config")
    return res


def get_versions(client: VOLTClient) -> dict:
    res = client.send_conf_cmd("show version")
    return parse_show_version_output(res)
