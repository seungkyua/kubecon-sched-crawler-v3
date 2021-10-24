from http.server import HTTPServer, BaseHTTPRequestHandler


class SimpleHTTPRequestsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(self.pretty_headers(), 'utf-8'))

    def pretty_headers(self):
        s = '\r\n'.join('{}: {}'.format(k, v) for k, v in self.headers.items())
        print(s)
        return s


def run():
    httpd = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestsHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    run()
