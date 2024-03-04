import pytest

port = 8001

pytest.main(
    [
        "./tests/data_tests",
        "-m",
        "not userquery",
        "--host",
        str(port),
    ]
)
