import time
from abc import ABC, abstractmethod
from telnetlib import Telnet
from paramiko import SSHClient, AutoAddPolicy


class Connection(ABC):

    @abstractmethod
    def login(self) -> None:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    @abstractmethod
    def get_shell_prompt(self) -> str:
        pass

    @abstractmethod
    def send(self) -> None:
        pass

    @abstractmethod
    def expect(self, match: list, timeout: float) -> (int, str):
        pass


class TNET(Connection):

    LOGIN_P = ["Login: ", "Password: ", "> "]
    SHELL_P = ["> ", "# "]

    def __init__(self, host: str, username: str, password: str, port: int = 23, connect_timeout: float = 5):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.connect_timeout = connect_timeout
        self.conn = None
        self._codec = 'ascii'
        self._encode = lambda x: x.encode(self._codec)
        self._decode = lambda x: x.decode(self._codec)
    
    def _isalive(self):
        return (self.conn and self.conn.eof!=True)

    def login(self):
        if self._isalive():
            return
        self.conn = Telnet(
            self.host, self.port, 
            timeout=self.connect_timeout)
        self.expect(self.LOGIN_P)
        self.send(self.username)
        p, _ = self.expect(self.LOGIN_P)
        if p != 1: raise ValueError("Invalid username.")
        self.send(self.password)
        p, _ = self.expect(self.LOGIN_P)
        if p!=2: raise ValueError("Invalid password.")

        # disable paging
        self.send('terminal length 0')
        self.expect(self.LOGIN_P)
    
    def logout(self):
        if not self.conn:
            return

        self.conn.close()
        self.conn = None

    def get_shell_prompt(self):
        self.send('')
        _, res = self.expect(self.SHELL_P)
        return res.strip('\r\n')

    def send(self, msg: str):
        self.conn.write(self._encode(msg)+b'\n')

    def expect(self, match: list, timeout: float = 5):
        match = [ self._encode(each) for each in match ]
        pos, _, res = self.conn.expect(match, timeout)
        return (pos, self._decode(res))

class SSH(Connection):

    LOGIN_P = ["Login: ", "Password: ", "> "]
    SHELL_P = ["> ", "# "]

    def __init__(self, host: str, username: str, password: str, port: int = 22, connect_timeout: float = 5):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.connect_timeout = connect_timeout
        self.conn = None
        self.shell = None
        self.transport = None
        self._codec = 'utf-8'
        self._encode = lambda x: x.encode(self._codec)
        self._decode = lambda x: x.decode(self._codec)
    
    def _isalive(self):
        return self.transport and self.transport.is_active()

    def login(self):
        if self._isalive():
            return
        self.conn = SSHClient()
        self.conn.set_missing_host_key_policy(AutoAddPolicy())
        self.conn.connect(
            self.host, port=self.port,
            username=self.username, password=self.password, 
            timeout=self.connect_timeout)
        self.transport = self.conn.get_transport()
        self.shell = self.conn.invoke_shell()
        self.expect(self.LOGIN_P)
        self.send(self.username)
        p, _ = self.expect(self.LOGIN_P)
        if p != 1: raise ValueError("Invalid username.")
        self.send(self.password)
        p, _ = self.expect(self.LOGIN_P)
        if p!=2: raise ValueError("Invalid password.")

        # disable paging
        self.send('terminal length 0')
        self.expect(self.LOGIN_P)


    def logout(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.transport:
            self.transport.close()
            self.transport = None

    def get_shell_prompt(self):
        self.send('')
        _, res = self.expect(self.SHELL_P)
        return res.strip('\r\n')

    def send(self, msg: str, timeout: float = 5):
        timeout = time.time()+timeout # seconds
        while not self.shell.send_ready():
            time.sleep(0.01)
            if time.time() > timeout:
                raise TimeoutError('Wait send ready timeout occurs.')
        self.shell.send(self._encode(msg)+b'\n')

    def expect(self, match: list, timeout: float=10):
        timeout = time.time()+timeout # seconds
        pos = -1
        res = ""
        while True:
            if self.shell.recv_ready():
                raw = self.shell.recv(4096)
                res += self._decode(raw)
            time.sleep(0.01)
            for i, p in enumerate(match):
                if res.endswith(p):
                    pos = i
                    break
            if pos != -1:
                break
            if time.time() > timeout:
                raise TimeoutError('Expect timeout occurs.')

        return pos, res
