"""
Tests unitarios para funciones de scraping.
"""

import pytest
from bs4 import BeautifulSoup


# Importar funciones a testear
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.html_parser import (
    extract_title,
    extract_links,
    extract_image_urls,
    count_images,
    analyze_structure
)
from scraper.metadata_extractor import (
    extract_meta_tags,
    extract_open_graph_tags,
    extract_twitter_tags
)


# HTML de prueba
HTML_TEST = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page Title</title>
    <meta name="description" content="Test description">
    <meta name="keywords" content="test, keywords">
    <meta property="og:title" content="OG Title">
    <meta property="og:description" content="OG Description">
    <meta name="twitter:card" content="summary">
</head>
<body>
    <h1>Main Heading</h1>
    <h2>Subheading 1</h2>
    <h2>Subheading 2</h2>
    <h3>Subsubheading</h3>
    
    <a href="https://example.com">External Link</a>
    <a href="/relative/path">Relative Link</a>
    <a href="#anchor">Anchor Link</a>
    
    <img src="https://example.com/image1.jpg" alt="Image 1">
    <img src="/images/image2.png" alt="Image 2">
    <img src="relative/image3.gif">
</body>
</html>
"""


class TestHTMLParser:
    """Tests para html_parser.py"""
    
    def test_extract_title_success(self):
        """Test: Extracción de título correcta"""
        soup = BeautifulSoup(HTML_TEST, 'html.parser')
        title = extract_title(soup)
        assert title == "Test Page Title"
    
    def test_extract_title_fallback_h1(self):
        """Test: Título cae back a H1 si no hay <title>"""
        html = "<html><body><h1>H1 Title</h1></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        title = extract_title(soup)
        assert title == "H1 Title"
    
    def test_extract_title_empty(self):
        """Test: Sin título ni H1 retorna 'Sin título'"""
        html = "<html><body><p>Content</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        title = extract_title(soup)
        assert title == "Sin título"
    
    def test_extract_links(self):
        """Test: Extracción de enlaces"""
        base_url = "https://test.com"
        soup = BeautifulSoup(HTML_TEST, 'html.parser')
        links = extract_links(soup, base_url)
        
        assert len(links) == 3  # Solo enlaces válidos (no anchors)
        assert "https://example.com" in links
        assert "https://test.com/relative/path" in links
    
    def test_extract_links_absolute_conversion(self):
        """Test: URLs relativas se convierten a absolutas"""
        base_url = "https://test.com/page"
        html = '<html><body><a href="/about">About</a></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        links = extract_links(soup, base_url)
        
        assert "https://test.com/about" in links
    
    def test_extract_image_urls(self):
        """Test: Extracción de URLs de imágenes"""
        base_url = "https://test.com"
        soup = BeautifulSoup(HTML_TEST, 'html.parser')
        images = extract_image_urls(soup, base_url)
        
        assert len(images) == 3
        assert "https://example.com/image1.jpg" in images
        assert "https://test.com/images/image2.png" in images
    
    def test_count_images(self):
        """Test: Conteo de imágenes"""
        soup = BeautifulSoup(HTML_TEST, 'html.parser')
        count = count_images(soup)
        assert count == 3
    
    def test_analyze_structure(self):
        """Test: Análisis de estructura de headings"""
        soup = BeautifulSoup(HTML_TEST, 'html.parser')
        structure = analyze_structure(soup)
        
        assert structure['h1'] == 1
        assert structure['h2'] == 2
        assert structure['h3'] == 1
        assert structure['h4'] == 0
        assert structure['h5'] == 0
        assert structure['h6'] == 0
    
    def test_analyze_structure_empty(self):
        """Test: Estructura sin headings"""
        html = "<html><body><p>No headings</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        structure = analyze_structure(soup)
        
        assert all(count == 0 for count in structure.values())


class TestMetadataExtractor:
    """Tests para metadata_extractor.py"""
    
    def test_extract_meta_tags(self):
        """Test: Extracción de meta tags básicos"""
        soup = BeautifulSoup(HTML_TEST, 'html.parser')
        meta = extract_meta_tags(soup)
        
        assert meta['description'] == "Test description"
        assert meta['keywords'] == "test, keywords"
    
    def test_extract_meta_tags_empty(self):
        """Test: Meta tags vacíos cuando no existen"""
        html = "<html><head></head><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        meta = extract_meta_tags(soup)
        
        assert meta['description'] is None
        assert meta['keywords'] is None
        assert meta['author'] is None
    
    def test_extract_open_graph_tags(self):
        """Test: Extracción de Open Graph tags"""
        soup = BeautifulSoup(HTML_TEST, 'html.parser')
        og = extract_open_graph_tags(soup)
        
        assert og['og:title'] == "OG Title"
        assert og['og:description'] == "OG Description"
    
    def test_extract_open_graph_tags_empty(self):
        """Test: OG tags vacíos cuando no existen"""
        html = "<html><head></head><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        og = extract_open_graph_tags(soup)
        
        assert len(og) == 0
    
    def test_extract_twitter_tags(self):
        """Test: Extracción de Twitter Card tags"""
        soup = BeautifulSoup(HTML_TEST, 'html.parser')
        twitter = extract_twitter_tags(soup)
        
        assert twitter['twitter:card'] == "summary"
    
    def test_extract_twitter_tags_empty(self):
        """Test: Twitter tags vacíos cuando no existen"""
        html = "<html><head></head><body></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        twitter = extract_twitter_tags(soup)
        
        assert len(twitter) == 0


class TestEdgeCases:
    """Tests para casos límite"""
    
    def test_malformed_html(self):
        """Test: HTML malformado no causa errores"""
        html = "<html><body><h1>Unclosed tag<p>Content"
        soup = BeautifulSoup(html, 'html.parser')
        
        # No debería lanzar excepciones
        title = extract_title(soup)
        links = extract_links(soup, "https://test.com")
        count = count_images(soup)
        
        assert title is not None
        assert isinstance(links, list)
        assert isinstance(count, int)
    
    def test_empty_html(self):
        """Test: HTML vacío"""
        html = ""
        soup = BeautifulSoup(html, 'html.parser')
        
        title = extract_title(soup)
        links = extract_links(soup, "https://test.com")
        structure = analyze_structure(soup)
        
        assert title == "Sin título"
        assert len(links) == 0
        assert all(count == 0 for count in structure.values())
    
    def test_links_without_href(self):
        """Test: Enlaces sin atributo href"""
        html = '<html><body><a>No href</a><a href="">Empty</a></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        links = extract_links(soup, "https://test.com")
        
        # Enlaces sin href o vacíos deben ser ignorados
        assert len(links) == 0
    
    def test_images_without_src(self):
        """Test: Imágenes sin atributo src"""
        html = '<html><body><img alt="No src"><img src=""></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        images = extract_image_urls(soup, "https://test.com")
        
        # Imágenes sin src o vacías deben ser ignoradas
        assert len(images) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
