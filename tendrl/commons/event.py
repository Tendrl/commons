from gevent import socket
from gevent.socket import error as socket_error
from gevent.socket import timeout as socket_timeout
import sys
from tendrl.commons.message import Message


class Event(object):
    def __init__(self, message):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._write(message)

    def _write(self, message):
        try:
            json_str = Message.to_json(message)
            socket_path = tendrl_ns.config.data['logging_socket_path']
            self.sock.connect(socket_path)
            self.sock.send(json_str)
        except (socket_error) as ex:
            msg = Message.to_json(message)
            sys.stderr.write(
                "Socket connection failed.%s\n" % str(ex))
            sys.stderr.write(
                "Unable to pass the message into socket.%s\n" % msg)
        except (socket_timeout) as ex:
            msg = Message.to_json(message)
            sys.stderr.write(
                "Socket connection timeout.%s\n" % str(ex))
            sys.stderr.write(
                "Unable to pass the message into socket.%s\n" % msg)
        except (TypeError) as ex:
            sys.stderr.write("%s-%s\n" % (str(ex), message.__dict__))
        finally:
            self.sock.close()
