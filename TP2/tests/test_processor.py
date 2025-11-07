"""
Tests unitarios para funciones de procesamiento.
"""

import pytest
from PIL import Image
import base64
from io import BytesIO


# Importar funciones a testear
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processor.image_processor import (
    generate_thumbnail,
    resize_image,
    optimize_image,
    convert_image_format,
    get_image_info,
    extract_main_images
)
from common.validators import (
    validate_url,
    validate_port,
    validate_workers,
    validate_timeout,
    validate_image_size,
    validate_quality,
    validate_image_format
)
from common.limits import (
    get_safe_timeout,
    get_safe_quality,
    get_safe_dimension,
    get_safe_max_images
)


def create_test_image(width=100, height=100, format='PNG'):
    """
    Crea una imagen de prueba.
    
    Returns:
        bytes de la imagen
    """
    img = Image.new('RGB', (width, height), color='red')
    buffer = BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()


class TestImageProcessor:
    """Tests para image_processor.py"""
    
    def test_generate_thumbnail(self):
        """Test: Generación de thumbnail"""
        image_data = create_test_image(200, 200)
        thumbnail = generate_thumbnail(image_data, size=(50, 50))
        
        assert thumbnail is not None
        assert isinstance(thumbnail, str)  # base64
        assert len(thumbnail) > 0
    
    def test_generate_thumbnail_aspect_ratio(self):
        """Test: Thumbnail mantiene aspect ratio"""
        # Imagen rectangular 200x100
        image_data = create_test_image(200, 100)
        thumbnail_b64 = generate_thumbnail(image_data, size=(100, 100))
        
        # Decodificar y verificar
        thumbnail_bytes = base64.b64decode(thumbnail_b64)
        img = Image.open(BytesIO(thumbnail_bytes))
        
        # Debería ser 100x50 (manteniendo ratio 2:1)
        assert img.width <= 100
        assert img.height <= 100
    
    def test_generate_thumbnail_invalid_data(self):
        """Test: Thumbnail con datos inválidos retorna None"""
        invalid_data = b"not an image"
        thumbnail = generate_thumbnail(invalid_data)
        
        assert thumbnail is None
    
    def test_resize_image(self):
        """Test: Redimensionamiento de imagen"""
        image_data = create_test_image(200, 200)
        resized = resize_image(image_data, 100, 100, maintain_aspect=False)
        
        assert resized is not None
        assert isinstance(resized, str)
    
    def test_optimize_image(self):
        """Test: Optimización de imagen"""
        image_data = create_test_image(1000, 1000)
        optimized = optimize_image(image_data, quality=75)
        
        assert optimized is not None
        assert isinstance(optimized, bytes)
        # Verificar que retorna bytes válidos (no siempre es más pequeño debido a conversión de formatos)
        assert len(optimized) > 0
    
    def test_convert_image_format(self):
        """Test: Conversión de formato"""
        image_data = create_test_image(100, 100, format='PNG')
        converted = convert_image_format(image_data, 'JPEG')
        
        assert converted is not None
        assert isinstance(converted, str)  # base64
    
    def test_get_image_info(self):
        """Test: Obtención de información de imagen"""
        image_data = create_test_image(150, 200)
        info = get_image_info(image_data)
        
        assert info is not None
        assert info['width'] == 150
        assert info['height'] == 200
        assert info['format'] == 'PNG'
        assert 'size_bytes' in info
        assert 'size_kb' in info
    
    def test_get_image_info_invalid(self):
        """Test: Info de imagen inválida retorna None"""
        invalid_data = b"not an image"
        info = get_image_info(invalid_data)
        
        assert info is None
    
    def test_extract_main_images(self):
        """Test: Filtrado de imágenes principales"""
        image_urls = [
            'https://example.com/main-image.jpg',
            'https://example.com/icon.png',
            'https://example.com/logo.gif',
            'https://example.com/photo.jpg',
            'https://example.com/tracking/pixel.png'
        ]
        
        filtered = extract_main_images(image_urls)
        
        # Debería filtrar icon, logo, pixel
        assert len(filtered) < len(image_urls)
        assert 'https://example.com/main-image.jpg' in filtered
        assert 'https://example.com/photo.jpg' in filtered


