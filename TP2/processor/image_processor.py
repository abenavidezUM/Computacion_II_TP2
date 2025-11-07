"""
Procesamiento de imágenes.
Descarga imágenes, genera thumbnails, redimensiona y optimiza.
"""

from PIL import Image
import requests
import base64
import logging
from typing import List, Optional, Tuple, Dict
from io import BytesIO

logger = logging.getLogger(__name__)

# Configuración por defecto
DEFAULT_THUMBNAIL_SIZE = (150, 150)
DEFAULT_QUALITY = 85
MAX_IMAGE_SIZE_MB = 10
DOWNLOAD_TIMEOUT = 30


def download_image(url: str, timeout: int = DOWNLOAD_TIMEOUT) -> Optional[bytes]:
    """
    Descarga una imagen desde una URL de forma síncrona.
    
    Args:
        url: URL de la imagen
        timeout: Timeout en segundos
        
    Returns:
        Bytes de la imagen o None si hay error
    """
    try:
        logger.debug(f"Descargando imagen: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, timeout=timeout, headers=headers, stream=True)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            
            # Verificar que es una imagen
            if not content_type.startswith('image/'):
                logger.warning(f"URL no es una imagen: {url} (tipo: {content_type})")
                return None
            
            # Verificar tamaño
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > MAX_IMAGE_SIZE_MB:
                    logger.warning(f"Imagen demasiado grande: {size_mb:.2f}MB > {MAX_IMAGE_SIZE_MB}MB")
                    return None
            
            image_data = response.content
            logger.debug(f"Imagen descargada: {len(image_data)} bytes")
            return image_data
        else:
            logger.warning(f"Error descargando imagen {url}: HTTP {response.status_code}")
            return None
                
    except requests.Timeout:
        logger.warning(f"Timeout descargando imagen: {url}")
        return None
    except requests.RequestException as e:
        logger.warning(f"Error de red descargando {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado descargando {url}: {e}")
        return None


def generate_thumbnail(image_data: bytes, size: Tuple[int, int] = DEFAULT_THUMBNAIL_SIZE,
                       format: str = 'JPEG', quality: int = DEFAULT_QUALITY) -> Optional[str]:
    """
    Genera un thumbnail de una imagen.
    
    Args:
        image_data: Bytes de la imagen original
        size: Tupla (width, height) para el thumbnail
        format: Formato de salida (JPEG, PNG, WEBP)
        quality: Calidad de compresión (1-100, solo para JPEG/WEBP)
        
    Returns:
        String con el thumbnail codificado en base64 o None si hay error
    """
    try:
        # Abrir imagen
        img = Image.open(BytesIO(image_data))
        
        # Convertir a RGB si es necesario (para JPEG)
        if format.upper() == 'JPEG' and img.mode in ('RGBA', 'P', 'LA'):
            # Crear fondo blanco para transparencias
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert('RGB')
        
        # Generar thumbnail manteniendo aspect ratio
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Guardar en buffer
        buffer = BytesIO()
        save_kwargs = {'format': format.upper()}
        
        if format.upper() in ('JPEG', 'WEBP'):
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        elif format.upper() == 'PNG':
            save_kwargs['optimize'] = True
        
        img.save(buffer, **save_kwargs)
        
        # Convertir a base64
        thumbnail_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        logger.info(f"Thumbnail generado: {img.size} -> {len(thumbnail_b64)/1024:.2f}KB (base64)")
        return thumbnail_b64
        
    except Exception as e:
        logger.error(f"Error generando thumbnail: {e}", exc_info=True)
        return None


def resize_image(image_data: bytes, width: int, height: int,
                 maintain_aspect: bool = True, format: str = 'JPEG',
                 quality: int = DEFAULT_QUALITY) -> Optional[str]:
    """
    Redimensiona una imagen.
    
    Args:
        image_data: Bytes de la imagen original
        width: Ancho objetivo
        height: Alto objetivo
        maintain_aspect: Si True, mantiene aspect ratio (puede ser menor al objetivo)
        format: Formato de salida
        quality: Calidad de compresión
        
    Returns:
        Imagen redimensionada en base64 o None si hay error
    """
    try:
        img = Image.open(BytesIO(image_data))
        
        # Convertir a RGB si es necesario
        if format.upper() == 'JPEG' and img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert('RGB')
        
        # Redimensionar
        if maintain_aspect:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Guardar
        buffer = BytesIO()
        save_kwargs = {'format': format.upper()}
        
        if format.upper() in ('JPEG', 'WEBP'):
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        elif format.upper() == 'PNG':
            save_kwargs['optimize'] = True
        
        img.save(buffer, **save_kwargs)
        
        resized_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        logger.info(f"Imagen redimensionada: {img.size}, {len(resized_b64)/1024:.2f}KB")
        return resized_b64
        
    except Exception as e:
        logger.error(f"Error redimensionando imagen: {e}")
        return None


def optimize_image(image_data: bytes, quality: int = DEFAULT_QUALITY,
                   max_width: int = 1920, max_height: int = 1080,
                   format: str = 'JPEG') -> Optional[bytes]:
    """
    Optimiza una imagen reduciendo su tamaño y calidad.
    
    Args:
        image_data: Bytes de la imagen original
        quality: Calidad de compresión (1-100)
        max_width: Ancho máximo
        max_height: Alto máximo
        format: Formato de salida
        
    Returns:
        Bytes de la imagen optimizada o None si hay error
    """
    try:
        img = Image.open(BytesIO(image_data))
        
        # Redimensionar si es muy grande
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            logger.debug(f"Imagen redimensionada a: {img.size}")
        
        # Convertir a RGB si es necesario
        if format.upper() == 'JPEG' and img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert('RGB')
        
        # Comprimir
        buffer = BytesIO()
        save_kwargs = {
            'format': format.upper(),
            'optimize': True
        }
        
        if format.upper() in ('JPEG', 'WEBP'):
            save_kwargs['quality'] = quality
        
        img.save(buffer, **save_kwargs)
        
        optimized = buffer.getvalue()
        original_size = len(image_data) / 1024
        optimized_size = len(optimized) / 1024
        reduction = ((original_size - optimized_size) / original_size) * 100
        
        logger.info(f"Imagen optimizada: {original_size:.2f}KB -> {optimized_size:.2f}KB ({reduction:.1f}% reducción)")
        return optimized
        
    except Exception as e:
        logger.error(f"Error optimizando imagen: {e}")
        return None


def convert_image_format(image_data: bytes, target_format: str,
                         quality: int = DEFAULT_QUALITY) -> Optional[str]:
    """
    Convierte una imagen a otro formato.
    
    Args:
        image_data: Bytes de la imagen original
        target_format: Formato objetivo (JPEG, PNG, WEBP, GIF)
        quality: Calidad para formatos con pérdida
        
    Returns:
        Imagen convertida en base64 o None si hay error
    """
    try:
        img = Image.open(BytesIO(image_data))
        
        target_format = target_format.upper()
        
        # Convertir a RGB si es necesario
        if target_format == 'JPEG' and img.mode in ('RGBA', 'P', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert('RGB')
        
        # Guardar en nuevo formato
        buffer = BytesIO()
        save_kwargs = {'format': target_format}
        
        if target_format in ('JPEG', 'WEBP'):
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        elif target_format == 'PNG':
            save_kwargs['optimize'] = True
        
        img.save(buffer, **save_kwargs)
        
        converted_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        logger.info(f"Formato convertido a {target_format}: {len(converted_b64)/1024:.2f}KB")
        return converted_b64
        
    except Exception as e:
        logger.error(f"Error convirtiendo formato: {e}")
        return None


def get_image_info(image_data: bytes) -> Optional[Dict]:
    """
    Obtiene información de una imagen.
    
    Args:
        image_data: Bytes de la imagen
        
    Returns:
        Diccionario con información (width, height, format, mode, size) o None
    """
    try:
        img = Image.open(BytesIO(image_data))
        
        info = {
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'mode': img.mode,
            'size_bytes': len(image_data),
            'size_kb': round(len(image_data) / 1024, 2),
            'size_mb': round(len(image_data) / (1024 * 1024), 2)
        }
        
        return info
        
    except Exception as e:
        logger.error(f"Error obteniendo info de imagen: {e}")
        return None


def process_page_images(image_urls: List[str], max_images: int = 5,
                        thumbnail_size: Tuple[int, int] = DEFAULT_THUMBNAIL_SIZE,
                        format: str = 'JPEG', quality: int = DEFAULT_QUALITY) -> List[Dict]:
    """
    Procesa múltiples imágenes de una página de forma síncrona.
    
    Args:
        image_urls: Lista de URLs de imágenes
        max_images: Número máximo de imágenes a procesar
        thumbnail_size: Tamaño de los thumbnails
        format: Formato de salida
        quality: Calidad de compresión
        
    Returns:
        Lista de diccionarios con thumbnails y metadatos
    """
    results = []
    processed = 0
    
    for url in image_urls:
        if processed >= max_images:
            break
        
        logger.info(f"Procesando imagen {processed + 1}/{max_images}: {url}")
        
        # Descargar imagen
        image_data = download_image(url)
        
        if image_data is None:
            logger.warning(f"No se pudo descargar: {url}")
            continue
        
        # Obtener info
        info = get_image_info(image_data)
        
        if info is None:
            logger.warning(f"No se pudo obtener info: {url}")
            continue
        
        # Generar thumbnail
        thumbnail = generate_thumbnail(image_data, thumbnail_size, format, quality)
        
        if thumbnail is None:
            logger.warning(f"No se pudo generar thumbnail: {url}")
            continue
        
        # Agregar resultado
        results.append({
            'url': url,
            'thumbnail': thumbnail,
            'format': format,
            'thumbnail_size': thumbnail_size,
            'original_info': info
        })
        
        processed += 1
    
    logger.info(f"Procesadas {processed} imágenes de {len(image_urls)}")
    return results


def extract_main_images(image_urls: List[str], min_width: int = 200,
                        min_height: int = 200) -> List[str]:
    """
    Filtra y extrae las imágenes principales de una página.
    Excluye iconos, logos pequeños, etc.
    
    Args:
        image_urls: Lista de todas las URLs de imágenes
        min_width: Ancho mínimo en pixels
        min_height: Alto mínimo en pixels
        
    Returns:
        Lista de URLs de imágenes principales
    """
    # Filtros básicos por URL
    filtered = []
    
    exclude_keywords = [
        'icon', 'logo', 'avatar', 'badge', 'button',
        'banner', 'ad', 'pixel', 'tracking', '1x1'
    ]
    
    for url in image_urls:
        url_lower = url.lower()
        
        # Excluir por keywords
        if any(keyword in url_lower for keyword in exclude_keywords):
            continue
        
        # Excluir formatos no soportados
        if url_lower.endswith('.svg') or url_lower.endswith('.ico'):
            continue
        
        filtered.append(url)
    
    logger.info(f"Filtradas {len(filtered)} de {len(image_urls)} imágenes")
    return filtered
