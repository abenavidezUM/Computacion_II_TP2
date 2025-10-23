"""
Funciones para parsear contenido HTML.
Extrae información estructural de páginas web.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


def extract_title(soup: BeautifulSoup) -> str:
    """
    Extrae el título de la página.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        
    Returns:
        Título de la página o string vacío si no se encuentra
    """
    try:
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            logger.debug(f"Título encontrado: {title}")
            return title
        
        # Fallback: buscar en h1
        h1 = soup.find('h1')
        if h1 and h1.string:
            title = h1.string.strip()
            logger.debug(f"Título encontrado en H1: {title}")
            return title
            
        logger.warning("No se encontró título en la página")
        return ""
        
    except Exception as e:
        logger.error(f"Error extrayendo título: {e}")
        return ""


def extract_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """
    Extrae todos los enlaces de la página.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        base_url: URL base para resolver enlaces relativos
        
    Returns:
        Lista de URLs absolutas encontradas
    """
    links = []
    
    try:
        for anchor in soup.find_all('a', href=True):
            href = anchor['href'].strip()
            
            # Ignorar enlaces vacíos, anclas y javascript
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Convertir a URL absoluta
            absolute_url = urljoin(base_url, href)
            
            # Validar que sea http o https
            parsed = urlparse(absolute_url)
            if parsed.scheme in ['http', 'https']:
                links.append(absolute_url)
        
        # Eliminar duplicados manteniendo el orden
        links = list(dict.fromkeys(links))
        
        logger.info(f"Encontrados {len(links)} enlaces únicos")
        return links
        
    except Exception as e:
        logger.error(f"Error extrayendo enlaces: {e}")
        return []


def extract_image_urls(soup: BeautifulSoup, base_url: str) -> List[str]:
    """
    Extrae las URLs de todas las imágenes de la página.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        base_url: URL base para resolver URLs relativas
        
    Returns:
        Lista de URLs absolutas de imágenes
    """
    image_urls = []
    
    try:
        for img in soup.find_all('img', src=True):
            src = img['src'].strip()
            
            if not src:
                continue
            
            # Convertir a URL absoluta
            absolute_url = urljoin(base_url, src)
            
            # Validar que sea http o https
            parsed = urlparse(absolute_url)
            if parsed.scheme in ['http', 'https']:
                image_urls.append(absolute_url)
        
        # Eliminar duplicados
        image_urls = list(dict.fromkeys(image_urls))
        
        logger.info(f"Encontradas {len(image_urls)} imágenes únicas")
        return image_urls
        
    except Exception as e:
        logger.error(f"Error extrayendo URLs de imágenes: {e}")
        return []


def count_images(soup: BeautifulSoup) -> int:
    """
    Cuenta el número de imágenes en la página.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        
    Returns:
        Número de imágenes encontradas
    """
    try:
        images = soup.find_all('img')
        count = len(images)
        logger.debug(f"Contador de imágenes: {count}")
        return count
    except Exception as e:
        logger.error(f"Error contando imágenes: {e}")
        return 0


def analyze_structure(soup: BeautifulSoup) -> Dict[str, int]:
    """
    Analiza la estructura de headers (H1-H6) de la página.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        
    Returns:
        Diccionario con el conteo de cada tipo de header
    """
    structure = {}
    
    try:
        for i in range(1, 7):
            header_tag = f'h{i}'
            count = len(soup.find_all(header_tag))
            if count > 0:
                structure[header_tag] = count
        
        logger.debug(f"Estructura de headers: {structure}")
        return structure
        
    except Exception as e:
        logger.error(f"Error analizando estructura: {e}")
        return {}

