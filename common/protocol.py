"""
Protocolo de comunicación entre servidores.
Define el formato de mensajes y funciones de envío/recepción.
"""

import json
import struct
import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Formato del protocolo: [LENGTH(4 bytes)][JSON payload]
HEADER_FORMAT = '!I'  # Unsigned int, network byte order
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def encode_message(data: Dict) -> bytes:
    """
    Codifica un mensaje para envío por socket.
    
    Args:
        data: Diccionario con los datos a enviar
        
    Returns:
        Bytes con el mensaje codificado (header + payload)
    """
    # Implementación pendiente para Etapa 5
    return b''


def decode_message(data: bytes) -> Optional[Dict]:
    """
    Decodifica un mensaje recibido por socket.
    
    Args:
        data: Bytes recibidos
        
    Returns:
        Diccionario con los datos decodificados o None si hay error
    """
    # Implementación pendiente para Etapa 5
    return None


async def send_to_processor(host: str, port: int, task: Dict,
                           timeout: int = 30) -> Optional[Dict]:
    """
    Envía una tarea al servidor de procesamiento y espera la respuesta.
    
    Args:
        host: Host del servidor de procesamiento
        port: Puerto del servidor de procesamiento
        task: Diccionario con la tarea a ejecutar
        timeout: Timeout en segundos
        
    Returns:
        Diccionario con la respuesta o None si hay error
    """
    # Implementación pendiente para Etapa 5
    return None


async def receive_full_message(reader: asyncio.StreamReader) -> Optional[bytes]:
    """
    Recibe un mensaje completo siguiendo el protocolo.
    
    Args:
        reader: StreamReader de asyncio
        
    Returns:
        Bytes del mensaje completo o None si hay error
    """
    # Implementación pendiente para Etapa 5
    return None

