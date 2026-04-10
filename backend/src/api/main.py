from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from api.routers.robot_api import router as robot_router
from api.routers.admin_api import router as admin_router
from services.delivery_admin_service import check_late_deliveries
from contextlib import asynccontextmanager

import threading

# shared stop signal for the worker thread
stop_event = threading.Event() # shared signal flag (True/False)
late_thread = None

# function to check every 30s for late deliveries while FastAPI is running (used in a thread)
def late_delivery_worker():
    while not stop_event.is_set():
        try:
            check_late_deliveries()
        except Exception as e:
            print(f"Late delivery check failed: {e}")
        
        # wait up to 30s, but wake up immediately if stop_event is set
        stop_event.wait(30) 

# function to initiate thread for checking late delivery
def start_late_delivery_checker():
    global late_thread # this variable can be accessed anywhere in this module (global - required for assigning)
    stop_event.clear()
    late_thread = threading.Thread(target=late_delivery_worker, daemon=False)
    late_thread.start()

# to manage FastAPI app at startup (before yeild) and shutdown (after yeild)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    start_late_delivery_checker() 

    yield
    # --- Shutdown Logic ---
    stop_event.set()
    if late_thread and late_thread.is_alive():
        late_thread.join(timeout=5)

app = FastAPI(lifespan = lifespan)


# GET /health to confirm API is reachable by robot
@app.get("/health")
def health():
    return {"status": "running"}

app.include_router(robot_router, prefix = "/robot")
app.include_router(admin_router, prefix = "/admin")

# Handles LookupErrors: single-record queries that return no data
@app.exception_handler(LookupError)
async def lookup_error_handler(request: Request, exc: LookupError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

# Handles ValueErrors: Ex. entering an integer id that is >=0
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})