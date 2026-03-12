from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api.routers.delivery_api import router as deliveries_router
from api.routers.robot_api import router as robot_router

app = FastAPI()

# GET /health to confirm API is reachable by robot
@app.get("/health")
def health():
    return {"status": "running"}

app.include_router(robot_router, prefix = "/robot")

# Handles LookupErrors: single-record queries that return no data
@app.exception_handler(LookupError)
async def lookup_error_handler(request: Request, exc: LookupError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

# Handles ValueErrors: Ex. entering an integer id that is >=0
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})