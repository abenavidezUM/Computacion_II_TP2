#!/usr/bin/env python3
"""
Cliente de prueba para el sistema de scraping distribuido.
Permite realizar requests al servidor de scraping y mostrar resultados.
"""

import argparse
import asyncio
import json
import sys
import aiohttp
from typing import Optional


def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.
    
    Returns:
        Namespace con los argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description='Cliente para el sistema de scraping web',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='URL del sitio web a scrapear'
    )
    
    parser.add_argument(
        '--server-host',
        type=str,
        default='127.0.0.1',
        help='Host del servidor de scraping (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--server-port',
        type=int,
        default=8000,
        help='Puerto del servidor de scraping (default: 8000)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=60,
        help='Timeout en segundos (default: 60)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Archivo de salida para guardar el resultado JSON'
    )
    
    parser.add_argument(
        '--process',
        action='store_true',
        help='Solicitar procesamiento adicional (screenshots, performance, thumbnails)'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Mostrar output formateado y legible'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    return parser.parse_args()


async def scrape_url(url: str, server_host: str, server_port: int,
                     timeout: int, process: bool = False, verbose: bool = False) -> Optional[dict]:
    """
    Realiza un request de scraping al servidor.
    
    Args:
        url: URL a scrapear
        server_host: Host del servidor
        server_port: Puerto del servidor
        timeout: Timeout en segundos
        process: Si True, solicita procesamiento adicional
        verbose: Si True, muestra información detallada
        
    Returns:
        Diccionario con la respuesta del servidor o None si hay error
    """
    server_url = f"http://{server_host}:{server_port}/scrape"
    
    try:
        async with aiohttp.ClientSession() as session:
            params = {'url': url}
            if process:
                params['process'] = 'true'
            
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            
            if verbose:
                print(f"📡 Enviando request a {server_url}")
                print(f"🌐 URL objetivo: {url}")
                if process:
                    print(f"⚙️  Procesamiento adicional: ACTIVADO")
                print("⏳ Esperando respuesta...\n")
            
            async with session.get(server_url, params=params,
                                  timeout=timeout_config) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    print(f"❌ Error del servidor (status {response.status}): {error_text}")
                    return None
                    
    except aiohttp.ClientConnectorError:
        print(f"Error: No se pudo conectar al servidor en {server_host}:{server_port}")
        print("Verifica que el servidor esté ejecutándose")
        return None
    except asyncio.TimeoutError:
        print(f"Error: Timeout después de {timeout} segundos")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None


def print_results(data: dict, pretty: bool = False):
    """
    Imprime los resultados de forma formateada.
    
    Args:
        data: Diccionario con los datos de respuesta
        pretty: Si True, muestra formato legible en lugar de JSON
    """
    if not pretty:
        print("=" * 70)
        print("RESULTADOS DEL SCRAPING")
        print("=" * 70)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("=" * 70)
        return
    
    # Formato legible
    print("\n" + "=" * 70)
    print("📊 RESULTADOS DEL SCRAPING")
    print("=" * 70)
    
    # Estado
    status = data.get('status', 'unknown')
    print(f"\n✅ Estado: {status.upper()}")
    
    # Datos de scraping
    scraping_data = data.get('scraping_data', {})
    if scraping_data:
        print(f"\n🔍 DATOS DE SCRAPING:")
        print(f"  📄 Título: {scraping_data.get('title', 'N/A')}")
        print(f"  🔗 Enlaces: {scraping_data.get('links_count', 0)}")
        print(f"  🖼️  Imágenes: {scraping_data.get('images_count', 0)}")
        
        structure = scraping_data.get('structure', {})
        if structure:
            print(f"  📑 Estructura:")
            for tag, count in sorted(structure.items()):
                if count > 0:
                    print(f"     {tag}: {count}")
    
    # Datos de procesamiento
    processing_data = data.get('processing_data', {})
    if processing_data:
        print(f"\n⚙️  DATOS DE PROCESAMIENTO:")
        
        screenshot = processing_data.get('screenshot', {})
        if screenshot and screenshot.get('status') == 'success':
            print(f"  📸 Screenshot: Capturado")
        
        performance = processing_data.get('performance', {})
        if performance and performance.get('status') == 'success':
            metrics = performance.get('metrics', {})
            print(f"  ⚡ Performance:")
            print(f"     Tiempo de carga: {metrics.get('load_time_ms', 0)}ms")
            resources = metrics.get('resources', {})
            print(f"     Requests: {resources.get('total_requests', 0)}")
            print(f"     Tamaño: {resources.get('total_size_kb', 0)} KB")
        
        thumbnails = processing_data.get('thumbnails', [])
        if thumbnails:
            print(f"  🖼️  Thumbnails: {len(thumbnails)} generados")
    
    print("\n" + "=" * 70 + "\n")


def save_results(data: dict, output_file: str):
    """
    Guarda los resultados en un archivo JSON.
    
    Args:
        data: Diccionario con los datos
        output_file: Ruta del archivo de salida
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nResultados guardados en: {output_file}")
    except Exception as e:
        print(f"Error guardando resultados: {e}")


async def main():
    """
    Función principal del cliente.
    """
    args = parse_arguments()
    
    # Realizar scraping
    results = await scrape_url(
        url=args.url,
        server_host=args.server_host,
        server_port=args.server_port,
        timeout=args.timeout,
        process=args.process,
        verbose=args.verbose
    )
    
    if results:
        # Mostrar resultados
        print_results(results, pretty=args.pretty)
        
        # Guardar si se especificó archivo de salida
        if args.output:
            save_results(results, args.output)
        
        return 0
    else:
        print("\nNo se pudieron obtener resultados")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

