from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from cloud_ip_checker.cloud_ip_checker import CloudIPChecker
import uvicorn
import logging
import os

# Enable logging if the environment variable is set
logging_enabled = os.getenv("ENABLE_LOGGING", "false").lower() == "true"
if logging_enabled:
    logging.basicConfig(level=logging.INFO)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

checker = CloudIPChecker()
checker.download_files(force=False)
checker.load_data()


def get_real_client_ip(request: Request) -> str:
    """Extract the real client IP from X-Forwarded-For or fallback to request.client.host."""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    return x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    client_ip = get_real_client_ip(request)
    logging.info(f"GET request from client IP: {client_ip}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "results": None,
        "error": None,
    })


@app.post("/", response_class=HTMLResponse)
async def submit(request: Request, ip: str = Form(...)):
    client_ip = get_real_client_ip(request)
    logging.info(f"POST request from client IP: {client_ip}")

    ip = ip[:39].strip()
    if not checker.is_ip_address(ip):
        logging.warning(f"Invalid IP address submitted: {ip}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "results": None,
            "error": "Invalid IP address format.",
        })

    matches = checker.get_matches(ip)
    if not matches:
        logging.info(f"No matches found for IP: {ip}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "results": None,
            "error": "IP not found.",
        })

    logging.info(f"Matches found for IP {ip}: {matches}")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "results": matches,
        "error": None,
    })


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


