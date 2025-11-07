"""
Análisis de rendimiento de páginas web.
Mide tiempos de carga, tamaño de recursos, número de requests usando Selenium y Performance API.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
import json
import logging
import time
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


def _get_chrome_options_for_performance() -> Options:
    """
    Configura opciones de Chrome para análisis de performance.
    
    Returns:
        Opciones de Chrome configuradas
    """
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    # Habilitar logging de performance
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    return options


def analyze_performance(url: str, timeout: int = 30) -> Optional[Dict]:
    """
    Analiza el rendimiento de carga de una página.
    
    Args:
        url: URL de la página a analizar
        timeout: Timeout en segundos
        
    Returns:
        Diccionario con métricas de rendimiento completas
    """
    driver = None
    
    try:
        logger.info(f"Iniciando análisis de performance para {url}")
        
        # Configurar driver
        options = _get_chrome_options_for_performance()
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(timeout)
        
        # Marcar tiempo de inicio
        start_time = time.time()
        
        # Cargar página
        driver.get(url)
        
        # Esperar a que cargue completamente
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        # Tiempo de carga total
        load_time = (time.time() - start_time) * 1000  # en ms
        
        # Obtener métricas de Navigation Timing API
        navigation_timing = driver.execute_script("""
            var timing = window.performance.timing;
            var navigation = window.performance.navigation;
            return {
                navigationStart: timing.navigationStart,
                domainLookupStart: timing.domainLookupStart,
                domainLookupEnd: timing.domainLookupEnd,
                connectStart: timing.connectStart,
                connectEnd: timing.connectEnd,
                requestStart: timing.requestStart,
                responseStart: timing.responseStart,
                responseEnd: timing.responseEnd,
                domLoading: timing.domLoading,
                domInteractive: timing.domInteractive,
                domContentLoadedEventStart: timing.domContentLoadedEventStart,
                domContentLoadedEventEnd: timing.domContentLoadedEventEnd,
                domComplete: timing.domComplete,
                loadEventStart: timing.loadEventStart,
                loadEventEnd: timing.loadEventEnd,
                navigationType: navigation.type,
                redirectCount: navigation.redirectCount
            };
        """)
        
        # Calcular métricas derivadas
        metrics = _calculate_timing_metrics(navigation_timing)
        
        # Obtener información de recursos
        resources = driver.execute_script("""
            var resources = window.performance.getEntriesByType('resource');
            return resources.map(function(r) {
                return {
                    name: r.name,
                    type: r.initiatorType,
                    size: r.transferSize || 0,
                    duration: r.duration,
                    startTime: r.startTime
                };
            });
        """)
        
        # Analizar recursos
        resource_analysis = _analyze_resources(resources)
        
        # Obtener métricas de paint
        paint_metrics = driver.execute_script("""
            var paints = window.performance.getEntriesByType('paint');
            var result = {};
            paints.forEach(function(p) {
                result[p.name] = p.startTime;
            });
            return result;
        """)
        
        # Construir resultado
        result = {
            'url': url,
            'load_time_ms': round(load_time, 2),
            'timing_metrics': metrics,
            'resources': resource_analysis,
            'paint_metrics': paint_metrics,
            'navigation': {
                'type': _get_navigation_type(navigation_timing.get('navigationType', 0)),
                'redirect_count': navigation_timing.get('redirectCount', 0)
            }
        }
        
        logger.info(f"Análisis completado: {load_time:.2f}ms, {resource_analysis['total_requests']} requests")
        
        return result
        
    except TimeoutException:
        logger.error(f"Timeout analizando performance de {url}")
        return None
    except WebDriverException as e:
        logger.error(f"Error de WebDriver analizando {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado analizando performance: {e}", exc_info=True)
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def _calculate_timing_metrics(timing: Dict) -> Dict:
    """
    Calcula métricas de timing a partir de Navigation Timing API.
    
    Args:
        timing: Datos de navigation timing
        
    Returns:
        Diccionario con métricas calculadas
    """
    nav_start = timing.get('navigationStart', 0)
    
    if nav_start == 0:
        return {}
    
    metrics = {}
    
    # DNS lookup time
    if timing.get('domainLookupEnd') and timing.get('domainLookupStart'):
        metrics['dns_lookup_ms'] = timing['domainLookupEnd'] - timing['domainLookupStart']
    
    # TCP connection time
    if timing.get('connectEnd') and timing.get('connectStart'):
        metrics['tcp_connection_ms'] = timing['connectEnd'] - timing['connectStart']
    
    # Request/Response time
    if timing.get('responseStart') and timing.get('requestStart'):
        metrics['request_response_ms'] = timing['responseStart'] - timing['requestStart']
    
    # Response download time
    if timing.get('responseEnd') and timing.get('responseStart'):
        metrics['response_download_ms'] = timing['responseEnd'] - timing['responseStart']
    
    # DOM processing time
    if timing.get('domComplete') and timing.get('domLoading'):
        metrics['dom_processing_ms'] = timing['domComplete'] - timing['domLoading']
    
    # DOM Interactive
    if timing.get('domInteractive'):
        metrics['dom_interactive_ms'] = timing['domInteractive'] - nav_start
    
    # DOM Content Loaded
    if timing.get('domContentLoadedEventEnd') and timing.get('domContentLoadedEventStart'):
        metrics['dom_content_loaded_ms'] = timing['domContentLoadedEventEnd'] - timing['domContentLoadedEventStart']
    
    # Total page load time
    if timing.get('loadEventEnd'):
        metrics['total_load_ms'] = timing['loadEventEnd'] - nav_start
    
    return metrics


def _analyze_resources(resources: List[Dict]) -> Dict:
    """
    Analiza los recursos cargados.
    
    Args:
        resources: Lista de recursos de Performance API
        
    Returns:
        Análisis de recursos
    """
    analysis = {
        'total_requests': len(resources),
        'total_size_bytes': 0,
        'by_type': {},
        'largest_resources': []
    }
    
    # Agrupar por tipo
    type_stats = {}
    
    for resource in resources:
        res_type = resource.get('type', 'other')
        size = resource.get('size', 0)
        duration = resource.get('duration', 0)
        
        analysis['total_size_bytes'] += size
        
        if res_type not in type_stats:
            type_stats[res_type] = {
                'count': 0,
                'total_size': 0,
                'total_duration': 0
            }
        
        type_stats[res_type]['count'] += 1
        type_stats[res_type]['total_size'] += size
        type_stats[res_type]['total_duration'] += duration
    
    analysis['by_type'] = type_stats
    analysis['total_size_kb'] = round(analysis['total_size_bytes'] / 1024, 2)
    analysis['total_size_mb'] = round(analysis['total_size_bytes'] / (1024 * 1024), 2)
    
    # Recursos más grandes
    sorted_resources = sorted(resources, key=lambda x: x.get('size', 0), reverse=True)
    analysis['largest_resources'] = [
        {
            'name': r.get('name', '')[:100],  # Truncar URLs largas
            'type': r.get('type', 'other'),
            'size_kb': round(r.get('size', 0) / 1024, 2),
            'duration_ms': round(r.get('duration', 0), 2)
        }
        for r in sorted_resources[:5]  # Top 5
    ]
    
    return analysis


def _get_navigation_type(nav_type: int) -> str:
    """
    Convierte el tipo de navegación a string.
    
    Args:
        nav_type: Tipo de navegación (0-2)
        
    Returns:
        String descriptivo
    """
    types = {
        0: 'navigate',
        1: 'reload',
        2: 'back_forward'
    }
    return types.get(nav_type, 'unknown')


def measure_page_load_time(url: str, timeout: int = 30) -> Optional[float]:
    """
    Mide solo el tiempo de carga de la página.
    
    Args:
        url: URL a medir
        timeout: Timeout en segundos
        
    Returns:
        Tiempo en milisegundos o None si hay error
    """
    driver = None
    
    try:
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(timeout)
        
        start_time = time.time()
        driver.get(url)
        
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        load_time = (time.time() - start_time) * 1000
        
        logger.info(f"Tiempo de carga de {url}: {load_time:.2f}ms")
        return round(load_time, 2)
        
    except Exception as e:
        logger.error(f"Error midiendo tiempo de carga: {e}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def get_performance_insights(metrics: Dict) -> Dict:
    """
    Genera insights y recomendaciones basadas en las métricas.
    
    Args:
        metrics: Métricas de performance
        
    Returns:
        Diccionario con insights y recomendaciones
    """
    insights = {
        'score': 'good',  # good, fair, poor
        'issues': [],
        'recommendations': []
    }
    
    if not metrics:
        return insights
    
    load_time = metrics.get('load_time_ms', 0)
    resources = metrics.get('resources', {})
    total_size_mb = resources.get('total_size_mb', 0)
    total_requests = resources.get('total_requests', 0)
    
    # Evaluar tiempo de carga
    if load_time > 3000:
        insights['score'] = 'poor'
        insights['issues'].append(f"Tiempo de carga alto: {load_time}ms")
        insights['recommendations'].append("Optimizar recursos y reducir tiempo de carga")
    elif load_time > 1500:
        insights['score'] = 'fair'
        insights['issues'].append(f"Tiempo de carga moderado: {load_time}ms")
    
    # Evaluar tamaño total
    if total_size_mb > 5:
        insights['issues'].append(f"Tamaño de página grande: {total_size_mb}MB")
        insights['recommendations'].append("Comprimir imágenes y minificar recursos")
    
    # Evaluar número de requests
    if total_requests > 100:
        insights['issues'].append(f"Muchos requests HTTP: {total_requests}")
        insights['recommendations'].append("Combinar archivos CSS/JS y usar sprites")
    
    return insights
