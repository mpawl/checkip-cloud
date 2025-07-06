from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from cloud_ip_checker import CloudIPChecker
import uvicorn
import logging
import os

logging_enabled = os.getenv("ENABLE_LOGGING", "false").lower() == "true"
if logging_enabled:
    logging.basicConfig(level=logging.INFO)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

checker = CloudIPChecker()
checker.download_files(force=False)
checker.load_data()

def get_real_client_ip(request: Request) -> str:
    try:
        xff = request.headers.get("X-Forwarded-For", "")
        if xff:
            return xff.split(",")[0].strip()
        elif request.client and request.client.host:
            return request.client.host
        else:
            return "unknown"
    except Exception:
        return "unknown"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    client_ip = get_real_client_ip(request)
    logging.info(f"GET request from client IP: {client_ip}")

    return templates.TemplateResponse("index.html", {"request": request, "results": None, "error": None})

@app.post("/", response_class=HTMLResponse)
async def submit(request: Request, ip: str = Form(...)):
    client_ip = get_real_client_ip(request)
    logging.info(f"POST request from client IP: {client_ip}")

    ip = ip[:39].strip()
    if not checker.is_ip_address(ip.strip()):
        return templates.TemplateResponse("index.html", {
            "request": request,
            "results": None,
            "error": f"{ip} is not a valid IP address."
        })
    results = checker.lookup_ip(ip.strip())
    if not results:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "ip": ip,
            "results": None,
            "error": f"{ip} not found."
        })
    if logging_enabled:
        logging.info(f"UI IP lookup: {ip}")
    return templates.TemplateResponse("index.html", {"request": request, "ip": ip, "results": results, "error": None})

@app.get("/api/ip/{ip}")
async def api_lookup(ip: str):
    ip = ip[:39].strip()
    if not checker.is_ip_address(ip.strip()):
        return JSONResponse(status_code=400, content={"error": f"{ip} is not a valid IP address."})
    results = checker.lookup_ip(ip.strip())
    if not results:
        return JSONResponse(status_code=404, content={"error": f"{ip} not found."})
    if logging_enabled:
        logging.info(f"API IP lookup: {ip}")
    return JSONResponse(content={"ip": ip, "matches": results})

