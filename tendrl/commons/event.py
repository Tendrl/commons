import struct

import socket
import sys
import traceback


from tendrl.commons.logger import Logger
from tendrl.commons.message import Message


class Event(object):
    def __init__(self, message, socket_path=None):
        if message.publisher == "node_agent":
            try:
                json_str = Message.to_json(message)
                message = Message.from_json(json_str)
                Logger(message)
            except (TypeError, ValueError, KeyError, AttributeError):
                sys.stderr.write(
                    "Unable to log the message.%s\n" % message)
                exc_type, exc_value, exc_tb = sys.exc_info()
                traceback.print_exception(
                    exc_type, exc_value, exc_tb, file=sys.stderr)
        else:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket_path = socket_path
            if self.socket_path is None:
                self.socket_path = NS.config.data['logging_socket_path']
            self._write(message)

    def _write(self, message):
        try:
            json_str = Message.to_json(message)
            self.sock.connect(self.socket_path)
            self._pack_and_send(json_str)
        except (socket.error, socket.timeout, TypeError):
            msg = Message.to_json(message)
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)
            sys.stderr.write(
                "Unable to pass the message into socket.%s\n" % msg)
        finally:
            self.sock.close()

    def _pack_and_send(self, msg):
        frmt = "=%ds" % len(msg)
        packedMsg = struct.pack(frmt, msg)
        packedHdr = struct.pack('=I', len(packedMsg))
        self._send(packedHdr)
        self._send(packedMsg)

    def _send(self, msg):
        sent = 0
        while sent < len(msg):
            sent += self.sock.send(msg[sent:])
