from piccolo.engine.postgres import PostgresEngine

from piccolo.conf.apps import AppRegistry


DB = PostgresEngine(
    config={
        "database": "olive_garden_auth",
        "user": "postgres",
        "password": "1234",
        "host": "localhost",
        "port": 5432,
    }
)

APP_REGISTRY = AppRegistry(
    apps=["auth.piccolo_app"]
)
