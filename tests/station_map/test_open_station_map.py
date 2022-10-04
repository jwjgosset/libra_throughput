from libra_metrics.apollo_interface.station_map import open_station_map


def test_open_station_map():
    hubs = open_station_map(
        station_map='./tests/data/station_map.json'
    )
    assert len(hubs.hubs) == 2
    assert hubs.hubs[0].carina_id == 'carina110_2635'
