from fastapi import FastAPI
from piccolo.engine import engine_finder

# from kafka_subscribers import router
from core.endpoints import auth_router, geolocation_router

app = FastAPI(
    title="OliveGarden Auth Service",
    # lifespan=router.lifespan_context
)
# app.include_router(router)
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(geolocation_router, prefix="/api/v1/user")


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
