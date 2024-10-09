import asyncio
import functools
import threading
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from typing import Union

from vsol_olt_client.connection import SSH, TNET, Connection


class CLI_MODE(Enum):
    PRI = "> "
    ALT = "# "
    CONF = "(config)# "


class PROTO(Enum):
    ssh = SSH
    telnet = TNET


class VOLTClient:

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        connect_timeout: float = 5,
        proto: PROTO = PROTO.telnet,
        mutex: Union[threading.Lock, None] = None,
    ) -> None:

        self.host = host
        self.username = username
        self.password = password
        self.connect_timeout = connect_timeout
        self.shell: Connection = None
        self.proto: PROTO = proto
        self.mutex = mutex or threading.Lock()

    def __enable_pri_mode(self):
        p = self.shell.get_shell_prompt()
        if not p.endswith(CLI_MODE.PRI.value):
            # `exit` command doesn't work.
            self.shell.logout()
        self.shell.login()

    def __enable_alt_mode(self):
        p = self.shell.get_shell_prompt()
        if p.endswith(CLI_MODE.CONF.value):
            self.shell.send("exit")
            self.shell.expect([CLI_MODE.ALT.value])
        if p.endswith(CLI_MODE.PRI.value):
            self.shell.send("enable")
            self.shell.expect(["Password: "])
            self.shell.send(self.shell.password)
            self.shell.expect([CLI_MODE.ALT.value])

    def __enable_conf_mode(self):
        p = self.shell.get_shell_prompt()
        if CLI_MODE.CONF.value in p:
            return

        if p.endswith(CLI_MODE.PRI.value):
            self.shell.send("enable")
            self.shell.expect(["Password: "])
            self.shell.send(self.shell.password)
            self.shell.expect([CLI_MODE.ALT.value])

        self.shell.send("configure terminal")
        self.shell.expect([CLI_MODE.CONF.value])

    def connect(self) -> None:
        if not self.shell:
            self.shell = self.proto.value(
                self.host,
                self.username,
                self.password,
                connect_timeout=self.connect_timeout,
            )
            self.shell.login()

    def disconnect(self) -> None:
        if self.shell:
            self.shell.logout()
            self.shell = None

    def send_pri_cmd(self, msg: str, timeout: float = 5):
        if msg in ["enable", "exit"]:
            raise ValueError("Not allowed in pri mode.")
        try:
            self.mutex.acquire()
            self.__enable_pri_mode()
            self.shell.send(msg)
            _, output = self.shell.expect([CLI_MODE.PRI.value], timeout=timeout)
        finally:
            self.mutex.release()
        return output

    def send_alt_cmd(self, msg: str, timeout: float = 5):
        if msg in ["configure terminal", "exit"]:
            raise ValueError("Not allowed in alt mode.")
        try:
            self.mutex.acquire()
            self.__enable_alt_mode()
            self.shell.send(msg)
            _, output = self.shell.expect([CLI_MODE.ALT.value], timeout=timeout)
        finally:
            self.mutex.release()
        return output

    def send_conf_cmd(self, msg: str, timeout: float = 5):
        if msg in ["exit"]:
            raise ValueError("Not allowed in config mode.")
        try:
            self.mutex.acquire()
            self.__enable_conf_mode()
            self.shell.send(msg)
            _, output = self.shell.expect([CLI_MODE.CONF.value], timeout=timeout)
        finally:
            self.mutex.release()

        return output
