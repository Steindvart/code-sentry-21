import uvicorn

from app.config.app import app

import logging as log


if __name__ == "__main__":
  log.debug('app run')
  uvicorn.run(app, host="127.0.0.1", port=8000)
