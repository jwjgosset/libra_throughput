import logging
from urllib.error import HTTPError
import click
from libra_metrics.apollo_interface.soh_api import get_staion_statistics, \
    request_api
from libra_metrics.apollo_interface.station_map import open_station_map
from libra_metrics.config import LogLevels
from libra_metrics.nagios.nagios_config import load_nagios_config
from libra_metrics.nagios.libra_checks import check_station
from libra_metrics.nagios.nrdp import NagiosCheckResults, submit


@click.command()
@click.option(
   '--station-map',
   help='The station map json file containing information about which stations \
       come through which TDMA slot at which Libra HUB'
)
@click.option(
    '--apollo-address',
    help='The hostname or IP address of the apollo server to query, including \
        port number'
)
@click.option(
    '--nagios-config',
    help='The configuration file containing information for reaching the \
        Nagios server'
)
@click.option(
    '--log-level',
    help="Log more information about the program's execution",
    default='WARNING'
)
def main(
    station_map: str,
    apollo_address: str,
    nagios_config: str,
    log_level: LogLevels
):
    if log_level == 'INFO':
        level = LogLevels.INFO
    elif log_level == 'WARNING':
        level = LogLevels.WARNING
    elif log_level == 'ERROR':
        level = LogLevels.ERROR
    elif log_level == 'DEBUG':
        level = LogLevels.DEBUG
    else:
        raise ValueError('Invalid --log-level specified')
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=level.value)

    # Load station map and nagios config
    nagios = load_nagios_config(nagios_config)
    hubs = open_station_map(station_map)

    results = NagiosCheckResults()

    for hub in hubs.hubs:
        # Get SOH data from the API for each hub
        api_data = request_api(
            apollo_address=apollo_address,
            carina_id=hub.carina_id
        )

        # Extract station metrics from the API
        stations = get_staion_statistics(
            api_data=api_data,
            hub=hub
        )

        # Generate nagios check results for each station attached to the hub
        for station in stations.stations:
            check_results = check_station(
                stats=station
            )
        results.extend(check_results)

    # Push the results to nagios using NRDP
    try:
        submit(
            nrdp=results,
            nagios=nagios.address,
            token=nagios.token
        )
    except HTTPError as e:
        logging.error(f"Failed to submit check results: {e}")


if __name__ == '__main__':
    main()
