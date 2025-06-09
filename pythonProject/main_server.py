from server.Server import Server
from Logger import Logger

def main():
    logger = Logger("config.json")
    logger.start()

    server = Server(port=5000, logger=logger)
    try:
        server.start()
    finally:
        logger.stop()

if __name__ == "__main__":
    main()
