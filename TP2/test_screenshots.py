#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de screenshots.
Verifica que Selenium pueda capturar páginas correctamente.
"""

import sys
import os
import asyncio
from common.protocol import send_to_processor


async def test_screenshot_simple():
    """
    Test 1: Screenshot simple de example.com
    """
    print("=" * 70)
    print("Test 1: Screenshot simple (example.com)")
    print("=" * 70)
    
    task = {
        'task_type': 'screenshot',
        'url': 'https://example.com',
        'width': 1280,
        'height': 720,
        'full_page': True,
        'timeout': 30
    }
    
    try:
        print(f"Enviando tarea de screenshot al procesador...")
        response = await send_to_processor('127.0.0.1', 9000, task, timeout=60)
        
        if response:
            status = response.get('status')
            print(f"✓ Status: {status}")
            
            if status == 'success':
                screenshot = response.get('screenshot')
                if screenshot:
                    size_kb = len(screenshot) / 1024
                    print(f"✓ Screenshot capturado: {size_kb:.2f} KB (base64)")
                    print(f"✓ Formato: {response.get('format')}")
                    print(f"✓ Encoding: {response.get('encoding')}")
                    print(f"✓ Dimensiones: {response.get('dimensions')}")
                    print(f"✓ Full page: {response.get('full_page')}")
                    
                    # Guardar screenshot para inspección manual
                    import base64
                    screenshot_bytes = base64.b64decode(screenshot)
                    test_file = '/tmp/test_screenshot_example.png'
                    with open(test_file, 'wb') as f:
                        f.write(screenshot_bytes)
                    print(f"✓ Screenshot guardado en: {test_file}")
                    
                    print("\n✅ Test 1 PASADO\n")
                    return True
                else:
                    print("✗ No se recibió imagen en la respuesta")
                    return False
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


async def test_screenshot_viewport():
    """
    Test 2: Screenshot solo viewport (sin full page)
    """
    print("=" * 70)
    print("Test 2: Screenshot viewport (github.com)")
    print("=" * 70)
    
    task = {
        'task_type': 'screenshot',
        'url': 'https://github.com',
        'width': 1920,
        'height': 1080,
        'full_page': False,  # Solo viewport
        'timeout': 30
    }
    
    try:
        print(f"Enviando tarea de screenshot (viewport only)...")
        response = await send_to_processor('127.0.0.1', 9000, task, timeout=60)
        
        if response and response.get('status') == 'success':
            screenshot = response.get('screenshot')
            if screenshot:
                size_kb = len(screenshot) / 1024
                print(f"✓ Screenshot viewport capturado: {size_kb:.2f} KB")
                print(f"✓ Full page: {response.get('full_page')}")
                
                # Guardar
                import base64
                screenshot_bytes = base64.b64decode(screenshot)
                test_file = '/tmp/test_screenshot_github_viewport.png'
                with open(test_file, 'wb') as f:
                    f.write(screenshot_bytes)
                print(f"✓ Guardado en: {test_file}")
                
                print("\n✅ Test 2 PASADO\n")
                return True
        
        print("✗ Test fallido")
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_screenshot_custom_size():
    """
    Test 3: Screenshot con tamaño personalizado
    """
    print("=" * 70)
    print("Test 3: Screenshot tamaño personalizado (mobile)")
    print("=" * 70)
    
    task = {
        'task_type': 'screenshot',
        'url': 'https://www.python.org',
        'width': 375,  # iPhone size
        'height': 667,
        'full_page': True,
        'timeout': 30
    }
    
    try:
        print(f"Enviando tarea de screenshot (mobile 375x667)...")
        response = await send_to_processor('127.0.0.1', 9000, task, timeout=60)
        
        if response and response.get('status') == 'success':
            screenshot = response.get('screenshot')
            if screenshot:
                size_kb = len(screenshot) / 1024
                dims = response.get('dimensions', {})
                print(f"✓ Screenshot capturado: {size_kb:.2f} KB")
                print(f"✓ Dimensiones: {dims.get('width')}x{dims.get('height')}")
                
                # Guardar
                import base64
                screenshot_bytes = base64.b64decode(screenshot)
                test_file = '/tmp/test_screenshot_mobile.png'
                with open(test_file, 'wb') as f:
                    f.write(screenshot_bytes)
                print(f"✓ Guardado en: {test_file}")
                
                print("\n✅ Test 3 PASADO\n")
                return True
        
        print("✗ Test fallido")
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def main():
    """
    Ejecuta todos los tests de screenshots.
    """
    print("\n" + "=" * 70)
    print("TEST DE FUNCIONALIDAD: Screenshots con Selenium")
    print("=" * 70 + "\n")
    
    print("NOTA: Estos tests requieren:")
    print("  1. Servidor de procesamiento corriendo (127.0.0.1:9000)")
    print("  2. Chrome/Chromium instalado")
    print("  3. Conexión a internet\n")
    
    # Test 1
    test1_passed = await test_screenshot_simple()
    
    # Test 2
    test2_passed = await test_screenshot_viewport()
    
    # Test 3
    test3_passed = await test_screenshot_custom_size()
    
    # Resumen
    print("=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    print(f"Test 1 (Simple): {'✅ PASADO' if test1_passed else '❌ FALLADO'}")
    print(f"Test 2 (Viewport): {'✅ PASADO' if test2_passed else '❌ FALLADO'}")
    print(f"Test 3 (Custom size): {'✅ PASADO' if test3_passed else '❌ FALLADO'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print("\n🎉 TODOS LOS TESTS PASARON")
        print("✅ La funcionalidad de screenshots está operativa")
        print(f"\nScreenshots guardados en /tmp/test_screenshot_*.png")
        sys.exit(0)
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

