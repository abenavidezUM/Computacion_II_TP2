"""
Cliente HTTP asíncrono para descargar páginas web.
Utiliza aiohttp para operaciones no bloqueantes.
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Timeout por defecto para requests
DEFAULT_TIMEOUT = 30

# Headers para simular un navegador real
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}


async def fetch_html(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """
    Descarga el contenido HTML de una URL de forma asíncrona.
    
    Args:
        url: URL a descargar
        timeout: Timeout en segundos
        
    Returns:
        String con el HTML o None si hay error
    """
    import ssl
    import certifi
    
    try:
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        
        # Configurar SSL context con certificados de certifi
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(timeout=timeout_config, connector=connector) as session:
            async with session.get(url, headers=DEFAULT_HEADERS, allow_redirects=True) as response:
                
                if response.status == 200:
                    html = await response.text()
                    logger.info(f"HTML descargado exitosamente desde {url} ({len(html)} bytes)")
                    return html
                else:
                    logger.warning(f"Error HTTP {response.status} al descargar {url}")
                    return None
                    
    except asyncio.TimeoutError:
        logger.error(f"Timeout después de {timeout}s al intentar descargar {url}")
        return None
    except aiohttp.ClientError as e:
        logger.error(f"Error de cliente al descargar {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al descargar {url}: {e}", exc_info=True)
        return None


async def fetch_with_headers(url: str, headers: Dict[str, str],
                            timeout: int = DEFAULT_TIMEOUT) -> Optional[str]:
    """
    Descarga HTML con headers personalizados.
    
    Args:
        url: URL a descargar
        headers: Diccionario de headers HTTP
        timeout: Timeout en segundos
        
    Returns:
        String con el HTML o None si hay error
    """
    # Implementación pendiente para Etapa 3
    return None


async def download_binary(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[bytes]:
    """
    Descarga contenido binario (imágenes, etc.) de forma asíncrona.
    
    Args:
        url: URL a descargar
        timeout: Timeout en segundos
        
    Returns:
        Bytes del contenido o None si hay error
    """
    # Implementación pendiente para Etapa 8
    return None

