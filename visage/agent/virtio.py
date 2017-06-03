# -*- coding:utf-8 -*-
import fcntl, signal, os, time, select, errno, sys
from pysigset import SIGSET, sigemptyset, sigaddset,\
    sigprocmask, SIG_BLOCK, SIG_UNBLOCK
from visage.utils import log
from visage.common.timeout import timeout, TimeoutError

LOG = log.Log()


class ChannelAgent(object):

    def __init__(self, conn_handler, conn_label, dispatcher, non_blocking=False):

        self.conn_label = conn_label
        self.conn_handler = conn_handler
        self.dispatcher = dispatcher
        self.non_blocking = non_blocking
        self.check_host_connection = False
        self.poller = select.poll()
        self.sigset = SIGSET()
        self._allow_sigio(self.conn_handler, self.non_blocking)

        self.fd_to_socket = {
            self.conn_handler.fileno(): self.conn_handler
        }

    @staticmethod
    def _allow_sigio(fd, non_blocking):
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        if non_blocking:
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_ASYNC | os.O_NONBLOCK)
        else:
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_ASYNC)
        fcntl.fcntl(fd, fcntl.F_SETOWN, os.getpid())

    def sigio_handler(self, signal_number, frame):
        print "get into sigio_handler"
        if not self.check_host_connection:
            print "set mask sigio"
            self.mask_sigio()
            self.check_host_connection = True

    def mask_sigio(self):
        sigemptyset(self.sigset)
        sigaddset(self.sigset, signal.SIGIO)
        sigprocmask(SIG_BLOCK, self.sigset, 0)

    def unmask_sigio(self):
        sigemptyset(self.sigset)
        sigaddset(self.sigset, signal.SIGIO)
        sigprocmask(SIG_UNBLOCK, self.sigset, 0)

    def handle_host_conn_shutdown(self):
        self.unmask_sigio()
        self.check_host_connection = False

    def handle_host_msg(self, flag):
        if flag & select.POLLIN:
            message = self.get_request_data()
            print message
            # TODO handle IOError data
            # for example, 
            if not message:
                print "no data recived"
                LOG.info("Connection closed")
                self.handle_host_conn_shutdown()
                return
            resp = self.dispatcher(message)
            # time.sleep(2)
            # TODO flush() function will always be blocked
            # if connection closed
            # before flush()

            # 如果在flush之前，主机端的连接断开了，那么flush()方法将会一直阻塞
            # 所以要设置超时机制，并且如果超时了，需要清空文件的缓冲区
            self.write_back_to_host(resp)

        # handle device unhotpluged
        elif flag & select.POLLHUP:
            sys.exit(-1)

    def get_request_data(self):
        try:
            return self._do_read()
        except TimeoutError:
            return None


    def write_back_to_host(self, resp):
        try:
            self._do_write_back(resp)
        except (IOError, TimeoutError):
            return

    @timeout(2)
    def _do_read(self):
        while True:
            try:
                data = self.conn_handler.readline()
                return data.strip()
            except IOError as error:
                if error.errno == errno.EAGAIN:
                    time.sleep(0.05)
                    continue
                else:
                    return None

    @timeout(2)
    def _do_write_back(self, resp):
        while True:
            try:
                if not resp.endswith('\n'):
                    self.conn_handler.write(resp)
                    self.conn_handler.write('\n')
                    self.conn_handler.flush()
                else:
                    self.conn_handler.write(resp)
                    self.conn_handler.flush()
                break
            except IOError:
                time.sleep(0.05)
                continue

    def run(self):
        signal.signal(signal.SIGIO, self.sigio_handler)

        while True:

            nfds = 0
            if self.check_host_connection:
                self.poller.register(self.conn_handler, select.POLLIN)
                nfds = nfds + 1

            if nfds > 0:
                try:
                    events = self.poller.poll()
                    for fd, flag in events:
                        s = self.fd_to_socket[fd]
                        if s is self.conn_handler:
                            self.handle_host_msg(flag)

                except select.error as e:
                    time.sleep(1)
            else:
                print "waiting for connection..."
                time.sleep(5)
