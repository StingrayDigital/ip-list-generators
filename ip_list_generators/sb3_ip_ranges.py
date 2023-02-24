"""Get IP ranges for Stingray's servers and the AWS services it uses."""
import ipaddress
import os
import socket
from ipaddress import IPv4Network
from pathlib import Path
from typing import TypedDict, cast

import requests

STINGRAY_HOSTS = ["cs.stingray360.com", "cs-affiliates.stingray360.com"]
AWS_IP_URL = "https://ip-ranges.amazonaws.com/ip-ranges.json"
TARGET_SERVICE_AND_REGIONS = {
    "CLOUDFRONT": {"GLOBAL"},
    "S3": {"us-east-1", "us-east-2"},
}
STINGRAY_TIME_FILENAME = "stingray-time.txt"
STINGRAY_AND_AWS_FILENAME = "stingray.txt"


class AWSPrefix(TypedDict):
    """Data for an AWS IP range."""

    ip_prefix: str
    service: str
    network_border_group: str
    region: str


def get_aws_ip_data(aws_ip_url: str) -> list[AWSPrefix]:
    """Get AWS IP range data."""
    return requests.get(aws_ip_url, timeout=30).json()["prefixes"]


def get_stingray_server_ips(stingray_hosts: list[str]) -> list[IPv4Network]:
    """Get Stingray server IPs as networks."""
    stingray_ips = [socket.gethostbyname(host) for host in stingray_hosts]

    return [cast(IPv4Network, ipaddress.ip_network(ip)) for ip in stingray_ips]


def filter_aws_ip_data(
    aws_data: list[AWSPrefix], target_services: dict
) -> list[IPv4Network]:
    """Filter AWS IP range data."""
    ip_prefixes: set[str] = set()
    for ip_data in aws_data:
        for service, regions in target_services.items():
            if ip_data["service"] == service and ip_data["region"] in regions:
                ip_prefixes.add(ip_data["ip_prefix"])
                break

    return [cast(IPv4Network, ipaddress.ip_network(ip)) for ip in ip_prefixes]


def collapse_networks(networks: list[IPv4Network]) -> list[IPv4Network]:
    """Take a list of lists of IP ranges and collapse them to remove overlap/redundancy."""
    return list(ipaddress.collapse_addresses(networks))


def get_output_folder() -> Path:
    """Get the output folder's path."""
    output_path = Path(os.getcwd())
    if output_folder := os.getenv("IP_RANGES_OUTPUT_PATH"):
        output_path = Path(output_folder)

    if not output_path.exists():
        raise ValueError(f"Output path {output_path} does not exist.")
    return output_path


def write_files(
    output_path: Path,
    stingray_ip_ranges: list[IPv4Network],
    aws_and_stingray_ip_ranges: list[IPv4Network],
) -> None:
    """Write the IP ranges to files."""
    with open(output_path / STINGRAY_TIME_FILENAME, "w", encoding="UTF-8") as file:
        file.write("\n".join([str(x) for x in stingray_ip_ranges]))

    with open(output_path / STINGRAY_AND_AWS_FILENAME, "w", encoding="UTF-8") as file:
        file.write("\n".join([str(x) for x in aws_and_stingray_ip_ranges]))


def main(
    aws_ip_url: str,
    stingray_hosts: list[str],
    target_service_and_regions: dict[str, set[str]],
) -> None:
    """Create lists of IP ranges required by the Stingray music player."""
    output_path = get_output_folder()

    stingray_ip_ranges = get_stingray_server_ips(stingray_hosts)

    aws_data = get_aws_ip_data(aws_ip_url)
    aws_ip_ranges = filter_aws_ip_data(aws_data, target_service_and_regions)

    aws_and_stingray_ip_ranges = collapse_networks(stingray_ip_ranges + aws_ip_ranges)

    write_files(output_path, stingray_ip_ranges, aws_and_stingray_ip_ranges)


if __name__ == "__main__":
    main(AWS_IP_URL, STINGRAY_HOSTS, TARGET_SERVICE_AND_REGIONS)
