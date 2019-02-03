
import argparse

from workers.basic_worker import BasicUserParseWorker


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='ShillBot -- Identify shills and trolls on Reddit')
    parser.add_argument('username', type=str, help='The Reddit username of the suspected shill/troll.')

    args = parser.parse_args()
    if args.username:
        worker = BasicUserParseWorker('https://old.reddit.com/user/%s' % args.username)
        worker.run()
    else:
        parser.print_usage()
