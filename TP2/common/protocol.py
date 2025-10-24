"""
Protocolo de comunicación entre servidores.
Define el formato de mensajes y funciones de envío/recepción.
Protocolo: [LENGTH(4 bytes)][JSON payload]
"""

import json
import struct
import asyncio
import socket
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Formato del protocolo: [LENGTH(4 bytes)][JSON payload]
HEADER_FORMAT = '!I'  # Unsigned int, network byte order
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def encode_message(data: Dict) -> bytes:
    """
    Codifica un mensaje para envío por socket.
    Formato: [4 bytes length][JSON payload]
    
    Args:
        data: Diccionario con los datos a enviar
        
    Returns:
        Bytes con el mensaje codificado (header + payload)
    """
    try:
        # Serializar a JSON
        json_data = json.dumps(data, ensure_ascii=False)
        payload = json_data.encode('utf-8')
        
        # Crear header con la longitud del payload
        length = len(payload)
        header = struct.pack(HEADER_FORMAT, length)
        
        # Retornar header + payload
        message = header + payload
        logger.debug(f"Mensaje codificado: {length} bytes")
        
        return message
        
    except Exception as e:
        logger.error(f"Error codificando mensaje: {e}", exc_info=True)
        return b''


def decode_message(data: bytes) -> Optional[Dict]:
    """
    Decodifica un mensaje recibido por socket.
    Espera formato: [4 bytes length][JSON payload]
    
    Args:
        data: Bytes recibidos (incluyendo header)
        
    Returns:
        Diccionario con los datos decodificados o None si hay error
    """
    try:
        if len(data) < HEADER_SIZE:
            logger.error(f"Mensaje muy corto: {len(data)} bytes")
            return None
        
        # Extraer header
        header = data[:HEADER_SIZE]
        length = struct.unpack(HEADER_FORMAT, header)[0]
        
        # Extraer payload
        payload = data[HEADER_SIZE:HEADER_SIZE + length]
        
        if len(payload) != length:
            logger.error(f"Payload incompleto: esperados {length}, recibidos {len(payload)}")
            return None
        
        # Decodificar JSON
        json_str = payload.decode('utf-8')
        message = json.loads(json_str)
        
        logger.debug(f"Mensaje decodificado: {length} bytes")
        return message
        
    except Exception as e:
        logger.error(f"Error decodificando mensaje: {e}", exc_info=True)
        return None


def receive_message_sync(sock: socket.socket) -> Optional[Dict]:
    """
    Recibe un mensaje completo de un socket de forma síncrona.
    
    Args:
        sock: Socket del que recibir
        
    Returns:
        Diccionario con el mensaje o None si hay error
    """
    try:
        # Recibir header (4 bytes)
        header_data = b''
        while len(header_data) < HEADER_SIZE:
            chunk = sock.recv(HEADER_SIZE - len(header_data))
            if not chunk:
                logger.error("Conexión cerrada mientras se recibía header")
                return None
            header_data += chunk
        
        # Parsear longitud
        length = struct.unpack(HEADER_FORMAT, header_data)[0]
        
        if length > 10 * 1024 * 1024:  # Límite de 10MB
            logger.error(f"Mensaje demasiado grande: {length} bytes")
            return None
        
        # Recibir payload
        payload_data = b''
        while len(payload_data) < length:
            chunk = sock.recv(length - len(payload_data))
            if not chunk:
                logger.error("Conexión cerrada mientras se recibía payload")
                return None
            payload_data += chunk
        
        # Decodificar JSON
        json_str = payload_data.decode('utf-8')
        message = json.loads(json_str)
        
        logger.debug(f"Mensaje recibido: {length} bytes")
        return message
        
    except Exception as e:
        logger.error(f"Error recibiendo mensaje: {e}", exc_info=True)
        return None


def send_message_sync(sock: socket.socket, data: Dict) -> bool:
    """
    Envía un mensaje completo a un socket de forma síncrona.
    
    Args:
        sock: Socket al que enviar
        data: Diccionario con los datos a enviar
        
    Returns:
        True si se envió correctamente, False en caso contrario
    """
    try:
        message = encode_message(data)
        if not message:
            return False
        
        # Enviar todo el mensaje
        sock.sendall(message)
        logger.debug(f"Mensaje enviado: {len(message)} bytes")
        
        return True
        
    except Exception as e:
        logger.error(f"Error enviando mensaje: {e}", exc_info=True)
        return False


async def send_to_processor(host: str, port: int, task: Dict,
                           timeout: int = 30) -> Optional[Dict]:
    """
    Envía una tarea al servidor de procesamiento y espera la respuesta.
    Versión asíncrona para usar desde el servidor de scraping.
    
    Args:
        host: Host del servidor de procesamiento
        port: Puerto del servidor de procesamiento
        task: Diccionario con la tarea a ejecutar
        timeout: Timeout en segundos
        
    Returns:
        Diccionario con la respuesta o None si hay error
    """
    try:
        # Abrir conexión asíncrona
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        
        # Codificar y enviar mensaje
        message = encode_message(task)
        writer.write(message)
        await writer.drain()
        
        logger.info(f"Tarea enviada al procesador: {task.get('task_type', 'unknown')}")
        
        # Recibir respuesta
        # Leer header
        header_data = await asyncio.wait_for(
            reader.readexactly(HEADER_SIZE),
            timeout=timeout
        )
        
        length = struct.unpack(HEADER_FORMAT, header_data)[0]
        
        if length > 10 * 1024 * 1024:  # Límite de 10MB
            logger.error(f"Respuesta demasiado grande: {length} bytes")
            writer.close()
            await writer.wait_closed()
            return None
        
        # Leer payload
        payload_data = await asyncio.wait_for(
            reader.readexactly(length),
            timeout=timeout
        )
        
        # Decodificar respuesta
        json_str = payload_data.decode('utf-8')
        response = json.loads(json_str)
        
        logger.info(f"Respuesta recibida del procesador: {response.get('status', 'unknown')}")
        
        # Cerrar conexión
        writer.close()
        await writer.wait_closed()
        
        return response
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout comunicándose con procesador {host}:{port}")
        return None
    except Exception as e:
        logger.error(f"Error comunicándose con procesador: {e}", exc_info=True)
        return None

