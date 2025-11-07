#!/usr/bin/env python3
"""
Servidor de Procesamiento Distribuido (Parte B)
Utiliza multiprocessing para ejecutar tareas CPU-bound en paralelo.
"""

import argparse
import logging
import multiprocessing
import signal
import socketserver
import sys
from ipaddress import ip_address, AddressValueError

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
        description='Servidor de Procesamiento Distribuido',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--ip',
        type=validate_ip_address,
        required=True,
        metavar='IP',
        help='Dirección de escucha'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=validate_port,
        required=True,
        metavar='PORT',
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-n', '--processes',
        type=int,
        default=multiprocessing.cpu_count(),
        metavar='PROCESSES',
        help=f'Número de procesos en el pool (default: {multiprocessing.cpu_count()})'
    )
    
    return parser.parse_args()


class ProcessingRequestHandler(socketserver.BaseRequestHandler):
    """
    Handler para procesar requests del servidor de scraping.
    Cada request se procesa en un worker del pool de procesos.
    """
    
    def handle(self):
        """
        Maneja una conexión entrante.
        Recibe una tarea, la procesa y envía la respuesta.
        """
        try:
            logger.info(f"Conexión recibida de {self.client_address[0]}:{self.client_address[1]}")
            
            # Importar protocolo
            import sys
            sys.path.insert(0, '/Users/agus/Documents/Facultad/Computacion_II/TP2/TP2')
            from common.protocol import receive_message_sync, send_message_sync
            
            # Recibir mensaje del cliente
            task = receive_message_sync(self.request)
            
            if task is None:
                logger.error("No se pudo recibir la tarea del cliente")
                return
            
            logger.info(f"Tarea recibida: {task.get('task_type', 'unknown')}")
            
            # Procesar la tarea
            response = self.process_task(task)
            
            # Enviar respuesta
            if not send_message_sync(self.request, response):
                logger.error("No se pudo enviar la respuesta al cliente")
                return
            
            logger.info(f"Respuesta enviada exitosamente")
            
        except Exception as e:
            logger.error(f"Error manejando request: {e}", exc_info=True)
            # Intentar enviar respuesta de error
            try:
                error_response = {
                    'status': 'error',
                    'message': str(e)
                }
                send_message_sync(self.request, error_response)
            except:
                pass
    
    def process_task(self, task: dict) -> dict:
        """
        Procesa una tarea según su tipo.
        
        Args:
            task: Diccionario con la tarea a procesar
            
        Returns:
            Diccionario con el resultado
        """
        task_type = task.get('task_type', 'unknown')
        
        try:
            if task_type == 'test':
                # Tarea de prueba
                return {
                    'status': 'success',
                    'task_type': 'test',
                    'message': 'Test task processed successfully',
                    'echo': task.get('data', {})
                }
            
            elif task_type == 'screenshot':
                # Generar screenshot real
                url = task.get('url')
                if not url:
                    return {
                        'status': 'error',
                        'task_type': 'screenshot',
                        'message': 'URL is required for screenshot task'
                    }
                
                logger.info(f"Screenshot request para: {url}")
                
                # Importar módulo de screenshots
                from processor.screenshot import generate_screenshot_with_options
                
                # Obtener parámetros opcionales
                width = task.get('width', 1920)
                height = task.get('height', 1080)
                full_page = task.get('full_page', True)
                timeout = task.get('timeout', 30)
                
                # Generar screenshot
                screenshot_b64 = generate_screenshot_with_options(
                    url, 
                    width=width,
                    height=height,
                    full_page=full_page,
                    timeout=timeout
                )
                
                if screenshot_b64:
                    return {
                        'status': 'success',
                        'task_type': 'screenshot',
                        'message': f'Screenshot captured successfully',
                        'screenshot': screenshot_b64,
                        'format': 'png',
                        'encoding': 'base64',
                        'dimensions': {
                            'width': width,
                            'height': height
                        },
                        'full_page': full_page
                    }
                else:
                    return {
                        'status': 'error',
                        'task_type': 'screenshot',
                        'message': 'Failed to capture screenshot'
                    }
            
            elif task_type == 'performance':
                # Análisis de rendimiento real
                url = task.get('url')
                if not url:
                    return {
                        'status': 'error',
                        'task_type': 'performance',
                        'message': 'URL is required for performance task'
                    }
                
                logger.info(f"Performance analysis request para: {url}")
                
                # Importar módulo de performance
                from processor.performance import analyze_performance, get_performance_insights
                
                # Obtener timeout opcional
                timeout = task.get('timeout', 30)
                
                # Analizar performance
                metrics = analyze_performance(url, timeout=timeout)
                
                if metrics:
                    # Generar insights
                    insights = get_performance_insights(metrics)
                    
                    return {
                        'status': 'success',
                        'task_type': 'performance',
                        'message': 'Performance analysis completed successfully',
                        'metrics': metrics,
                        'insights': insights
                    }
                else:
                    return {
                        'status': 'error',
                        'task_type': 'performance',
                        'message': 'Failed to analyze performance'
                    }
            
            elif task_type == 'thumbnails':
                # Placeholder para thumbnails (se implementará en Etapa 8)
                logger.info(f"Thumbnail generation request para: {len(task.get('image_urls', []))} imágenes")
                return {
                    'status': 'success',
                    'task_type': 'thumbnails',
                    'message': 'Thumbnail generation not yet implemented',
                    'thumbnails': []
                }
            
            else:
                logger.warning(f"Tipo de tarea desconocido: {task_type}")
                return {
                    'status': 'error',
                    'task_type': task_type,
                    'message': f'Unknown task type: {task_type}'
                }
                
        except Exception as e:
            logger.error(f"Error procesando tarea {task_type}: {e}", exc_info=True)
            return {
                'status': 'error',
                'task_type': task_type,
                'message': f'Error processing task: {str(e)}'
            }


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Servidor TCP que maneja múltiples conexiones en threads separados.
    """
    allow_reuse_address = True
    daemon_threads = True


def initialize_process_pool(num_processes: int):
    """
    Inicializa el pool de procesos para tareas CPU-bound.
    
    Args:
        num_processes: Número de procesos en el pool
        
    Returns:
        ProcessPoolExecutor configurado
    """
    from concurrent.futures import ProcessPoolExecutor
    
    pool = ProcessPoolExecutor(max_workers=num_processes)
    logger.info(f"Pool de procesos inicializado con {num_processes} workers")
    
    return pool


def shutdown_handler(signum, frame):
    """
    Maneja las señales de shutdown (SIGINT, SIGTERM).
    
    Args:
        signum: Número de señal
        frame: Frame actual
    """
    logger.info("Señal de shutdown recibida, deteniendo servidor...")
    sys.exit(0)


def start_server(host: str, port: int, num_processes: int):
    """
    Inicia el servidor de procesamiento.
    
    Args:
        host: Dirección IP de escucha
        port: Puerto de escucha
        num_processes: Número de procesos en el pool
    """
    # Configurar handlers de señales
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    # Inicializar pool de procesos
    process_pool = initialize_process_pool(num_processes)
    
    try:
        # Crear y configurar servidor
        server = ThreadedTCPServer((host, port), ProcessingRequestHandler)
        
        # Guardar pool en el servidor para acceso desde handlers
        server.process_pool = process_pool
        
        logger.info(f"Servidor de procesamiento iniciado en {host}:{port}")
        logger.info(f"Pool de procesos: {num_processes} workers")
        logger.info("Esperando conexiones...")
        
        # Iniciar servidor
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en el servidor: {e}", exc_info=True)
    finally:
        logger.info("Cerrando pool de procesos...")
        process_pool.shutdown(wait=True)
        logger.info("Servidor detenido")


def main():
    """
    Función principal del servidor.
    """
    args = parse_arguments()
    
    try:
        start_server(
            host=args.ip,
            port=args.port,
            num_processes=args.processes
        )
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

