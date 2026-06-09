# -*- coding: UTF-8 -*-

import socket
from asyncio import StreamReader, StreamWriter

from librouteros.exceptions import ConnectionClosed, RouterSyncTimeoutError


class SocketTransport:
    def __init__(self, sock: socket.socket) -> None:
        self.sock: socket.socket = sock

    def write(self, data: bytes) -> None:
        """
        Write given bytes to socket. Loop as long as every byte in
        string is written unless exception is raised.
        """
        try:
            self.sock.sendall(data)
        except socket.timeout as error:
            raise RouterSyncTimeoutError from error

    def read(self, length: int) -> bytes:
        """
        Read as many bytes from socket as specified in length.
        Loop as long as every byte is read unless exception is raised.
        """
        data: bytearray = bytearray()
        try:
            while (to_read := length - len(data)) != 0:
                got: bytes = self.sock.recv(to_read)
                if not got:
                    raise ConnectionClosed("Connection unexpectedly closed.")
                data += got
        except socket.timeout as error:
            raise RouterSyncTimeoutError from error
        return bytes(data)

    def close(self) -> None:
        self.sock.close()


class AsyncSocketTransport:
    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.reader: StreamReader = reader
        self.writer: StreamWriter = writer

    async def write(self, data: bytes) -> None:
        """
        Write given bytes to socket. Loop as long as every byte in
        string is written unless exception is raised.
        """
        self.writer.write(data)
        await self.writer.drain()

    async def read(self, length: int) -> bytes:
        """
        Read as many bytes from socket as specified in length.
        Loop as long as every byte is read unless exception is raised.
        """
        data: bytearray = bytearray()
        while (to_read := length - len(data)) != 0:
            got: bytes = await self.reader.read(to_read)
            if not got:
                raise ConnectionClosed("Connection unexpectedly closed.")
            data += got
        return bytes(data)

    async def close(self) -> None:
        self.writer.close()
        await self.writer.wait_closed()
