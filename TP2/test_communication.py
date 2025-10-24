#!/usr/bin/env python3
"""
Script de prueba para verificar la comunicación entre servidores.
"""

import asyncio
import sys
from common.protocol import send_to_processor


async def test_processor_communication():
    """
    Prueba la comunicación con el servidor de procesamiento.
    """
    print("=== Test de Comunicación con Servidor de Procesamiento ===\n")
    
    # Configuración
    host = '127.0.0.1'
    port = 9000
    
    # Test 1: Tarea de prueba simple
    print("Test 1: Tarea de prueba simple")
    task = {
        'task_type': 'test',
        'data': {
            'message': 'Hello from scraping server!',
            'test_number': 42
        }
    }
    
    print(f"Enviando tarea al procesador {host}:{port}...")
    response = await send_to_processor(host, port, task, timeout=10)
    
    if response:
        print(f"✓ Respuesta recibida:")
        print(f"  Status: {response.get('status')}")
        print(f"  Message: {response.get('message')}")
        print(f"  Echo: {response.get('echo')}")
    else:
        print("✗ No se recibió respuesta")
        return False
    
    print()
    
    # Test 2: Tarea de screenshot (placeholder)
    print("Test 2: Tarea de screenshot (placeholder)")
    task = {
        'task_type': 'screenshot',
        'url': 'https://example.com'
    }
    
    print(f"Enviando tarea de screenshot...")
    response = await send_to_processor(host, port, task, timeout=10)
    
    if response:
        print(f"✓ Respuesta recibida:")
        print(f"  Status: {response.get('status')}")
        print(f"  Message: {response.get('message')}")
    else:
        print("✗ No se recibió respuesta")
        return False
    
    print()
    
    # Test 3: Tarea de performance (placeholder)
    print("Test 3: Tarea de performance (placeholder)")
    task = {
        'task_type': 'performance',
        'url': 'https://github.com'
    }
    
    print(f"Enviando tarea de performance...")
    response = await send_to_processor(host, port, task, timeout=10)
    
    if response:
        print(f"✓ Respuesta recibida:")
        print(f"  Status: {response.get('status')}")
        print(f"  Message: {response.get('message')}")
    else:
        print("✗ No se recibió respuesta")
        return False
    
    print()
    print("=== Todos los tests pasaron exitosamente ===")
    return True


async def main():
    """
    Función principal.
    """
    try:
        success = await test_processor_communication()
        sys.exit(0 if success else 1)
    except ConnectionRefusedError:
        print("\n✗ Error: No se pudo conectar al servidor de procesamiento")
        print("Asegúrate de que esté corriendo en 127.0.0.1:9000")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

