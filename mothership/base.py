
import socket
import threading
import json
import settings

from queue import Queue

from mothership.analytics import DataAnalyzer


class MothershipServer(object):

    host = ''
    port = None
    sock = None
    buff_size = None

    analyzer = None
    data_queue = None

    def __init__(self):
        self.host = settings.MOTHERSHIP.get('host', 'localhost')
        self.port = settings.MOTHERSHIP.get('port', 8080)
        self.buff_size = settings.BUFFER_SIZE

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.data_queue = Queue()
        self.analyzer = DataAnalyzer()

    def data_consumer(self):
        """
        Consumer thread. Takes data from queue and processes it.
        :return:
        """
        while True:
            data = self.data_queue.get(block=True)
            if data != 'quit':
                break
            self.analyzer.parse_data(data)


    def run(self):

        print('Starting Mothership.')

        # consumer = threading.Thread(target=self.data_consumer)
        # consumer.start()

        self.sock.listen(5)
        print('Mother is listening...')

        thread = None
        while True:
            try:
                worker, address = self.sock.accept()
                worker.settimeout(60)
                print('Connection Received: %s' % str(address))
                thread = threading.Thread(target=self.handle_worker_contact, args=(worker, address))
                thread.start()
                thread.join()
            except:
                if thread:
                    thread.join()
                break

        print('Shutting Down...')
        self.data_queue.put('quit')
        # consumer.join()
        print('Done.')

    def handle_worker_contact(self, worker, address):
        while True:
            try:
                frames = []
                while True:
                    frame = worker.recv(self.buff_size)
                    if frame == settings.SOCK_END_RECV or frame == '' or not frame:
                        break
                    frames.append(frame.decode('utf-8'))

                data = ''.join(frames)
                if data:
                    # json_data = json.loads(data.decode("utf-8"))
                    json_data = json.loads(data)
                    self.data_queue.put(json_data)
                else:
                    raise ValueError('No Value Given')
            except ValueError as e:
                worker.close()







