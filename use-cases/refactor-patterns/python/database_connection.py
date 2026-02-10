# Database connection manager with complex initialization
class BaseConnector:
    def __init__(self, config):
        self.config = config

    def connect(self):
        raise NotImplementedError("Connector must implement connect().")


class MySQLConnector(BaseConnector):
    def connect(self):
        connection_string = (
            f"mysql://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
        )
        connection_string += f"?charset={self.config.charset}"
        connection_string += f"&connectionTimeout={self.config.connection_timeout}"

        if self.config.use_ssl:
            connection_string += "&useSSL=true"

        print(f"MySQL Connection: {connection_string}")
        return None


class PostgreSQLConnector(BaseConnector):
    def connect(self):
        connection_string = (
            f"postgresql://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
        )

        if self.config.use_ssl:
            connection_string += "?sslmode=require"

        print(f"PostgreSQL Connection: {connection_string}")
        return None


class MongoDBConnector(BaseConnector):
    def connect(self):
        connection_string = (
            f"mongodb://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
        )
        connection_string += f"?retryAttempts={self.config.retry_attempts}"
        connection_string += f"&poolSize={self.config.pool_size}"

        if self.config.use_ssl:
            connection_string += "&ssl=true"

        print(f"MongoDB Connection: {connection_string}")
        return None


class RedisConnector(BaseConnector):
    def connect(self):
        print(
            f"Redis Connection: {self.config.host}:"
            f"{self.config.port}/{self.config.database}"
        )
        return None


class DatabaseConnectorFactory:
    _CONNECTORS = {
        "mysql": MySQLConnector,
        "postgresql": PostgreSQLConnector,
        "mongodb": MongoDBConnector,
        "redis": RedisConnector,
    }

    @classmethod
    def create(cls, db_type, config):
        connector_class = cls._CONNECTORS.get(db_type)
        if connector_class is None:
            raise ValueError(f"Unsupported database type: {db_type}")
        return connector_class(config)


class DatabaseConnection:
    def __init__(self, db_type, host, port, username, password, database,
                 use_ssl=False, connection_timeout=30, retry_attempts=3,
                 pool_size=5, charset='utf8'):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.use_ssl = use_ssl
        self.connection_timeout = connection_timeout
        self.retry_attempts = retry_attempts
        self.pool_size = pool_size
        self.charset = charset
        self.connection = None

    def connect(self):
        print(f"Connecting to {self.db_type} database...")

        connector = DatabaseConnectorFactory.create(self.db_type, self)
        self.connection = connector.connect()

        print("Connection successful!")
        return self.connection

# Example usage
# Creating different database connections with various configurations
mysql_db = DatabaseConnection(
    db_type='mysql',
    host='localhost',
    port=3306,
    username='db_user',
    password='password123',
    database='app_db',
    use_ssl=True
)
mysql_db.connect()

mongo_db = DatabaseConnection(
    db_type='mongodb',
    host='mongodb.example.com',
    port=27017,
    username='mongo_user',
    password='mongo123',
    database='analytics',
    pool_size=10,
    retry_attempts=5
)
mongo_db.connect()