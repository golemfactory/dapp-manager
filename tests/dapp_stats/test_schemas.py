from dapp_stats.statistics import schemas


def test_state_ok():
    payload = """
        {
            "nodes": {
                "db": {
                    "0": "running"
                },
                "http": {
                    "0": "starting"
                }
            },
            "timestamp": "2022-12-19T10:22:53Z",
            "app": "starting"
        }
        """
    schemas.State.parse_raw(payload)
