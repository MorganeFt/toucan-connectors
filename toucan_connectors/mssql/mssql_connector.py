import pandas as pd
import pymssql
from pydantic import Schema, SecretStr, constr

from toucan_connectors.toucan_connector import ToucanConnector, ToucanDataSource


class MSSQLDataSource(ToucanDataSource):
    # By default SQL Server selects the database which is set
    # as default for specific user
    database: str = Schema(
        None,
        description='The name of the database you want to query. '
        "By default SQL Server selects the user's default database",
    )
    query: constr(min_length=1) = Schema(
        ..., description='You can write your SQL query here', widget='sql'
    )


class MSSQLConnector(ToucanConnector):
    """
    Import data from Microsoft SQL Server.
    """

    data_source_model: MSSQLDataSource

    host: str = Schema(
        ...,
        description='The domain name (preferred option as more dynamic) or '
        'the hardcoded IP address of your database server',
    )

    port: int = Schema(None, description='The listening port of your database server')
    user: str = Schema(..., description='Your login username')
    password: SecretStr = Schema(None, description='Your login password')
    connect_timeout: int = Schema(
        None,
        title='Connection timeout',
        description='You can set a connection timeout in seconds here, i.e. the maximum length '
        'of time you want to wait for the server to respond. None by default',
    )

    def get_connection_params(self, database):
        con_params = {
            'server': self.host,
            'user': self.user,
            'database': database,
            'password': self.password.get_secret_value() if self.password else None,
            'port': self.port,
            'login_timeout': self.connect_timeout,
            'as_dict': True,
        }
        # remove None values
        return {k: v for k, v in con_params.items() if v is not None}

    def _retrieve_data(self, datasource):
        connection = pymssql.connect(**self.get_connection_params(datasource.database))
        df = pd.read_sql(datasource.query, con=connection)

        connection.close()
        return df
