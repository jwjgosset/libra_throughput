from configparser import ConfigParser
from dataclasses import dataclass


@dataclass
class NagiosConfig:
    address: str
    api_key: str

    def __init__(
        self,
        address: str,
        token: str
    ):
        self.address = address
        self.token = token


def load_nagios_config(
    nagios_config: str
) -> NagiosConfig:
    '''
    Loads a config file and populates a NagiosConfig object with an address
    and an api key

    Parameters
    ----------
    nagios_config: str
        The path to the nagios config file

    Returns
    -------
    NagiosConfig: Object containing Nagios Server's address and api token
    '''
    parser = ConfigParser()

    parser.read(nagios_config)
    try:
        config = NagiosConfig(
            address=parser['nagios']['address'],
            token=parser['nagios']['token']
        )
    except KeyError as e:
        raise KeyError(f"Invalid nagios config file. Key missing: {e}")
    return config
