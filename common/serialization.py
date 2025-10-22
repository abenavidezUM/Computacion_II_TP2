"""
Utilidades para serialización de datos entre procesos.
Maneja conversión de objetos a formatos transmisibles.
"""

import json
import pickle
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def serialize_json(data: Any) -> Optional[str]:
    """
    Serializa datos a JSON.
    
    Args:
        data: Datos a serializar
        
    Returns:
        String JSON o None si hay error
    """
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error serializando a JSON: {e}")
        return None


def deserialize_json(json_string: str) -> Optional[Any]:
    """
    Deserializa datos desde JSON.
    
    Args:
        json_string: String JSON
        
    Returns:
        Datos deserializados o None si hay error
    """
    try:
        return json.loads(json_string)
    except Exception as e:
        logger.error(f"Error deserializando JSON: {e}")
        return None


def serialize_pickle(data: Any) -> Optional[bytes]:
    """
    Serializa datos con pickle (para objetos complejos).
    
    Args:
        data: Datos a serializar
        
    Returns:
        Bytes con datos pickleados o None si hay error
    """
    try:
        return pickle.dumps(data)
    except Exception as e:
        logger.error(f"Error serializando con pickle: {e}")
        return None


def deserialize_pickle(data: bytes) -> Optional[Any]:
    """
    Deserializa datos desde pickle.
    
    Args:
        data: Bytes pickleados
        
    Returns:
        Datos deserializados o None si hay error
    """
    try:
        return pickle.loads(data)
    except Exception as e:
        logger.error(f"Error deserializando pickle: {e}")
        return None

