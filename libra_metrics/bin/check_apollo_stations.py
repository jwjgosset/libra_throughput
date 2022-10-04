import logging
from urllib.error import HTTPError
import click
from libra_metrics.apollo_interface.soh_api import get_staion_statistics, \
    request_api
from libra_metrics.apollo_interface.station_map import open_station_map
from libra_metrics.nagios.config import load_nagios_config
from libra_metrics.nagios.libra_checks import check_station
from libra_metrics.nagios.nrdp import NagiosCheckResults, submit


@click.command()
@click.option(
   '-m',
   '--station-map',
   help='The station map json file containing information about which stations \
       come through which TDMA slot at which Libra HUB'
)
@click.option(
    '-a',
    '-apollo-address',
    help='The hostname or IP address of the apollo server to query, including \
        port number'
)
@click.option(
    '-n',
    '--nagios-config',
    help='The configuration file containing information for reaching the \
        Nagios server'
)
def main(
    station_map: str,
    apollo_address: str,
    nagios_config: str
):
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
            token=nagios.api_key
        )
    except HTTPError as e:
        logging.error(f"Failed to submit check results: {e}")


if __name__ == '__main__':
    main()
