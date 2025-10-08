from multiprocessing import Process
import uvicorn
from mcp.mcp_server import mcp

def run_fastapi():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

def run_mcp():
    # Usa HTTP si quieres puerto 8001
    mcp.run_http(host="0.0.0.0", port=8001)
    # O usa STDIO si es modo plugin:
    # mcp.run()

if __name__ == "__main__":
    p1 = Process(target=run_fastapi)
    p2 = Process(target=run_mcp)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
