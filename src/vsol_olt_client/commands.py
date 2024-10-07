import re

from vsol_olt_client.client import VOLTClient


def get_hostname(client: VOLTClient) -> str:
    p = client.send_pri_cmd("")
    return re.sub("> |\(config\)# |# ", "", p)


def get_running_config(client: VOLTClient) -> str:
    res = client.send_alt_cmd("show running-config")
    return res


def get_versions(client: VOLTClient) -> dict:
    res = client.send_conf_cmd("show version")
    patterns = {
        "serial_number": r"Olt Serial Number:\s+(\S+)",
        "device_model": r"Olt Device Model:\s+(\S+)",
        "hardware_version": r"Hardware Version:\s+(\S+)",
        "software_version": r"Software Version:\s+(\S+)",
        "software_created_time": r"Software Created Time:\s+(.*)",
    }
    # Parse the information using regex
    parsed_results = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, res)
        if match:
            parsed_results[key] = match.group(1)

    return parsed_results
