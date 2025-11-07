"""
Límites y configuraciones de recursos del sistema.
Define valores máximos y timeouts para evitar abusos.
"""

# Límites de scraping
MAX_URL_LENGTH = 2048
MAX_SCRAPING_TIMEOUT = 60  # segundos
DEFAULT_SCRAPING_TIMEOUT = 30
MIN_SCRAPING_TIMEOUT = 5

# Límites de procesamiento
MAX_PROCESSING_TIMEOUT = 120  # segundos
DEFAULT_PROCESSING_TIMEOUT = 60
MAX_SCREENSHOT_TIMEOUT = 60
MAX_PERFORMANCE_TIMEOUT = 60

# Límites de imágenes
MAX_IMAGE_URLS = 20
MAX_IMAGES_TO_PROCESS = 10
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGE_DIMENSION = 4096
MIN_IMAGE_DIMENSION = 1
DEFAULT_THUMBNAIL_SIZE = (150, 150)
MAX_THUMBNAIL_DIMENSION = 500

# Límites de calidad
MIN_QUALITY = 1
MAX_QUALITY = 100
DEFAULT_QUALITY = 85

# Límites de workers
MIN_WORKERS = 1
MAX_WORKERS = 32
DEFAULT_WORKERS = 4

# Límites de puertos
MIN_PORT = 1024  # Evitar puertos privilegiados
MAX_PORT = 65535
DEFAULT_SCRAPING_PORT = 8000
DEFAULT_PROCESSING_PORT = 9000

# Límites de concurrencia
MAX_CONCURRENT_REQUESTS = 100
MAX_QUEUE_SIZE = 1000

# Dominios bloqueados por seguridad
BLOCKED_DOMAINS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '::1'
]

# Patrones de IP privadas (para bloquear)
PRIVATE_IP_PREFIXES = [
    '192.168.',
    '10.',
    '172.16.',
    '172.17.',
    '172.18.',
    '172.19.',
    '172.20.',
    '172.21.',
    '172.22.',
    '172.23.',
    '172.24.',
    '172.25.',
    '172.26.',
    '172.27.',
    '172.28.',
    '172.29.',
    '172.30.',
    '172.31.',
]

# Formatos de imagen soportados
SUPPORTED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP', 'GIF']

# User agents (rotar para evitar blocks)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


def get_safe_timeout(timeout: int, max_timeout: int, default_timeout: int) -> int:
    """
    Retorna un timeout seguro dentro de los límites.
    
    Args:
        timeout: Timeout solicitado
        max_timeout: Timeout máximo permitido
        default_timeout: Timeout por defecto si el valor es inválido
        
    Returns:
        Timeout seguro
    """
    if timeout is None or not isinstance(timeout, (int, float)):
        return default_timeout
    
    timeout = int(timeout)
    
    if timeout < MIN_SCRAPING_TIMEOUT:
        return default_timeout
    
    if timeout > max_timeout:
        return max_timeout
    
    return timeout


def get_safe_quality(quality: int) -> int:
    """
    Retorna una calidad segura dentro de los límites.
    
    Args:
        quality: Calidad solicitada
        
    Returns:
        Calidad segura
    """
    if quality is None or not isinstance(quality, int):
        return DEFAULT_QUALITY
    
    if quality < MIN_QUALITY:
        return MIN_QUALITY
    
    if quality > MAX_QUALITY:
        return MAX_QUALITY
    
    return quality


def get_safe_dimension(width: int, height: int, max_dim: int = MAX_IMAGE_DIMENSION) -> tuple:
    """
    Retorna dimensiones seguras dentro de los límites.
    
    Args:
        width: Ancho solicitado
        height: Alto solicitado
        max_dim: Dimensión máxima permitida
        
    Returns:
        Tupla (width, height) seguras
    """
    if not isinstance(width, int) or not isinstance(height, int):
        return DEFAULT_THUMBNAIL_SIZE
    
    width = max(MIN_IMAGE_DIMENSION, min(width, max_dim))
    height = max(MIN_IMAGE_DIMENSION, min(height, max_dim))
    
    return (width, height)


def get_safe_max_images(max_images: int) -> int:
    """
    Retorna un número seguro de imágenes a procesar.
    
    Args:
        max_images: Número solicitado
        
    Returns:
        Número seguro
    """
    if not isinstance(max_images, int):
        return 5
    
    if max_images < 1:
        return 1
    
    if max_images > MAX_IMAGES_TO_PROCESS:
        return MAX_IMAGES_TO_PROCESS
    
    return max_images

