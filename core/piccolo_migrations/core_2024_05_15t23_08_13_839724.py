from piccolo.apps.migrations.auto.migration_manager import MigrationManager


ID = "2024-05-15T23:08:13:839724"
VERSION = "1.5.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="", description=DESCRIPTION
    )

    def run():
        print(f"running {ID}")

    manager.add_raw(run)

    return manager
