from logging import Logger


class DummyService:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.logger.info("DummyService initialized")

    def do_something(self):
        self.logger.info("DummyService is doing something")

