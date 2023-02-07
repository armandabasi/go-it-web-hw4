import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import json
import socket
from threading import Thread
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

BASE_DIR = pathlib.Path()
FILE_NAME = 'data.json'
STORAGE_NAME = 'storage'
STORAGE_DIR = BASE_DIR.joinpath(STORAGE_NAME)
STORAGE_FILE = STORAGE_DIR / FILE_NAME
env = Environment(loader=FileSystemLoader('templates'))
SERVER_IP_ADDRESS = '127.0.0.1'
SERVER_PORT = 5000


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/about_me':
            self.render_templates('about_me.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def render_templates(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open('about_me.json', 'r', encoding='utf-8') as fd:
            r = json.load(fd)
        template = env.get_template(filename)
        print(template)
        html = template.render(blogs=r)
        self.wfile.write(html.encode())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        send_data_to_socket(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


def send_data_to_socket(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(data, (SERVER_IP_ADDRESS, SERVER_PORT))
    client_socket.close()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('0.0.0.0', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def save_data(data):
    data_parse = urllib.parse.unquote_plus(data.decode())
    try:
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        time_to_get = str(datetime.now())
        if STORAGE_FILE.exists():
            with open(STORAGE_FILE, 'r', encoding='utf-8') as fd:
                data = json.load(fd)
            data[time_to_get] = data_dict
        else:
            data = {time_to_get: data_dict}
        with open(STORAGE_FILE, 'w', encoding='utf-8') as fd:
            json.dump(data, fd, ensure_ascii=False)
    except ValueError as err:
        logging.error(f'Field parse data {data_parse} with error {err}')
    except OSError as err:
        logging.error(f'Field write data {data_parse} with error {err}')


def run_socket_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    server_socket.bind(server)
    try:
        while True:
            data, address = server_socket.recvfrom(1024)
            save_data(data)
    except KeyboardInterrupt:
        logging.info('Socked server stopped')
    finally:
        server_socket.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")

    if not STORAGE_FILE.exists():
        with open(STORAGE_FILE, 'w', encoding='utf-8') as fd :
            json.dump({}, fd, ensure_ascii=False)

    thread_server = Thread(target=run)
    thread_server.start()

    thread_socket = Thread(target=run_socket_server(SERVER_IP_ADDRESS, SERVER_PORT))
    thread_socket.start()