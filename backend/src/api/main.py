from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from models.delivery import DeliveryCreateRequest, DeliveryQuickView
from api.routers.delivery_api import router as deliveries_router

app = FastAPI()

@app.get("/")
def root():
    return {"Message": "Main Program"}

app.include_router(deliveries_router, prefix = "/deliveries")

# Handles LookupErrors: single-record queries that return no data
@app.exception_handler(LookupError)
async def lookup_error_handler(request: Request, exc: LookupError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

# Handles ValueErrors: Ex. entering an integer id that is >=0
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})