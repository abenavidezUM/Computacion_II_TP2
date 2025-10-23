"""
Funciones para extraer metadatos de páginas web.
Incluye meta tags, Open Graph, etc.
"""

from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def extract_meta_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extrae meta tags relevantes de la página.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        
    Returns:
        Diccionario con los meta tags encontrados
        (description, keywords, Open Graph tags, etc.)
    """
    meta_tags = {}
    
    try:
        # Extraer meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            meta_tags['description'] = meta_desc['content'].strip()
        
        # Extraer meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            meta_tags['keywords'] = meta_keywords['content'].strip()
        
        # Extraer meta author
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            meta_tags['author'] = meta_author['content'].strip()
        
        # Extraer Open Graph tags
        og_tags = extract_open_graph_tags(soup)
        meta_tags.update(og_tags)
        
        # Extraer Twitter Card tags
        twitter_tags = extract_twitter_tags(soup)
        meta_tags.update(twitter_tags)
        
        logger.info(f"Extraídos {len(meta_tags)} meta tags")
        return meta_tags
        
    except Exception as e:
        logger.error(f"Error extrayendo meta tags: {e}")
        return {}


def extract_open_graph_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extrae específicamente los tags de Open Graph.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        
    Returns:
        Diccionario con los tags OG encontrados
    """
    og_tags = {}
    
    try:
        # Buscar todos los meta tags con property que empiecen con og:
        og_metas = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        
        for meta in og_metas:
            property_name = meta.get('property')
            content = meta.get('content')
            
            if property_name and content:
                og_tags[property_name] = content.strip()
        
        logger.debug(f"Extraídos {len(og_tags)} Open Graph tags")
        return og_tags
        
    except Exception as e:
        logger.error(f"Error extrayendo Open Graph tags: {e}")
        return {}


def extract_twitter_tags(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extrae los tags de Twitter Card.
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        
    Returns:
        Diccionario con los tags de Twitter encontrados
    """
    twitter_tags = {}
    
    try:
        # Buscar todos los meta tags con name que empiecen con twitter:
        twitter_metas = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        
        for meta in twitter_metas:
            name = meta.get('name')
            content = meta.get('content')
            
            if name and content:
                twitter_tags[name] = content.strip()
        
        logger.debug(f"Extraídos {len(twitter_tags)} Twitter Card tags")
        return twitter_tags
        
    except Exception as e:
        logger.error(f"Error extrayendo Twitter tags: {e}")
        return {}


def extract_schema_data(soup: BeautifulSoup) -> Dict:
    """
    Extrae datos estructurados (JSON-LD, Schema.org).
    
    Args:
        soup: Objeto BeautifulSoup con el HTML parseado
        
    Returns:
        Diccionario con los datos estructurados encontrados
    """
    # Implementación pendiente para bonus track
    return {}

