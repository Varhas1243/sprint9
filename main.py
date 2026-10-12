import json
from http.server import HTTPServer, BaseHTTPRequestHandler

USERS_LIST = [
    {
        "id": 1,
        "username": "theUser",
        "firstName": "John",
        "lastName": "James",
        "email": "john@email.com",
        "password": "12345",
    }
]

FIELDS = {
    "username": str,
    "firstName": str,
    "lastName": str,
    "email": str,
    "password": str,
}


def is_valid(data, with_id=True):
    fields = dict(FIELDS, id=int) if with_id else FIELDS
    return (isinstance(data, dict)
            and data.keys() == fields.keys()
            and all(isinstance(data[key], typ) for key, typ in fields.items()))


def find_user(user_id):
    for user in USERS_LIST:
        if str(user["id"]) == user_id:
            return user


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_response(self, status_code=200, body=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body if body is not None else {}).encode('utf-8'))

    def _pars_body(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        return json.loads(self.rfile.read(content_length).decode('utf-8'))  # <--- Gets the data itself

    def do_GET(self):
        if self.path == '/reset':
            USERS_LIST[:] = [{
                "id": 1,
                "username": "theUser",
                "firstName": "John",
                "lastName": "James",
                "email": "john@email.com",
                "password": "12345",
            }]
            self._set_response(200)
        elif self.path == '/users':
            self._set_response(200, USERS_LIST)
        elif self.path.startswith('/user/'):
            username = self.path.split('/')[-1]
            for user in USERS_LIST:
                if user["username"] == username:
                    self._set_response(200, user)
                    return
            self._set_response(400, {"error": "User not found"})
        else:
            self._set_response(418)

    def do_POST(self):
        try:
            data = self._pars_body()
        except (TypeError, ValueError):
            data = None

        if self.path == '/user':
            users = [data]
        elif self.path == '/user/createWithList':
            users = data
        else:
            self._set_response(418)
            return

        if not isinstance(users, list) or not all(is_valid(u) for u in users):
            self._set_response(400)
            return

        ids = [u["id"] for u in USERS_LIST + users]
        if len(ids) != len(set(ids)):
            self._set_response(400)
            return

        USERS_LIST.extend(users)
        self._set_response(201, data)

    def do_PUT(self):
        if not self.path.startswith('/user/'):
            self._set_response(418)
            return

        try:
            data = self._pars_body()
        except (TypeError, ValueError):
            data = None

        if not is_valid(data, with_id=False):
            self._set_response(400, {"error": "not valid request data"})
            return

        user = find_user(self.path.split('/')[-1])
        if user is None:
            self._set_response(404, {"error": "User not found"})
            return

        user.update(data)
        self._set_response(200, user)

    def do_DELETE(self):
        user = find_user(self.path.split('/')[-1])
        if user is None:
            self._set_response(404, {"error": "User not found"})
            return

        USERS_LIST.remove(user)
        self._set_response(200)


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, host='localhost', port=8000):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()