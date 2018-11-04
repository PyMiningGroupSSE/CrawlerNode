import json
import time
from msg_socket import MsgSocket

# define request command strings
__CMD_CONNECT__ = "connect"
__CMD_TASK__ = "task"
__CMD_XPATH__ = "xpath"
__CMD_SUBMIT__ = "submit"
__CMD_EXIT__ = "exit"

# define connection status codes
__CODE_CONN_SUCCESS__ = 100
__CODE_CONN_FAILED__ = 101
__CODE_TASK_SUCCESS__ = 200
__CODE_TASK_FAILED__ = 201
__CODE_TASK_EMPTY__ = 210
__CODE_XPATH_SUCCESS__ = 300
__CODE_XPATH_FAILED__ = 301
__CODE_SUBMIT_SUCCESS__ = 400
__CODE_SUBMIT_FAILED__ = 401
__CODE_SUBMIT_EXIT__ = 410

# define connection macros
__BUFF_SIZE__ = 4096


class ClientConnection:
    __pysocket__ = None
    __client_id__ = None

    __flag_connected__ = False

    # init the class and establish the socket connection
    def __init__(self, client_id, address, port):
        self.__client_id__ = client_id
        self.__pysocket__ = MsgSocket()
        while self.__pysocket__.connect_ex(address, port) != 0:
            print("server offline")
            time.sleep(3)

    # connect to the server and exchange information
    # program will block here until the connection established
    def connect(self):
        if self.__flag_connected__:
            raise ConnectionError("server already connected")
        req = dict(id=self.__client_id__, cmd=__CMD_CONNECT__, data=None)
        while True:
            res = self.__request__(req)
            if int(res["status"]) == __CODE_CONN_SUCCESS__:
                break
            else:
                print("connection error")
                time.sleep(3)
        peer = self.__pysocket__.getpeername()
        print("connected to {0} on port {1}".format(peer[0], peer[1]))
        self.__flag_connected__ = True

    # request the server for sending task(s)
    # will return a list of urls
    def request_tasks(self, count=1):
        if not self.__flag_connected__:
            raise ConnectionError("server not connected")
        req = dict(id=self.__client_id__, cmd=__CMD_TASK__, data={"count": count})
        while True:
            res = self.__request__(req)
            if int(res["status"]) == __CODE_TASK_SUCCESS__:
                break
            elif int(res["status"]) == __CODE_TASK_EMPTY__:
                print("server task list empty")
                time.sleep(3)
            else:
                print("task request error")
                time.sleep(3)
        return res["data"]["urls"]

    # request the server for the xpath rules
    # param host is host field in the url. eg: news.163.com
    def request_xpath(self, host):
        if not self.__flag_connected__:
            raise ConnectionError("server not connected")
        req = dict(id=self.__client_id__, cmd=__CMD_XPATH__, data={"host": host})
        res = self.__request__(req)
        if int(res["status"]) == __CODE_XPATH_SUCCESS__:
            return res["data"][host]
        else:
            return None

    # submit parsed data to the server
    # param data must be an instance of list
    def submit_data(self, data_list):
        if not self.__flag_connected__:
            raise ConnectionError("server not connected")
        if type(data_list) is not list:
            raise TypeError("param 'data_list' must be type of 'list'")
        req = dict(id=self.__client_id__, cmd=__CMD_SUBMIT__, data={"artilist": data_list})
        while True:
            self.__pysocket__.send_msg(json.dumps(req))
            res = json.loads(self.__pysocket__.recv_msg())
            if int(res["status"]) == __CODE_SUBMIT_SUCCESS__:
                return 0
            elif int(res["status"]) == __CODE_SUBMIT_EXIT__:
                return 1
            else:
                print("data submission error, retry after 3 seconds")
                time.sleep(3)

    def __request__(self, req):
        self.__pysocket__.send_msg(json.dumps(req))
        res = json.loads(self.__pysocket__.recv_msg())
        return res
