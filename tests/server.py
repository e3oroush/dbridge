from dbridge.server.config import add_connection, ConnectionConfig, get_connections


def test_add_connection():
    uri = ":memory:"
    connection = ConnectionConfig(uri=uri, adapter="duckdb")
    add_connection(connection)
    gotConnection = get_connections()
    assert connection in gotConnection
