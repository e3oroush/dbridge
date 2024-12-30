import uvicorn

from dbridge.server import app
from dbridge.config import settings

if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
