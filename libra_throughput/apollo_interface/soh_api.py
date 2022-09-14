from typing import Dict
from dataclasses import dataclass
import requests
from libra_throughput.apollo_interface.station_map import LibraHubs


@dataclass
class StationStats:
    station_name: str


def assemble_api_url(
    apollo_address: str,
    carina_id: str
) -> str:
    base_url = f'http://{apollo_address}/api/v1/instruments/soh'
    api_options = f'?instrumentId={carina_id}&pretty=true'
    return (base_url + api_options)


def request_api(
    request_url: str
) -> Dict[str, str]:
    resp = requests.get(request_url)
    resp.raise_for_status()
    data = resp.json()

    return data


def parse_api(
    api_data: Dict,
    hub_map: LibraHubs
):
    for hub in LibraHubs:
        pass
