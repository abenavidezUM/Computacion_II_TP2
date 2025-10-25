#!/usr/bin/env python3
"""
Script de prueba end-to-end para la integración completa A↔B.
Verifica que el servidor de scraping pueda comunicarse con el servidor de procesamiento.
"""

import asyncio
import sys
import aiohttp
import json


async def test_scraping_without_processing():
    """
    Test 1: Scraping sin procesamiento (comportamiento original).
    """
    print("=" * 70)
    print("Test 1: Scraping sin procesamiento adicional")
    print("=" * 70)
    
    url = "https://example.com"
    scraping_server = "http://127.0.0.1:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{scraping_server}/scrape",
                params={'url': url}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Status: {data.get('status')}")
                    print(f"✓ URL: {data.get('url')}")
                    print(f"✓ Título: {data.get('scraping_data', {}).get('title')}")
                    print(f"✓ Enlaces encontrados: {data.get('scraping_data', {}).get('links_count')}")
                    print(f"✓ Imágenes: {data.get('scraping_data', {}).get('images_count')}")
                    
                    # Verificar que NO haya datos de procesamiento
                    if 'processing_data' not in data:
                        print("✓ Sin datos de procesamiento (como se esperaba)")
                    else:
                        print("✗ ERROR: Se encontraron datos de procesamiento inesperados")
                        return False
                    
                    print("\n✅ Test 1 PASADO\n")
                    return True
                else:
                    print(f"✗ Error HTTP: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_scraping_with_processing():
    """
    Test 2: Scraping con procesamiento integrado.
    """
    print("=" * 70)
    print("Test 2: Scraping con procesamiento integrado (process=true)")
    print("=" * 70)
    
    url = "https://example.com"
    scraping_server = "http://127.0.0.1:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{scraping_server}/scrape",
                params={'url': url, 'process': 'true'}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Status: {data.get('status')}")
                    print(f"✓ URL: {data.get('url')}")
                    
                    # Verificar datos de scraping
                    scraping_data = data.get('scraping_data', {})
                    print(f"✓ Título: {scraping_data.get('title')}")
                    print(f"✓ Enlaces encontrados: {scraping_data.get('links_count')}")
                    
                    # Verificar datos de procesamiento
                    processing_data = data.get('processing_data', {})
                    
                    if not processing_data:
                        print("✗ ERROR: No se encontraron datos de procesamiento")
                        return False
                    
                    print(f"\n📦 Datos de Procesamiento:")
                    
                    # Screenshot
                    screenshot = processing_data.get('screenshot', {})
                    print(f"  - Screenshot: {screenshot.get('status')}")
                    print(f"    Message: {screenshot.get('message')}")
                    
                    # Performance
                    performance = processing_data.get('performance', {})
                    print(f"  - Performance: {performance.get('status')}")
                    print(f"    Message: {performance.get('message')}")
                    
                    print("\n✅ Test 2 PASADO\n")
                    return True
                else:
                    print(f"✗ Error HTTP: {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return False
                    
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_complex_page_with_processing():
    """
    Test 3: Página compleja con procesamiento.
    """
    print("=" * 70)
    print("Test 3: Página compleja (GitHub) con procesamiento")
    print("=" * 70)
    
    url = "https://github.com"
    scraping_server = "http://127.0.0.1:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{scraping_server}/scrape",
                params={'url': url, 'process': 'true'},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    scraping_data = data.get('scraping_data', {})
                    processing_data = data.get('processing_data', {})
                    
                    print(f"✓ Título: {scraping_data.get('title')[:50]}...")
                    print(f"✓ Enlaces: {scraping_data.get('links_count')}")
                    print(f"✓ Imágenes: {scraping_data.get('images_count')}")
                    print(f"✓ Estructura: {scraping_data.get('structure')}")
                    print(f"\n✓ Screenshot Status: {processing_data.get('screenshot', {}).get('status')}")
                    print(f"✓ Performance Status: {processing_data.get('performance', {}).get('status')}")
                    
                    print("\n✅ Test 3 PASADO\n")
                    return True
                else:
                    print(f"✗ Error HTTP: {response.status}")
                    return False
                    
    except asyncio.TimeoutError:
        print("✗ Timeout - La página tardó demasiado")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_health_check():
    """
    Test 0: Verificar que ambos servidores estén corriendo.
    """
    print("=" * 70)
    print("Test 0: Verificación de servidores")
    print("=" * 70)
    
    scraping_server = "http://127.0.0.1:8000"
    
    try:
        # Verificar servidor de scraping
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{scraping_server}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ Servidor de Scraping: {data.get('status')}")
                    print(f"  - Workers: {data.get('workers')}")
                    print(f"  - Procesador: {data.get('processor', {}).get('host')}:{data.get('processor', {}).get('port')}")
                else:
                    print(f"✗ Servidor de scraping no responde correctamente")
                    return False
        
        print("\n✅ Servidores verificados\n")
        return True
        
    except aiohttp.ClientConnectorError:
        print("✗ ERROR: No se puede conectar al servidor de scraping (127.0.0.1:8000)")
        print("   Asegúrate de que esté corriendo:")
        print("   $ python server_scraping.py -i 127.0.0.1 -p 8000 -w 4")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def main():
    """
    Ejecuta todos los tests.
    """
    print("\n" + "=" * 70)
    print("TEST DE INTEGRACIÓN END-TO-END: Servidor A ↔ Servidor B")
    print("=" * 70 + "\n")
    
    # Test 0: Health check
    if not await test_health_check():
        print("\n❌ Los servidores no están disponibles")
        print("\nPara ejecutar estos tests, asegúrate de que ambos servidores estén corriendo:")
        print("  Terminal 1: python server_scraping.py -i 127.0.0.1 -p 8000 -w 4")
        print("  Terminal 2: python server_processing.py -i 127.0.0.1 -p 9000 -n 4")
        sys.exit(1)
    
    # Test 1: Sin procesamiento
    test1_passed = await test_scraping_without_processing()
    
    # Test 2: Con procesamiento
    test2_passed = await test_scraping_with_processing()
    
    # Test 3: Página compleja
    test3_passed = await test_complex_page_with_processing()
    
    # Resumen
    print("=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    print(f"Test 1 (Scraping básico): {'✅ PASADO' if test1_passed else '❌ FALLADO'}")
    print(f"Test 2 (Con procesamiento): {'✅ PASADO' if test2_passed else '❌ FALLADO'}")
    print(f"Test 3 (Página compleja): {'✅ PASADO' if test3_passed else '❌ FALLADO'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print("\n🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("✅ La integración A↔B está funcionando correctamente")
        sys.exit(0)
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

