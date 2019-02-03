
import os
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

    shill_file = None
    noshill_file = None

    def __init__(self):
        self.host = settings.MOTHERSHIP.get('host', 'localhost')
        self.port = settings.MOTHERSHIP.get('port', 8080)
        self.buff_size = settings.BUFFER_SIZE

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.shill_file = '%s/resources/shill_file.txt' % os.getcwd()
        self.noshill_file = '%s/resources/not_shill.txt' % os.getcwd()

        self.data_queue = Queue()
        self.analyzer = DataAnalyzer(self.shill_file, self.noshill_file)

    def data_consumer(self):
        """
        Consumer thread. Takes data from queue and processes it.
        :return:
        """
        while True:
            try:
                data = self.data_queue.get()
                # print('DEBUG: %s\n' % data)
                self.analyzer.classify_data(data)
                self.data_queue.task_done()
                if data == 'quit':
                    break

            except:
                print('EXCEPTION! Could not parse data. Skipping.')
                self.data_queue.task_done()

    def run(self):

        print('Starting Mothership.')

        consumer = threading.Thread(target=self.data_consumer)
        consumer.daemon = True
        consumer.start()

        self.sock.listen(10)
        print('Mother is listening...')

        thread = None
        while True:
            try:
                worker, address = self.sock.accept()
                worker.settimeout(60)
                print('Connection Received: %s' % str(address))
                thread = threading.Thread(target=self.handle_worker_contact, args=(worker, address)).start()
            except:
                print('EXCEPTION! Could not operate.')
                if thread:
                    thread.join()
                break

        print('Shutting Down...')
        self.data_queue.put('quit')
        self.data_queue.join()
        consumer.join()
        print('Done.')

    def handle_worker_contact(self, worker, address):

        try:
            frames = []
            while True:
                frame = worker.recv(self.buff_size)
                if frame == settings.SOCK_END_RECV or frame == '' or not frame:
                    worker.close()
                    break
                frames.append(frame.decode('utf-8'))

            data = ''.join(frames)
            if data:
                json_data = json.loads(data)
                self.data_queue.put(json_data)

        except ValueError as e:
            worker.close()







