from pathlib import Path
import json
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class TDMASlot:
    cygnus_id: str
    station: str

    def __init__(self, data: Dict):
        '''
        Initializes the TDMASlot object with a cygnus_id and station
        Assumes the data Dict contains keys for these two variables
        '''
        self.cygnus_id = data['cygnus_id']
        self.station = data['station']


@dataclass
class LibraHub:
    tdmaslots: Dict[str, TDMASlot]
    carina_id: str
    hub_id: str

    def __init__(self, data: Dict, hub_id: str):
        '''
        Initializes the LibraHub object
        Assumes the data Dict passed contains a carina_id key and a tdma_slot
        key which would point the dictionary required for a TDMASlot
        initializer
        '''
        self.carina_id = data['carina_id']
        for slot in data['tdma_slots']:
            self.tdmaslots[slot] = TDMASlot(data['tdma_slots'][slot])
            self.hub_id = hub_id


class LibraHubs(List):
    pass


def open_station_map(
    station_map: str
) -> LibraHubs:
    '''
    Read the station_map file for information about which station is attached
    to which TDMA slot in which hub

    Parameters
    ----------
    station_map: str
        The path to the file containing the station_map.json file

    Returns
    -------
    Dict: Dictionary containings hub names as keys and LibraHub objects as
    values
    '''

    map_path = Path(station_map)
    with open(map_path) as f:
        map_data: Dict = json.load(f)

    hubs = parse_map_data(map_data)

    return hubs


def parse_map_data(
    map_data: Dict
) -> LibraHubs:
    '''
    Parses the raw data from the  station_map.json file, breaking it down into
    a dictionary of LibraHub objects

    Parameters
    ----------
    map_data: Dict
        The data read from the station_map.json file

    Returns
    -------
    Dict: Dictionary containings hub names as keys and LibraHub objects as
    values
    '''
    hubs = LibraHubs()
    for hub in map_data:
        hubs.append(LibraHub(
            data=map_data[hub],
            hub_id=hub
        ))
    return hubs
