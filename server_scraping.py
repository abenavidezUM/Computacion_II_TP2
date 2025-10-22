#!/usr/bin/env python3
"""
Servidor de Scraping Web Asíncrono (Parte A)
Utiliza asyncio para manejar múltiples clientes de forma concurrente.
"""

import argparse
import asyncio
import logging
import sys
from ipaddress import ip_address, AddressValueError
from aiohttp import web

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_ip_address(ip_string: str) -> str:
    """
    Valida que la dirección IP sea válida (IPv4 o IPv6).
    
    Args:
        ip_string: String con la dirección IP a validar
        
    Returns:
        String con la IP validada
        
    Raises:
        argparse.ArgumentTypeError: Si la IP no es válida
    """
    try:
        ip_address(ip_string)
        return ip_string
    except AddressValueError:
        raise argparse.ArgumentTypeError(f"'{ip_string}' no es una dirección IP válida")


def validate_port(port_string: str) -> int:
    """
    Valida que el puerto sea un número válido (1-65535).
    
    Args:
        port_string: String con el puerto a validar
        
    Returns:
        Puerto como entero
        
    Raises:
        argparse.ArgumentTypeError: Si el puerto no es válido
    """
    try:
        port = int(port_string)
        if 1 <= port <= 65535:
            return port
        raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(f"El puerto debe estar entre 1 y 65535")


def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.
    
    Returns:
        Namespace con los argumentos parseados
    """
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Web Asíncrono',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--ip',
        type=validate_ip_address,
        required=True,
        metavar='IP',
        help='Dirección de escucha (soporta IPv4/IPv6)'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=validate_port,
        required=True,
        metavar='PORT',
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=4,
        metavar='WORKERS',
        help='Número de workers (default: 4)'
    )
    
    parser.add_argument(
        '--processor-host',
        type=str,
        default='127.0.0.1',
        metavar='HOST',
        help='Host del servidor de procesamiento (default: 127.0.0.1)'
    )
    
    parser.add_argument(
        '--processor-port',
        type=validate_port,
        default=9000,
        metavar='PORT',
        help='Puerto del servidor de procesamiento (default: 9000)'
    )
    
    return parser.parse_args()


async def handle_scrape(request: web.Request) -> web.Response:
    """
    Handler para el endpoint /scrape.
    Recibe una URL y retorna información de scraping.
    
    Args:
        request: Request de aiohttp
        
    Returns:
        Response JSON con los datos scrapeados
    """
    try:
        # Obtener URL de los parámetros
        url = request.query.get('url')
        
        if not url:
            return web.json_response(
                {'status': 'error', 'message': 'URL parameter is required'},
                status=400
            )
        
        # Por ahora, respuesta básica (se implementará en Etapa 3)
        response_data = {
            'url': url,
            'status': 'success',
            'message': 'Scraping endpoint ready (functionality to be implemented)'
        }
        
        logger.info(f"Received scraping request for URL: {url}")
        return web.json_response(response_data)
        
    except Exception as e:
        logger.error(f"Error handling scrape request: {e}", exc_info=True)
        return web.json_response(
            {'status': 'error', 'message': 'Internal server error'},
            status=500
        )


async def handle_health(request: web.Request) -> web.Response:
    """
    Handler para el endpoint /health.
    Verifica que el servidor esté funcionando.
    
    Args:
        request: Request de aiohttp
        
    Returns:
        Response JSON con el estado del servidor
    """
    return web.json_response({
        'status': 'healthy',
        'service': 'scraping-server'
    })


def create_app() -> web.Application:
    """
    Crea y configura la aplicación aiohttp.
    
    Returns:
        Aplicación aiohttp configurada
    """
    app = web.Application()
    
    # Configurar rutas
    app.router.add_get('/scrape', handle_scrape)
    app.router.add_post('/scrape', handle_scrape)
    app.router.add_get('/health', handle_health)
    
    return app


async def start_server(host: str, port: int, workers: int,
                      processor_host: str, processor_port: int):
    """
    Inicia el servidor de scraping.
    
    Args:
        host: Dirección IP de escucha
        port: Puerto de escucha
        workers: Número de workers concurrentes
        processor_host: Host del servidor de procesamiento
        processor_port: Puerto del servidor de procesamiento
    """
    app = create_app()
    
    # Guardar configuración en app para acceso global
    app['config'] = {
        'workers': workers,
        'processor_host': processor_host,
        'processor_port': processor_port
    }
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Determinar si es IPv6
    is_ipv6 = ':' in host
    site = web.TCPSite(runner, host, port)
    
    await site.start()
    
    protocol = 'IPv6' if is_ipv6 else 'IPv4'
    logger.info(f"Servidor de scraping iniciado en {protocol} {host}:{port}")
    logger.info(f"Workers configurados: {workers}")
    logger.info(f"Servidor de procesamiento: {processor_host}:{processor_port}")
    logger.info("Endpoints disponibles:")
    logger.info(f"  - GET/POST /scrape?url=<URL>")
    logger.info(f"  - GET /health")
    
    # Mantener el servidor corriendo
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Deteniendo servidor...")
    finally:
        await runner.cleanup()


def main():
    """
    Función principal del servidor.
    """
    args = parse_arguments()
    
    try:
        asyncio.run(start_server(
            host=args.ip,
            port=args.port,
            workers=args.workers,
            processor_host=args.processor_host,
            processor_port=args.processor_port
        ))
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

