import logging
from libra_metrics.apollo_interface.soh_api import StationStats
from libra_metrics.nagios.models import NagiosRange
from libra_metrics.nagios.nrdp import NagiosCheckResults, NagiosCheckResult


def check_station(
    stats: StationStats,
) -> NagiosCheckResults:
    '''
    Assemble check results for a single station to be pushed to Nagios through
    NRDP

    Parameters
    ----------
    stats: StationStats
        Object containing the station's name and the statistics assembled from
        the API

    Returns
    -------
    NagiosCheckResults:
        List of NagiosCheckResult objects for each service
    '''
    results = NagiosCheckResults()

    # Use the standard hostname for the station's comms as the target for the
    # services
    hostname = f"{stats.station_name}-comms"

    # Assemble each check result for each service
    results.append(check_bytes(
        hostname=hostname,
        total_bytes=stats.total_bytes
    ))
    results.append(check_burst_percentage(
        hostname=hostname,
        burst_percentage=stats.good_burst
    ))
    results.append(check_receive_power(
        hostname=hostname,
        receive_power=stats.receive_strength
    ))
    return results


def check_bytes(
    hostname: str,
    total_bytes: int,
    threshold: str = '1:'
) -> NagiosCheckResult:
    '''
    Check if the total bytes is above a certain threshold and assemble a check
    result for Nagios

    Parameters
    ----------
    hostname: str
        The hostname for the station comms as it appears in Nagios

    total_bytes: int
        The total number of bytes received from the station

    threshold: str
        The critical threshold for this check in Nagios

    Returns
    -------
    NagiosCheckResult
    '''
    logging.debug(f"Bytes check for {hostname}")
    # Value below 0 indicates that the metric was not found in the API
    if total_bytes < 0:
        state = 3
        output = "UNKNOWN - No data returned from API"
    # Check if the value is in the critical range
    elif NagiosRange(threshold).in_range(total_bytes):
        state = 2
        output = f"CRITICAL - {total_bytes}"
    else:
        state = 0
        output = f"OK - {total_bytes}"

    output += f" | Bytes={total_bytes}c;;{threshold};;"

    service = "Bytes Received at Hub"

    logging.debug(output)

    return NagiosCheckResult(
        hostname=hostname,
        servicename=service,
        state=state,
        output=output
    )


def check_burst_percentage(
    hostname: str,
    burst_percentage: float,
    threshold: str = '1:'
) -> NagiosCheckResult:
    '''
    Check if the percentage of good bursts is above a certain threshold and
    assemble a check result for Nagios

    Parameters
    ----------
    hostname: str
        The hostname for the station comms as it appears in Nagios

    burst_percentage: float
        The percentage of good bursts coming from the station

    threshold: str
        The critical threshold for this check in Nagios

    Returns
    -------
    NagiosCheckResult
    '''
    logging.debug(f"Burst check for {hostname}")

    # Value below 0 indicates that the metric was not found in the API
    if burst_percentage < 0:
        state = 3
        output = "UNKNOWN - No data returned from API"
    # Check if the value is in the critical range
    elif NagiosRange(threshold).in_range(burst_percentage):
        state = 2
        output = f"CRITICAL - {burst_percentage}"
    else:
        state = 0
        output = f"OK - {burst_percentage}"

    output += f" | GoodBursts={burst_percentage}%;;{threshold};;"

    service = "Good Burst Percentage"

    logging.debug(output)

    return NagiosCheckResult(
        hostname=hostname,
        servicename=service,
        state=state,
        output=output
    )


def check_receive_power(
    hostname: str,
    receive_power: int,
    threshold: str = '-30:'
) -> NagiosCheckResult:
    '''
    Check if the percentage of good bursts is above a certain threshold and
    assemble a check result for Nagios

    Parameters
    ----------
    hostname: str
        The hostname for the station comms as it appears in Nagios

    receive_power: int
        The percentage of good bursts coming from the station

    threshold: str
        The critical threshold for this check in Nagios

    Returns
    -------
    NagiosCheckResult
    '''
    logging.debug(f"Receive power check for {hostname}")
    # Value below 0 indicates that the metric was not found in the API
    if receive_power < 0:
        state = 3
        output = "UNKNOWN - No data returned from API"
    # Check if the value is in the critical range
    elif NagiosRange(threshold).in_range(receive_power):
        state = 2
        output = f"CRITICAL - {receive_power}"
    else:
        state = 0
        output = f"OK - {receive_power}"

    output += f" | ReceivePower={receive_power}dBm;;{threshold};;"

    service = "Receive Power at Hub"

    logging.debug(output)

    return NagiosCheckResult(
        hostname=hostname,
        servicename=service,
        state=state,
        output=output
    )
