from fastapi import FastAPI
from starlette.routing import Route
from piccolo.engine import engine_finder

from kafka_subscribers import router
from core.endpoints import AuthEndpoint

app = FastAPI(
    title="OliveGarden Auth Service",
    lifespan=router.lifespan_context
)
app.include_router(router)
app.include_router(AuthEndpoint(), prefix="/api/v1/auth")

@app.on_event("startup")
async def open_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


@app.on_event("shutdown")
async def close_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
    except Exception:
        print("Unable to connect to the database")
