"""
Generación de screenshots de páginas web.
Utiliza Selenium con WebDriver para renderizar y capturar páginas.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import base64
import logging
import time
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Directorio para guardar screenshots
SCREENSHOTS_DIR = "/tmp/screenshots"


def _get_chrome_options(width: int, height: int, headless: bool = True) -> Options:
    """
    Configura las opciones de Chrome para screenshots.
    
    Args:
        width: Ancho de la ventana
        height: Alto de la ventana
        headless: Ejecutar en modo headless
        
    Returns:
        Opciones de Chrome configuradas
    """
    options = Options()
    
    if headless:
        options.add_argument('--headless=new')
    
    # Opciones para estabilidad
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-extensions')
    
    # Tamaño de ventana
    options.add_argument(f'--window-size={width},{height}')
    
    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Deshabilitar notificaciones y popups
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0
    }
    options.add_experimental_option("prefs", prefs)
    
    # Logging
    options.add_argument('--log-level=3')  # Solo errores críticos
    
    return options


def generate_screenshot(url: str, timeout: int = 30) -> Optional[str]:
    """
    Genera un screenshot de una página web con configuración por defecto.
    
    Args:
        url: URL de la página a capturar
        timeout: Timeout en segundos para la carga de la página
        
    Returns:
        String con la imagen codificada en base64 o None si hay error
    """
    return generate_screenshot_with_options(url, timeout=timeout)


def generate_screenshot_with_options(url: str, width: int = 1920,
                                     height: int = 1080,
                                     full_page: bool = True,
                                     timeout: int = 30) -> Optional[str]:
    """
    Genera un screenshot con opciones personalizadas.
    
    Args:
        url: URL de la página a capturar
        width: Ancho del viewport en pixels
        height: Alto del viewport en pixels
        full_page: Si True, captura la página completa (scroll)
        timeout: Timeout en segundos
        
    Returns:
        String con la imagen codificada en base64 o None si hay error
    """
    driver = None
    
    try:
        logger.info(f"Iniciando captura de screenshot para {url}")
        
        # Configurar opciones de Chrome
        options = _get_chrome_options(width, height)
        
        # Inicializar driver (Selenium 4.6+ usa selenium-manager automáticamente)
        # No necesitamos especificar service, Selenium lo maneja automáticamente
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(timeout)
        
        # Cargar página
        logger.debug(f"Cargando página: {url}")
        driver.get(url)
        
        # Esperar a que el DOM esté listo
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        # Esperar un poco más para renderizado completo
        time.sleep(2)
        
        # Capturar screenshot
        if full_page:
            # Obtener dimensiones completas de la página
            total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
            driver.set_window_size(width, total_height)
            time.sleep(1)  # Esperar a que se ajuste el tamaño
            
            logger.debug(f"Capturando página completa ({width}x{total_height}px)")
            screenshot_png = driver.get_screenshot_as_png()
        else:
            logger.debug(f"Capturando viewport ({width}x{height}px)")
            screenshot_png = driver.get_screenshot_as_png()
        
        # Convertir a base64
        screenshot_b64 = base64.b64encode(screenshot_png).decode('utf-8')
        
        size_kb = len(screenshot_b64) / 1024
        logger.info(f"Screenshot capturado exitosamente ({size_kb:.2f} KB en base64)")
        
        return screenshot_b64
        
    except TimeoutException:
        logger.error(f"Timeout cargando {url}")
        return None
    except WebDriverException as e:
        logger.error(f"Error de WebDriver capturando {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado capturando screenshot de {url}: {e}", exc_info=True)
        return None
    finally:
        if driver:
            try:
                driver.quit()
                logger.debug("WebDriver cerrado correctamente")
            except:
                pass


def save_screenshot_to_file(url: str, filename: str, width: int = 1920, 
                            height: int = 1080, full_page: bool = True) -> Optional[str]:
    """
    Captura un screenshot y lo guarda en disco.
    
    Args:
        url: URL a capturar
        filename: Nombre del archivo (sin extensión)
        width: Ancho de la ventana
        height: Alto de la ventana
        full_page: Captura página completa o solo viewport
        
    Returns:
        Path del archivo guardado o None si hay error
    """
    try:
        # Crear directorio si no existe
        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        
        # Capturar screenshot
        screenshot_b64 = generate_screenshot_with_options(url, width, height, full_page)
        
        if screenshot_b64 is None:
            return None
        
        # Decodificar y guardar
        screenshot_bytes = base64.b64decode(screenshot_b64)
        filepath = os.path.join(SCREENSHOTS_DIR, f"{filename}.png")
        
        with open(filepath, 'wb') as f:
            f.write(screenshot_bytes)
        
        logger.info(f"Screenshot guardado en: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error guardando screenshot: {e}", exc_info=True)
        return None


def get_page_dimensions(url: str, timeout: int = 30) -> Optional[Tuple[int, int]]:
    """
    Obtiene las dimensiones completas de una página.
    
    Args:
        url: URL de la página
        timeout: Timeout en segundos
        
    Returns:
        Tupla (width, height) o None si hay error
    """
    driver = None
    
    try:
        options = _get_chrome_options(1920, 1080)
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(timeout)
        
        driver.get(url)
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        width = driver.execute_script("return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth)")
        height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
        
        logger.info(f"Dimensiones de {url}: {width}x{height}px")
        return (width, height)
        
    except Exception as e:
        logger.error(f"Error obteniendo dimensiones: {e}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def setup_webdriver(width: int = 1920, height: int = 1080, headless: bool = True):
    """
    Configura el webdriver de Selenium en modo headless.
    
    Args:
        width: Ancho de la ventana
        height: Alto de la ventana
        headless: Modo headless
        
    Returns:
        Webdriver configurado
    """
    try:
        options = _get_chrome_options(width, height, headless)
        driver = webdriver.Chrome(options=options)
        logger.info("WebDriver configurado exitosamente")
        return driver
    except Exception as e:
        logger.error(f"Error configurando WebDriver: {e}")
        return None


def cleanup_webdriver(driver):
    """
    Limpia recursos del webdriver.
    
    Args:
        driver: Webdriver a limpiar
    """
    if driver:
        try:
            driver.quit()
            logger.debug("WebDriver limpiado correctamente")
        except Exception as e:
            logger.error(f"Error limpiando WebDriver: {e}")
