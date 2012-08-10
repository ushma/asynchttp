# -*- coding: utf-8 -*-

import socket
import select
import errno
from . import defaults

class Socket(socket.socket):

    def __init__(self, sock=None, poll_map=None):
        self.accepting = False
        self.connected = False
        if sock is None:
            super(Socket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self._sock = sock
            try:
                addr = self.getpeername()
                self.connected = True
            except socket.error as err:
                if err.args[0] != errno.ENOTCONN:
                    raise
        if poll_map is None:
            self.poll_map = defaults.poll_map
        else:
            self.poll_map = poll_map
        self.add_poll()
        self.set_sock()

    def set_sock(self):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.setblocking(0)

    def add_poll(self):
        self.poll_map[self.fileno] = self

    def del_poll(self):
        fd = self.fileno
        if fd in self.poll_map:
            del self.poll_map[fd]

    def log(self, type='info', msg):
        print '%s: %s' % (type, msg)

    def send(self, data):
        try:
            _send = self.send(data)
            return _send
        except socket.error as err:
            if err.args[0] in defaults.DISCONNECTED:
                self.handle_close()
                return 0
            elif err.args[0] == errno.EWOULDBLOCK:
                return 0
            else:
                raise

    def recv(self, buffer_size=4096):
        try:
            data = self.recv(buffer_size)
            return data
        except socket.error as err:
            if err.args[0] in defaults.DISCONNECTED:
                self.handle_close()
                return ''
            else:
                raise

    def handle_read(self):
        raise NotImplementedError('handle_read method should be overriden')

    def handle_write(self, data):
        raise NotImplementedError('handle_write method should be overriden')

    def handle_close(self):
        self.accepting = False
        self.connected = False
        self.del_poll()
        try:
            self.close()
        except socket.error as err:
            if err.args[0] not in (errno.EBADF, errno.ENOTCONN):
                raise


class Server(Socket):

    def listen(self, num=10):
        self.accepting = True
        return self.listen(10)

    def handle_accept(self):
        try:
            conn, addr = self.accept()
            Connection(conn)
        except TypeError:
            return None
        except socket.error as err:
            if err.args[0] == errno.EWOULDBLOCK:
                return None
            else:
                raise

    def handle_read(self):
        # accepting sockets spawn new socket connections
        if self.accepting:
            self.handle_accept()


class Connection(Socket):

    def handle_read(self):
        data = self.recv()

    def handle_write(self, data):
        output = self.send(data)


