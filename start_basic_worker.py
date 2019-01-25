
from workers.basic_worker import BasicUserParseWorker


if __name__ == "__main__":
    # worker = BasicUserParseWorker("https://www.reddit.com/user/Chrikelnel")
    worker = BasicUserParseWorker("https://old.reddit.com/user/I_Like_Triscuits")
    worker.run()
