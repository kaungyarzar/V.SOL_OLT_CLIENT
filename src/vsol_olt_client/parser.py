import re


def parse_show_version_output(raw: str):
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
        match = re.search(pattern, raw)
        if match:
            parsed_results[key] = match.group(1)

    return parsed_results
