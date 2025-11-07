"""
Validadores comunes para el sistema de scraping.
Proporciona funciones de validación reutilizables.
"""

import re
from urllib.parse import urlparse
from typing import Optional, Tuple


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Valida que una URL sea válida y accesible.
    
    Args:
        url: URL a validar
        
    Returns:
        Tupla (es_valida, mensaje_error)
    """
    if not url or not isinstance(url, str):
        return False, "URL no puede estar vacía"
    
    # Validar longitud
    if len(url) > 2048:
        return False, "URL demasiado larga (máximo 2048 caracteres)"
    
    # Validar formato básico
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "URL con formato inválido"
    
    # Validar esquema
    if parsed.scheme not in ('http', 'https'):
        return False, f"Esquema inválido: '{parsed.scheme}'. Solo se permiten http y https"
    
    # Validar dominio
    if not parsed.netloc:
        return False, "URL sin dominio válido"
    
    # Validar caracteres permitidos en dominio
    domain_pattern = re.compile(
        r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?'
        r'(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    )
    
    # Extraer dominio sin puerto
    domain = parsed.netloc.split(':')[0]
    
    if not domain_pattern.match(domain):
        return False, f"Dominio inválido: '{domain}'"
    
    # URLs bloqueadas (localhost, IPs privadas para seguridad)
    blocked_domains = ['localhost', '127.0.0.1', '0.0.0.0']
    if domain.lower() in blocked_domains:
        return False, f"Dominio bloqueado por seguridad: '{domain}'"
    
    # Validar IPs privadas
    if domain.startswith('192.168.') or domain.startswith('10.') or domain.startswith('172.'):
        return False, f"IP privada bloqueada por seguridad: '{domain}'"
    
    return True, None


def validate_port(port: int) -> Tuple[bool, Optional[str]]:
    """
    Valida que un puerto sea válido.
    
    Args:
        port: Número de puerto
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not isinstance(port, int):
        return False, "Puerto debe ser un número entero"
    
    if port < 1 or port > 65535:
        return False, f"Puerto fuera de rango: {port}. Debe estar entre 1 y 65535"
    
    # Puertos bien conocidos que probablemente no deberían usarse
    if port < 1024:
        return False, f"Puerto {port} está en rango de puertos privilegiados (< 1024)"
    
    return True, None


def validate_workers(workers: int) -> Tuple[bool, Optional[str]]:
    """
    Valida el número de workers.
    
    Args:
        workers: Número de workers
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not isinstance(workers, int):
        return False, "Número de workers debe ser un entero"
    
    if workers < 1:
        return False, f"Número de workers inválido: {workers}. Debe ser al menos 1"
    
    if workers > 32:
        return False, f"Número de workers demasiado alto: {workers}. Máximo recomendado: 32"
    
    return True, None


def validate_timeout(timeout: int) -> Tuple[bool, Optional[str]]:
    """
    Valida un valor de timeout.
    
    Args:
        timeout: Timeout en segundos
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not isinstance(timeout, (int, float)):
        return False, "Timeout debe ser un número"
    
    if timeout <= 0:
        return False, f"Timeout inválido: {timeout}. Debe ser mayor a 0"
    
    if timeout > 300:  # 5 minutos
        return False, f"Timeout demasiado alto: {timeout}s. Máximo recomendado: 300s"
    
    return True, None


def validate_image_size(width: int, height: int) -> Tuple[bool, Optional[str]]:
    """
    Valida dimensiones de imagen.
    
    Args:
        width: Ancho en pixels
        height: Alto en pixels
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not isinstance(width, int) or not isinstance(height, int):
        return False, "Dimensiones deben ser enteros"
    
    if width < 1 or height < 1:
        return False, f"Dimensiones inválidas: {width}x{height}. Deben ser positivas"
    
    if width > 4096 or height > 4096:
        return False, f"Dimensiones demasiado grandes: {width}x{height}. Máximo: 4096x4096"
    
    return True, None


def validate_quality(quality: int) -> Tuple[bool, Optional[str]]:
    """
    Valida calidad de compresión de imagen.
    
    Args:
        quality: Calidad (1-100)
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not isinstance(quality, int):
        return False, "Calidad debe ser un entero"
    
    if quality < 1 or quality > 100:
        return False, f"Calidad inválida: {quality}. Debe estar entre 1 y 100"
    
    return True, None


def validate_image_format(format_name: str) -> Tuple[bool, Optional[str]]:
    """
    Valida formato de imagen.
    
    Args:
        format_name: Nombre del formato
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if not isinstance(format_name, str):
        return False, "Formato debe ser una cadena"
    
    valid_formats = ['JPEG', 'PNG', 'WEBP', 'GIF']
    format_upper = format_name.upper()
    
    if format_upper not in valid_formats:
        return False, f"Formato inválido: '{format_name}'. Formatos permitidos: {', '.join(valid_formats)}"
    
    return True, None


def sanitize_task_data(task: dict) -> dict:
    """
    Sanitiza y valida datos de una tarea.
    
    Args:
        task: Diccionario con datos de tarea
        
    Returns:
        Diccionario sanitizado
    """
    sanitized = {}
    
    # Validar task_type
    task_type = task.get('task_type', '')
    if not isinstance(task_type, str):
        sanitized['task_type'] = 'unknown'
    else:
        sanitized['task_type'] = task_type[:50]  # Limitar longitud
    
    # Validar URL si existe
    if 'url' in task:
        url = task.get('url', '')
        if isinstance(url, str):
            sanitized['url'] = url[:2048]  # Limitar longitud
    
    # Validar image_urls si existe
    if 'image_urls' in task:
        image_urls = task.get('image_urls', [])
        if isinstance(image_urls, list):
            # Limitar a 20 URLs máximo
            sanitized['image_urls'] = [str(url)[:2048] for url in image_urls[:20]]
    
    # Copiar otros campos con límites
    for key in ['timeout', 'max_images', 'width', 'height', 'quality']:
        if key in task:
            value = task.get(key)
            if isinstance(value, (int, float)):
                sanitized[key] = value
    
    for key in ['format', 'thumbnail_size', 'full_page']:
        if key in task:
            sanitized[key] = task.get(key)
    
    return sanitized

