import socket
import struct


class MsgSocket:
    __socket__ = None

    def __init__(self, sock=None):
        if sock is None:
            self.__socket__ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.__socket__ = sock

    def __del__(self):
        self.__socket__.close()

    def settimeout(self, timeout):
        return self.__socket__.settimeout(timeout)

    def bind(self, address, port):
        return self.__socket__.bind((str(address), int(port)))

    def listen(self, backlog):
        return self.__socket__.listen(backlog)

    def accept(self):
        conn, addr = self.__socket__.accept()
        return MsgSocket(sock=conn), addr

    def connect(self, address, port):
        return self.__socket__.connect((str(address), int(port)))

    def connect_ex(self, address, port):
        return self.__socket__.connect_ex((str(address), int(port)))

    def getpeername(self):
        return self.__socket__.getpeername()

    def send_msg(self, msg):
        data = self.__prepare_data__(msg)
        return self.__socket__.sendall(data)

    def recv_msg(self):
        msg_len = self.recv_all(4)
        if not msg_len:
            return None
        msg_len = struct.unpack(">I", msg_len)[0]
        return self.recv_all(msg_len).decode("utf-8")

    def recv_all(self, n):
        data = b""
        try:
            while len(data) < n:
                packet = self.__socket__.recv(n - len(data))
                if not packet:
                    return None
                data += packet
        except ConnectionError:
            return None
        return data

    @staticmethod
    def __prepare_data__(msg):
        if type(msg) is not str:
            raise TypeError("param 'msg' must be type of str")
        data = msg.encode("utf-8")
        return struct.pack('>I', len(data)) + data