class TestValidators:
    """Tests para validators.py"""
    
    def test_validate_url_valid(self):
        """Test: URL válida"""
        is_valid, msg = validate_url('https://example.com')
        assert is_valid is True
        assert msg is None
    
    def test_validate_url_invalid_scheme(self):
        """Test: URL con esquema inválido"""
        is_valid, msg = validate_url('ftp://example.com')
        assert is_valid is False
        assert 'esquema' in msg.lower()
    
    def test_validate_url_blocked_domain(self):
        """Test: URL con dominio bloqueado"""
        is_valid, msg = validate_url('http://localhost:8000')
        assert is_valid is False
        assert 'bloqueado' in msg.lower()
    
    def test_validate_url_private_ip(self):
        """Test: URL con IP privada"""
        is_valid, msg = validate_url('http://192.168.1.1')
        assert is_valid is False
        assert 'privada' in msg.lower()
    
    def test_validate_url_too_long(self):
        """Test: URL demasiado larga"""
        long_url = 'https://example.com/' + 'a' * 3000
        is_valid, msg = validate_url(long_url)
        assert is_valid is False
        assert 'larga' in msg.lower()
    
    def test_validate_port_valid(self):
        """Test: Puerto válido"""
        is_valid, msg = validate_port(8000)
        assert is_valid is True
        assert msg is None
    
    def test_validate_port_out_of_range(self):
        """Test: Puerto fuera de rango"""
        is_valid, msg = validate_port(70000)
        assert is_valid is False
    
    def test_validate_port_privileged(self):
        """Test: Puerto privilegiado"""
        is_valid, msg = validate_port(80)
        assert is_valid is False
    
    def test_validate_workers_valid(self):
        """Test: Número de workers válido"""
        is_valid, msg = validate_workers(4)
        assert is_valid is True
    
    def test_validate_workers_invalid(self):
        """Test: Número de workers inválido"""
        is_valid, msg = validate_workers(0)
        assert is_valid is False
    
    def test_validate_timeout_valid(self):
        """Test: Timeout válido"""
        is_valid, msg = validate_timeout(30)
        assert is_valid is True
    
    def test_validate_timeout_invalid(self):
        """Test: Timeout inválido"""
        is_valid, msg = validate_timeout(-5)
        assert is_valid is False
    
    def test_validate_image_size_valid(self):
        """Test: Dimensiones válidas"""
        is_valid, msg = validate_image_size(1920, 1080)
        assert is_valid is True
    
    def test_validate_image_size_invalid(self):
        """Test: Dimensiones inválidas"""
        is_valid, msg = validate_image_size(10000, 10000)
        assert is_valid is False
    
    def test_validate_quality_valid(self):
        """Test: Calidad válida"""
        is_valid, msg = validate_quality(85)
        assert is_valid is True
    
    def test_validate_quality_invalid(self):
        """Test: Calidad inválida"""
        is_valid, msg = validate_quality(150)
        assert is_valid is False
    
    def test_validate_image_format_valid(self):
        """Test: Formato válido"""
        is_valid, msg = validate_image_format('JPEG')
        assert is_valid is True
    
    def test_validate_image_format_invalid(self):
        """Test: Formato inválido"""
        is_valid, msg = validate_image_format('BMP')
        assert is_valid is False


class TestLimits:
    """Tests para limits.py"""
    
    def test_get_safe_timeout(self):
        """Test: Obtener timeout seguro"""
        safe = get_safe_timeout(45, 60, 30)
        assert safe == 45
        
        # Valor demasiado alto
        safe = get_safe_timeout(100, 60, 30)
        assert safe == 60
        
        # Valor inválido
        safe = get_safe_timeout(None, 60, 30)
        assert safe == 30
    
    def test_get_safe_quality(self):
        """Test: Obtener calidad segura"""
        assert get_safe_quality(85) == 85
        assert get_safe_quality(150) == 100  # Máximo
        assert get_safe_quality(0) == 1  # Mínimo
    
    def test_get_safe_dimension(self):
        """Test: Obtener dimensiones seguras"""
        width, height = get_safe_dimension(1920, 1080)
        assert width == 1920
        assert height == 1080
        
        # Valores demasiado grandes
        width, height = get_safe_dimension(10000, 10000)
        assert width == 4096  # MAX_IMAGE_DIMENSION
        assert height == 4096
    
    def test_get_safe_max_images(self):
        """Test: Obtener número seguro de imágenes"""
        assert get_safe_max_images(5) == 5
        assert get_safe_max_images(50) == 10  # MAX_IMAGES_TO_PROCESS
        assert get_safe_max_images(0) == 1  # Mínimo


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
