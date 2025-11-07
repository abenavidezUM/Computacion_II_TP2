#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de procesamiento de imágenes.
Verifica thumbnails, redimensionamiento, optimización y conversión de formatos.
"""

import sys
import asyncio
from common.protocol import send_to_processor
import base64


async def test_thumbnails_basic():
    """
    Test 1: Generación básica de thumbnails
    """
    print("=" * 70)
    print("Test 1: Generación básica de thumbnails")
    print("=" * 70)
    
    # URLs de imágenes de ejemplo (públicas y accesibles)
    image_urls = [
        'https://via.placeholder.com/800x600.jpg',
        'https://via.placeholder.com/600x800.png',
        'https://via.placeholder.com/500x500.jpg'
    ]
    
    task = {
        'task_type': 'thumbnails',
        'image_urls': image_urls,
        'max_images': 3,
        'thumbnail_size': [150, 150],
        'format': 'JPEG',
        'quality': 85
    }
    
    try:
        print(f"Enviando tarea de thumbnails para {len(image_urls)} imágenes...")
        response = await send_to_processor('127.0.0.1', 9000, task, timeout=60)
        
        if response:
            status = response.get('status')
            print(f"✓ Status: {status}")
            
            if status == 'success':
                thumbnails = response.get('thumbnails', [])
                total_processed = response.get('total_processed', 0)
                total_requested = response.get('total_requested', 0)
                
                print(f"\n📊 Resultados:")
                print(f"  - Total solicitado: {total_requested}")
                print(f"  - Total procesado: {total_processed}")
                print(f"  - Thumbnails generados: {len(thumbnails)}")
                
                for i, thumb in enumerate(thumbnails, 1):
                    url = thumb.get('url', '')
                    thumbnail_b64 = thumb.get('thumbnail', '')
                    format_out = thumb.get('format', '')
                    size = thumb.get('thumbnail_size', [])
                    original_info = thumb.get('original_info', {})
                    
                    print(f"\n  Thumbnail {i}:")
                    print(f"    - URL: {url[:60]}...")
                    print(f"    - Tamaño thumbnail: {len(thumbnail_b64)/1024:.2f} KB (base64)")
                    print(f"    - Formato: {format_out}")
                    print(f"    - Dimensiones thumbnail: {size}")
                    print(f"    - Original: {original_info.get('width')}x{original_info.get('height')} ({original_info.get('size_kb')} KB)")
                
                # Guardar primer thumbnail para inspección
                if thumbnails:
                    first_thumb = thumbnails[0]['thumbnail']
                    thumb_bytes = base64.b64decode(first_thumb)
                    test_file = '/tmp/test_thumbnail.jpg'
                    with open(test_file, 'wb') as f:
                        f.write(thumb_bytes)
                    print(f"\n✓ Primer thumbnail guardado en: {test_file}")
                
                print("\n✅ Test 1 PASADO\n")
                return True
            else:
                print(f"✗ Error: {response.get('message')}")
                return False
        else:
            print("✗ No se recibió respuesta del servidor")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_thumbnails_different_sizes():
    """
    Test 2: Thumbnails con diferentes tamaños
    """
    print("=" * 70)
    print("Test 2: Thumbnails con diferentes tamaños")
    print("=" * 70)
    
    image_urls = [
        'https://via.placeholder.com/1920x1080.jpg'
    ]
    
    sizes = [
        ([100, 100], 'pequeño'),
        ([300, 300], 'mediano'),
        ([500, 500], 'grande')
    ]
    
    results = []
    
    for size, name in sizes:
        print(f"\nGenerando thumbnail {name} ({size[0]}x{size[1]})...")
        
        task = {
            'task_type': 'thumbnails',
            'image_urls': image_urls,
            'max_images': 1,
            'thumbnail_size': size,
            'format': 'JPEG',
            'quality': 85
        }
        
        try:
            response = await send_to_processor('127.0.0.1', 9000, task, timeout=60)
            
            if response and response.get('status') == 'success':
                thumbnails = response.get('thumbnails', [])
                if thumbnails:
                    thumb_size_kb = len(thumbnails[0]['thumbnail']) / 1024
                    print(f"✓ Thumbnail {name}: {thumb_size_kb:.2f} KB")
                    results.append((name, thumb_size_kb))
            else:
                print(f"✗ Error generando thumbnail {name}")
                return False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    print(f"\n📊 Comparación de tamaños:")
    for name, size_kb in results:
        print(f"  - {name:10s}: {size_kb:6.2f} KB")
    
    print("\n✅ Test 2 PASADO\n")
    return True


async def test_thumbnails_different_formats():
    """
    Test 3: Thumbnails en diferentes formatos
    """
    print("=" * 70)
    print("Test 3: Thumbnails en diferentes formatos")
    print("=" * 70)
    
    image_urls = [
        'https://via.placeholder.com/800x600.jpg'
    ]
    
    formats = ['JPEG', 'PNG', 'WEBP']
    results = []
    
    for format_out in formats:
        print(f"\nGenerando thumbnail en formato {format_out}...")
        
        task = {
            'task_type': 'thumbnails',
            'image_urls': image_urls,
            'max_images': 1,
            'thumbnail_size': [200, 200],
            'format': format_out,
            'quality': 85
        }
        
        try:
            response = await send_to_processor('127.0.0.1', 9000, task, timeout=60)
            
            if response and response.get('status') == 'success':
                thumbnails = response.get('thumbnails', [])
                if thumbnails:
                    thumb_size_kb = len(thumbnails[0]['thumbnail']) / 1024
                    print(f"✓ Formato {format_out}: {thumb_size_kb:.2f} KB")
                    results.append((format_out, thumb_size_kb))
                    
                    # Guardar para verificación
                    extension = format_out.lower()
                    if extension == 'jpeg':
                        extension = 'jpg'
                    thumb_bytes = base64.b64decode(thumbnails[0]['thumbnail'])
                    with open(f'/tmp/test_thumbnail.{extension}', 'wb') as f:
                        f.write(thumb_bytes)
            else:
                print(f"✗ Error con formato {format_out}")
                return False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    print(f"\n📊 Comparación de formatos:")
    for format_name, size_kb in results:
        print(f"  - {format_name:6s}: {size_kb:6.2f} KB")
    
    print(f"\n✓ Thumbnails guardados en /tmp/test_thumbnail.[jpg|png|webp]")
    print("\n✅ Test 3 PASADO\n")
    return True


async def main():
    """
    Ejecuta todos los tests de procesamiento de imágenes.
    """
    print("\n" + "=" * 70)
    print("TEST DE FUNCIONALIDAD: Procesamiento de Imágenes")
    print("=" * 70 + "\n")
    
    print("NOTA: Estos tests requieren:")
    print("  1. Servidor de procesamiento corriendo (127.0.0.1:9000)")
    print("  2. Pillow (PIL) instalado")
    print("  3. Conexión a internet para descargar imágenes de prueba")
    print("  4. Pueden tardar 30-60s\n")
    
    # Test 1
    test1_passed = await test_thumbnails_basic()
    
    # Test 2
    test2_passed = await test_thumbnails_different_sizes()
    
    # Test 3
    test3_passed = await test_thumbnails_different_formats()
    
    # Resumen
    print("=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    print(f"Test 1 (Básico): {'✅ PASADO' if test1_passed else '❌ FALLADO'}")
    print(f"Test 2 (Tamaños): {'✅ PASADO' if test2_passed else '❌ FALLADO'}")
    print(f"Test 3 (Formatos): {'✅ PASADO' if test3_passed else '❌ FALLADO'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print("\n🎉 TODOS LOS TESTS PASARON")
        print("✅ La funcionalidad de procesamiento de imágenes está operativa")
        print(f"\nThumbnails guardados en /tmp/test_thumbnail.*")
        sys.exit(0)
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

