#!/usr/bin/env python3
"""
Script de prueba para el sistema de tareas asíncronas (Bonus Track - Etapa 11).
"""

import asyncio
import aiohttp
import time


async def test_async_scraping():
    """
    Prueba el sistema de tareas asíncronas.
    """
    server_url = "http://127.0.0.1:8000"
    
    print("=" * 70)
    print("TEST: Sistema de Tareas Asíncronas (Bonus Track - Etapa 11)")
    print("=" * 70)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Crear tarea asíncrona
        print("\n1. Creando tarea asíncrona...")
        test_url = "https://example.com"
        
        async with session.post(
            f"{server_url}/scrape/async",
            params={'url': test_url}
        ) as response:
            if response.status == 202:
                data = await response.json()
                task_id = data['task_id']
                print(f"   ✓ Tarea creada: {task_id}")
                print(f"   URL: {test_url}")
                print(f"   Status: {data['status']}")
                print(f"   Endpoints:")
                print(f"     - Status: {data['endpoints']['status']}")
                print(f"     - Result: {data['endpoints']['result']}")
            else:
                print(f"   ✗ Error: {response.status}")
                return
        
        # Test 2: Consultar estado inmediatamente (debería estar pending o processing)
        print(f"\n2. Consultando estado inicial...")
        await asyncio.sleep(0.5)  # Esperar un poco
        
        async with session.get(f"{server_url}/status/{task_id}") as response:
            if response.status == 200:
                data = await response.json()
                status_info = data['task']
                print(f"   ✓ Estado: {status_info['status']}")
                print(f"   Creado: {status_info['created_at']}")
                if status_info.get('started_at'):
                    print(f"   Iniciado: {status_info['started_at']}")
            else:
                print(f"   ✗ Error: {response.status}")
        
        # Test 3: Intentar obtener resultado (debería estar processing)
        print(f"\n3. Intentando obtener resultado (procesando)...")
        
        async with session.get(f"{server_url}/result/{task_id}") as response:
            if response.status == 202:
                data = await response.json()
                print(f"   ✓ Estado: {data['status']} - {data['message']}")
            else:
                print(f"   ✗ Status: {response.status}")
        
        # Test 4: Esperar a que complete y obtener resultado
        print(f"\n4. Esperando a que complete...")
        max_attempts = 20
        attempt = 0
        completed = False
        
        while attempt < max_attempts and not completed:
            await asyncio.sleep(2)
            attempt += 1
            
            async with session.get(f"{server_url}/status/{task_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data['task']['status']
                    print(f"   Intento {attempt}/{max_attempts}: {status}")
                    
                    if status == 'completed':
                        completed = True
                        break
                    elif status == 'failed':
                        print(f"   ✗ Tarea falló: {data['task'].get('error')}")
                        return
        
        if not completed:
            print(f"   ✗ Timeout esperando resultado")
            return
        
        # Test 5: Obtener resultado final
        print(f"\n5. Obteniendo resultado final...")
        
        async with session.get(f"{server_url}/result/{task_id}") as response:
            if response.status == 200:
                data = await response.json()
                print(f"   ✓ Resultado obtenido exitosamente")
                print(f"   URL: {data['url']}")
                print(f"   Timestamp: {data['timestamp']}")
                
                scraping_data = data.get('scraping_data', {})
                print(f"\n   Datos de scraping:")
                print(f"     - Título: {scraping_data.get('title', 'N/A')}")
                print(f"     - Enlaces: {scraping_data.get('links_count', 0)}")
                print(f"     - Imágenes: {scraping_data.get('images_count', 0)}")
            else:
                print(f"   ✗ Error obteniendo resultado: {response.status}")
        
        # Test 6: Obtener estadísticas del servidor
        print(f"\n6. Consultando estadísticas del servidor...")
        
        async with session.get(f"{server_url}/stats") as response:
            if response.status == 200:
                data = await response.json()
                stats = data['stats']
                print(f"   ✓ Estadísticas:")
                print(f"     - Total tareas: {stats['total_tasks']}")
                print(f"     - Pendientes: {stats['pending']}")
                print(f"     - Procesando: {stats['processing']}")
                print(f"     - Completadas: {stats['completed']}")
                print(f"     - Fallidas: {stats['failed']}")
                print(f"     - Capacidad máxima: {stats['max_tasks']}")
            else:
                print(f"   ✗ Error obteniendo estadísticas: {response.status}")
        
        # Test 7: Crear múltiples tareas
        print(f"\n7. Creando múltiples tareas simultáneas...")
        test_urls = [
            "https://example.com",
            "https://www.iana.org",
            "https://httpbin.org/html"
        ]
        
        task_ids = []
        for url in test_urls:
            async with session.post(
                f"{server_url}/scrape/async",
                params={'url': url}
            ) as response:
                if response.status == 202:
                    data = await response.json()
                    task_ids.append(data['task_id'])
                    print(f"   ✓ Tarea creada para {url}")
        
        print(f"\n   {len(task_ids)} tareas creadas en paralelo")
        
        # Test 8: Verificar estadísticas actualizadas
        print(f"\n8. Estadísticas actualizadas...")
        await asyncio.sleep(1)
        
        async with session.get(f"{server_url}/stats") as response:
            if response.status == 200:
                data = await response.json()
                stats = data['stats']
                print(f"   ✓ Total tareas: {stats['total_tasks']}")
                print(f"   ✓ Pendientes: {stats['pending']}")
                print(f"   ✓ Procesando: {stats['processing']}")
        
        # Test 9: Probar tarea inválida (task_id inexistente)
        print(f"\n9. Probando tarea inexistente...")
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        
        async with session.get(f"{server_url}/status/{fake_task_id}") as response:
            if response.status == 404:
                print(f"   ✓ Error 404 correctamente retornado para tarea inexistente")
            else:
                print(f"   ✗ Status inesperado: {response.status}")
    
    print("\n" + "=" * 70)
    print("TESTS COMPLETADOS")
    print("=" * 70)


if __name__ == '__main__':
    try:
        asyncio.run(test_async_scraping())
    except KeyboardInterrupt:
        print("\nTest interrumpido por el usuario")
    except Exception as e:
        print(f"\nError en el test: {e}")
        import traceback
        traceback.print_exc()

