#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de análisis de performance.
Verifica que Selenium pueda obtener métricas de rendimiento correctamente.
"""

import sys
import asyncio
from common.protocol import send_to_processor
import json


async def test_performance_simple():
    """
    Test 1: Análisis de performance simple (example.com)
    """
    print("=" * 70)
    print("Test 1: Análisis de performance simple (example.com)")
    print("=" * 70)
    
    task = {
        'task_type': 'performance',
        'url': 'https://example.com',
        'timeout': 30
    }
    
    try:
        print(f"Enviando tarea de performance al procesador...")
        response = await send_to_processor('127.0.0.1', 9000, task, timeout=60)
        
        if response:
            status = response.get('status')
            print(f"✓ Status: {status}")
            
            if status == 'success':
                metrics = response.get('metrics', {})
                insights = response.get('insights', {})
                
                # Métricas básicas
                print(f"\n📊 Métricas Básicas:")
                print(f"  - Tiempo de carga: {metrics.get('load_time_ms')}ms")
                print(f"  - URL: {metrics.get('url')}")
                
                # Recursos
                resources = metrics.get('resources', {})
                print(f"\n📦 Recursos:")
                print(f"  - Total requests: {resources.get('total_requests')}")
                print(f"  - Tamaño total: {resources.get('total_size_kb')} KB ({resources.get('total_size_mb')} MB)")
                
                # Recursos por tipo
                print(f"\n📑 Por tipo:")
                by_type = resources.get('by_type', {})
                for res_type, stats in by_type.items():
                    print(f"  - {res_type}: {stats['count']} recursos, {stats['total_size']/1024:.2f} KB")
                
                # Timing metrics
                timing = metrics.get('timing_metrics', {})
                if timing:
                    print(f"\n⏱️  Timing Metrics:")
                    if 'dns_lookup_ms' in timing:
                        print(f"  - DNS Lookup: {timing['dns_lookup_ms']}ms")
                    if 'tcp_connection_ms' in timing:
                        print(f"  - TCP Connection: {timing['tcp_connection_ms']}ms")
                    if 'request_response_ms' in timing:
                        print(f"  - Request/Response: {timing['request_response_ms']}ms")
                    if 'dom_interactive_ms' in timing:
                        print(f"  - DOM Interactive: {timing['dom_interactive_ms']}ms")
                
                # Paint metrics
                paint = metrics.get('paint_metrics', {})
                if paint:
                    print(f"\n🎨 Paint Metrics:")
                    for metric, value in paint.items():
                        print(f"  - {metric}: {value:.2f}ms")
                
                # Insights
                print(f"\n💡 Insights:")
                print(f"  - Score: {insights.get('score')}")
                issues = insights.get('issues', [])
                if issues:
                    print(f"  - Issues: {len(issues)}")
                    for issue in issues:
                        print(f"    • {issue}")
                else:
                    print(f"  - No issues found!")
                
                recommendations = insights.get('recommendations', [])
                if recommendations:
                    print(f"  - Recommendations:")
                    for rec in recommendations:
                        print(f"    • {rec}")
                
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


async def test_performance_complex():
    """
    Test 2: Análisis de performance de página compleja (github.com)
    """
    print("=" * 70)
    print("Test 2: Análisis de performance compleja (github.com)")
    print("=" * 70)
    
    task = {
        'task_type': 'performance',
        'url': 'https://github.com',
        'timeout': 30
    }
    
    try:
        print(f"Enviando tarea de performance (puede tardar)...")
        response = await send_to_processor('127.0.0.1', 9000, task, timeout=60)
        
        if response and response.get('status') == 'success':
            metrics = response.get('metrics', {})
            resources = metrics.get('resources', {})
            insights = response.get('insights', {})
            
            print(f"✓ Tiempo de carga: {metrics.get('load_time_ms')}ms")
            print(f"✓ Total requests: {resources.get('total_requests')}")
            print(f"✓ Tamaño total: {resources.get('total_size_mb')} MB")
            print(f"✓ Performance score: {insights.get('score')}")
            
            # Top 5 recursos más grandes
            largest = resources.get('largest_resources', [])
            if largest:
                print(f"\n📊 Top 5 recursos más grandes:")
                for i, res in enumerate(largest, 1):
                    name = res['name'].split('/')[-1][:40]  # Último segmento de URL
                    print(f"  {i}. {name} ({res['type']}): {res['size_kb']} KB")
            
            print("\n✅ Test 2 PASADO\n")
            return True
        
        print("✗ Test fallido")
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_performance_comparison():
    """
    Test 3: Comparación de performance entre dos sitios
    """
    print("=" * 70)
    print("Test 3: Comparación de performance (example.com vs python.org)")
    print("=" * 70)
    
    sites = [
        ('https://example.com', 'Example.com'),
        ('https://www.python.org', 'Python.org')
    ]
    
    results = []
    
    for url, name in sites:
        print(f"\nAnalizando {name}...")
        task = {
            'task_type': 'performance',
            'url': url,
            'timeout': 30
        }
        
        try:
            response = await send_to_processor('127.0.0.1', 9000, task, timeout=60)
            
            if response and response.get('status') == 'success':
                metrics = response.get('metrics', {})
                resources = metrics.get('resources', {})
                results.append({
                    'name': name,
                    'load_time': metrics.get('load_time_ms'),
                    'requests': resources.get('total_requests'),
                    'size_mb': resources.get('total_size_mb'),
                    'score': response.get('insights', {}).get('score')
                })
                print(f"✓ {name}: {metrics.get('load_time_ms')}ms")
            else:
                print(f"✗ Error analizando {name}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    # Mostrar comparación
    print(f"\n📊 Comparación de Performance:")
    print(f"{'Sitio':<20} {'Load Time':<15} {'Requests':<12} {'Size':<12} {'Score'}")
    print("-" * 70)
    
    for r in results:
        print(f"{r['name']:<20} {r['load_time']:<15.2f}ms {r['requests']:<12} {r['size_mb']:<12.2f}MB {r['score']}")
    
    # Determinar ganador
    fastest = min(results, key=lambda x: x['load_time'])
    print(f"\n🏆 Sitio más rápido: {fastest['name']} ({fastest['load_time']:.2f}ms)")
    
    print("\n✅ Test 3 PASADO\n")
    return True


async def main():
    """
    Ejecuta todos los tests de performance.
    """
    print("\n" + "=" * 70)
    print("TEST DE FUNCIONALIDAD: Análisis de Performance Web")
    print("=" * 70 + "\n")
    
    print("NOTA: Estos tests requieren:")
    print("  1. Servidor de procesamiento corriendo (127.0.0.1:9000)")
    print("  2. Chrome/Chromium instalado")
    print("  3. Conexión a internet")
    print("  4. Pueden tardar 30-60s cada uno\n")
    
    # Test 1
    test1_passed = await test_performance_simple()
    
    # Test 2
    test2_passed = await test_performance_complex()
    
    # Test 3
    test3_passed = await test_performance_comparison()
    
    # Resumen
    print("=" * 70)
    print("RESUMEN DE TESTS")
    print("=" * 70)
    print(f"Test 1 (Simple): {'✅ PASADO' if test1_passed else '❌ FALLADO'}")
    print(f"Test 2 (Complejo): {'✅ PASADO' if test2_passed else '❌ FALLADO'}")
    print(f"Test 3 (Comparación): {'✅ PASADO' if test3_passed else '❌ FALLADO'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print("\n🎉 TODOS LOS TESTS PASARON")
        print("✅ La funcionalidad de análisis de performance está operativa")
        sys.exit(0)
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())

