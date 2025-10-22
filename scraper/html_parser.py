"""
Funciones para parsear contenido HTML.
Extrae información estructural de páginas web.
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional
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
    # Implementación pendiente para Etapa 3
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
    # Implementación pendiente para Etapa 3
    return []


def count_images(soup: BeautifulSoup) -> int:
    """
    Cuenta el número de imágenes en la página.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        
    Returns:
        Número de imágenes encontradas
    """
    # Implementación pendiente para Etapa 3
    return 0


def analyze_structure(soup: BeautifulSoup) -> Dict[str, int]:
    """
    Analiza la estructura de headers (H1-H6) de la página.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        
    Returns:
        Diccionario con el conteo de cada tipo de header
    """
    # Implementación pendiente para Etapa 3
    return {}

