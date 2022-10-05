from decimal import DivisionByZero
import logging
from typing import Dict, List
from dataclasses import dataclass
import requests
from libra_metrics.apollo_interface.station_map import LibraHub


@dataclass
class StationStats:
    station_name: str
    total_bytes: int
    good_burst: float
    receive_strength: int


@dataclass
class HubStats:
    hub_id: str
    temperature: float


@dataclass
class StationStatistics:
    stations: List[StationStats]


def assemble_api_url(
    apollo_address: str,
    carina_id: str
) -> str:
    '''
    Assemble the URL to be used to query the API for statistics about a HUB

    Parameters
    ----------
    apollo_address: str
        The address of the apollo server, including port number

    carina_id:
        The carina_id associated with the hub

    Returns
    -------
    str: The assembled URL to query the API with
    '''
    base_url = f'http://{apollo_address}/api/v1/instruments/soh'
    api_options = f'?instrumentId={carina_id}&pretty=true'
    return (base_url + api_options)


def request_api(
    apollo_address: str,
    carina_id: str,
) -> Dict[str, str]:
    '''
    Sends a request to the apollo server api to get SOH statistics about a HUB
    and the modems connected to it

    Parameters
    ----------
    apollo_address: str
        The address, including port number, for the apollo server's web
        interface

    carina_id: str
        The carina_id associated with the HUB

    Return
    ------
    Dictionary: The raw dump of the json returned by the API

    Raises
    ------
    HTTPError: Raised if the API call to the apollo server fails
    '''
    request_url = assemble_api_url(
        apollo_address=apollo_address,
        carina_id=carina_id
    )
    resp = requests.get(request_url)
    resp.raise_for_status()
    data = resp.json()

    return data


def get_staion_statistics(
    api_data: Dict,
    hub: LibraHub
) -> StationStatistics:
    '''
    Extract valuable station statistics from the API call results

    Parameters
    ----------
    api_data: Dict

    '''
    stations = StationStatistics(stations=[])
    for slot_id in hub.tdmaslots:
        slot_num = slot_id.split('_')[1]

        # Log a warning but don't crash if values are missing
        try:
            api_key = f"modem/tdma/slot/rxStats/totalBytes#_{slot_num}"
            logging.debug(api_key)
            total_bytes = int(api_data[hub.carina_id][api_key]['value'])
        except KeyError:
            logging.warning(f'No "total bytes" value for {slot_id} of '
                            + f'{hub.hub_id}, skipping.')
            # Set totalbyes to -1 so this can be handled down the pipe
            total_bytes = -1

        try:
            api_key = f"modem/tdma/slot/txStats/badBursts#_{slot_num}"
            logging.debug(api_key)
            bad_bursts = int(api_data[hub.carina_id][api_key]['value'])
            api_key = f"modem/tdma/slot/rxStats/goodBursts#_{slot_num}"
            logging.debug(api_key)
            good_bursts = int(
                api_data[hub.carina_id][api_key]['value'])
            total_bursts = good_bursts + bad_bursts
            logging.debug(f"Bursts Good={good_bursts} Bad={bad_bursts}")
            burst_percentage = good_bursts / total_bursts
        except KeyError:
            logging.warning(
                f'Burst statistics missing for {slot_id}, skipping.')
            # Set value to -1 so it can be handled downstream
            burst_percentage = -1
        except DivisionByZero:
            logging.warning(f'0 total Bursts for {slot_id} of {hub.hub_id}')

        try:
            api_key = f"modem/tdma/slot/rxStats/receivePower#_{slot_num}"
            logging.debug(api_key)
            receive_power = int(
                api_data[hub.carina_id][api_key]['value'])
        except KeyError:
            logging.warning(
                f'Receive power statistic missing for {slot_id}')
            receive_power = -1

        # Create a StationStats object for the station and add it to the
        # StationStatistics object
        station = StationStats(
            station_name=hub.tdmaslots[slot_id].station,
            total_bytes=total_bytes,
            good_burst=burst_percentage,
            receive_strength=receive_power
        )
        stations.stations.append(station)

    return stations
