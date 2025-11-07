# TP2 - Sistema de Scraping y Análisis Web Distribuido

Sistema distribuido de scraping y análisis web que utiliza programación asíncrona y paralelismo para extraer y procesar información de sitios web de forma eficiente.

## Descripción

El sistema consta de dos servidores que trabajan de forma coordinada:

- **Servidor de Scraping (Parte A)**: Servidor HTTP asíncrono que maneja requests de scraping utilizando `asyncio`. Extrae información estructural de páginas web.
- **Servidor de Procesamiento (Parte B)**: Servidor con `multiprocessing` que ejecuta tareas CPU-intensivas como generación de screenshots, análisis de rendimiento y procesamiento de imágenes.

## Arquitectura

```
Cliente HTTP
    |
    v
Servidor A (asyncio) ---[socket]---> Servidor B (multiprocessing)
    |                                      |
    |                                      v
    |                                Pool de Workers
    v
Respuesta JSON consolidada
```

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/abenavidezUM/Computacion_II_TP2.git
cd Computacion_II_TP2/TP2
```

### 2. Crear entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configuración adicional para screenshots

Para la funcionalidad de screenshots, necesitas instalar un driver de navegador:

**Opción 1: ChromeDriver (automático con webdriver-manager)**
```bash
# Ya incluido en requirements.txt
```

**Opción 2: Playwright (alternativa)**
```bash
pip install playwright
playwright install chromium
```

## Uso

### Iniciar el Servidor de Procesamiento (Servidor B)

Primero, inicia el servidor de procesamiento:

```bash
python server_processing.py -i 127.0.0.1 -p 9000 -n 4
```

**Opciones:**
- `-i, --ip`: Dirección IP de escucha
- `-p, --port`: Puerto de escucha
- `-n, --processes`: Número de procesos en el pool (default: número de CPUs)
- `-h, --help`: Muestra ayuda

### Iniciar el Servidor de Scraping (Servidor A)

En otra terminal, inicia el servidor de scraping:

```bash
python server_scraping.py -i 127.0.0.1 -p 8000 -w 4
```

**Opciones:**
- `-i, --ip`: Dirección IP de escucha (soporta IPv4/IPv6)
- `-p, --port`: Puerto de escucha
- `-w, --workers`: Número de workers concurrentes (default: 4)
- `--processor-host`: Host del servidor de procesamiento (default: 127.0.0.1)
- `--processor-port`: Puerto del servidor de procesamiento (default: 9000)
- `-h, --help`: Muestra ayuda

### Usar el Cliente

Realiza un request de scraping:

```bash
python client.py --url https://example.com
```

**Opciones:**
- `--url`: URL del sitio web a scrapear (requerido)
- `--server-host`: Host del servidor de scraping (default: 127.0.0.1)
- `--server-port`: Puerto del servidor de scraping (default: 8000)
- `--timeout`: Timeout en segundos (default: 60)
- `--output`: Archivo para guardar el resultado JSON
- `--process`: Solicitar procesamiento adicional (screenshots, performance, thumbnails)
- `--pretty`: Mostrar formato legible en lugar de JSON
- `--verbose, -v`: Información detallada

**Ejemplo con todas las opciones:**
```bash
# Simple
python client.py --url https://example.com

# Con formato legible
python client.py --url https://example.com --pretty

# Con procesamiento completo
python client.py --url https://example.com --process --pretty --verbose

# Guardar en archivo
python client.py --url https://github.com --timeout 120 --output result.json
```

### Soporte para IPv6

El servidor de scraping soporta IPv6:

```bash
# Servidor con IPv6
python server_scraping.py -i ::1 -p 8000

# Cliente apuntando a IPv6
python client.py --url https://example.com --server-host ::1
```

## Endpoints del Servidor de Scraping

### GET/POST /scrape

Realiza scraping de una URL.

**Parámetros:**
- `url` (query parameter): URL a scrapear

**Ejemplo:**
```bash
curl "http://localhost:8000/scrape?url=https://example.com"
```

**Respuesta:**
```json
{
  "url": "https://example.com",
  "timestamp": "2024-11-10T15:30:00Z",
  "scraping_data": {
    "title": "Título de la página",
    "links": ["url1", "url2"],
    "meta_tags": {
      "description": "...",
      "keywords": "..."
    },
    "structure": {
      "h1": 2,
      "h2": 5
    },
    "images_count": 15
  },
  "processing_data": {
    "screenshot": "base64_encoded_image",
    "performance": {
      "load_time_ms": 1250,
      "total_size_kb": 2048,
      "num_requests": 45
    }
  },
  "status": "success"
}
```

### GET /health

Verifica el estado del servidor.

**Ejemplo:**
```bash
curl "http://localhost:8000/health"
```

## Estructura del Proyecto

```
TP2/
├── server_scraping.py          # Servidor asyncio (Parte A)
├── server_processing.py        # Servidor multiprocessing (Parte B)
├── client.py                   # Cliente de prueba
├── scraper/                    # Módulo de scraping
│   ├── __init__.py
│   ├── html_parser.py          # Parsing HTML
│   ├── metadata_extractor.py   # Extracción de metadatos
│   └── async_http.py           # Cliente HTTP asíncrono
├── processor/                  # Módulo de procesamiento
│   ├── __init__.py
│   ├── screenshot.py           # Screenshots
│   ├── performance.py          # Análisis de rendimiento
│   └── image_processor.py      # Procesamiento de imágenes
├── common/                     # Utilidades comunes
│   ├── __init__.py
│   ├── protocol.py             # Protocolo de comunicación
│   └── serialization.py        # Serialización de datos
├── tests/                      # Tests
│   ├── __init__.py
│   ├── test_scraper.py
│   └── test_processor.py
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo
```

## Testing

El proyecto incluye tests unitarios completos para validar todas las funcionalidades críticas.

### Ejecutar Tests

Instalar pytest (si no está instalado):

```bash
pip install pytest
```

Ejecutar todos los tests:

```bash
pytest tests/ -v
```

Ejecutar tests específicos:

```bash
# Tests de scraping (HTML parser, metadata extractor)
pytest tests/test_scraper.py -v

# Tests de procesamiento (image processor, validators, limits)
pytest tests/test_processor.py -v
```

### Cobertura de Tests

**test_scraper.py** (18 tests):
- Extracción de título y fallbacks
- Extracción y conversión de enlaces
- Extracción de imágenes
- Análisis de estructura (H1-H6)
- Extracción de meta tags (basic, Open Graph, Twitter)
- Casos límite (HTML malformado, vacío, sin atributos)

**test_processor.py** (30+ tests):
- Generación de thumbnails con aspect ratio
- Redimensionamiento de imágenes
- Optimización y conversión de formatos
- Extracción de información de imágenes
- Validadores (URL, puertos, workers, timeouts, dimensiones, calidad, formatos)
- Límites de seguridad (safe timeouts, quality, dimensions, max images)
- Casos límite (datos inválidos, valores fuera de rango)

### Tests de Integración

Scripts de prueba manuales incluidos:

```bash
# Test de comunicación entre servidores
python test_communication.py

# Test de integración completo
python test_integration.py

# Test de performance
python test_performance.py

# Test de imágenes
python test_images.py
```

## Desarrollo

### Estado Actual

**Etapa 1 - Completada ✓**
- Estructura de carpetas creada
- CLI implementado para ambos servidores
- Servidores base funcionales
- Cliente de prueba básico

**Etapa 2 - Completada ✓**
- Servidor HTTP asíncrono completamente funcional
- Soporte IPv4 e IPv6 verificado
- Middlewares de logging y error handling
- Endpoints /scrape y /health operativos
- Validación robusta de URLs y parámetros

**Etapa 3 - Completada ✓**
- Cliente HTTP asíncrono con soporte SSL
- Parsing HTML con BeautifulSoup (lxml)
- Extracción de título, enlaces, meta tags
- Análisis de estructura (H1-H6)
- Conteo y URLs de imágenes

**Etapa 4 - Completada ✓**
- Protocolo de comunicación [LENGTH][JSON]
- Servidor TCP con ThreadingTCPServer
- Pool de procesos con multiprocessing
- Handler de tareas con tipos múltiples
- Testing de comunicación exitoso

**Etapa 5 - Completada ✓**
- Integración completa A↔B
- Endpoint /scrape con parámetro ?process=true
- Envío automático de tareas al servidor B
- Combinación de resultados en JSON unificado
- Testing end-to-end con 3 tests exitosos

**Etapa 6 - Completada ✓**
- Screenshots reales con Selenium WebDriver
- Captura full-page y viewport
- Tamaños personalizables (desktop, mobile, etc.)
- Formato PNG en base64
- 3 tests exitosos (example.com, github.com, python.org)

**Etapa 7 - Completada ✓**
- Análisis de rendimiento con Performance API
- Navigation Timing: DNS, TCP, Request/Response
- Paint Metrics: First Paint, First Contentful Paint
- DOM Metrics: Interactive, Content Loaded, Complete
- Performance Insights y recomendaciones
- Testing directo verificado

**Etapa 8 - Completada ✓**
- Procesamiento de imágenes con Pillow (PIL)
- Generación de thumbnails configurables
- Redimensionamiento y optimización de imágenes
- Conversión entre formatos (JPEG, PNG, WEBP)
- Descarga síncrona de imágenes (compatible con multiprocessing)
- Procesamiento batch de múltiples imágenes

**Etapa 9 - Completada ✓**
- Módulo de validadores robusto (common/validators.py)
- Módulo de límites de recursos (common/limits.py)
- Validación completa de URLs y parámetros
- Límites de recursos en todas las operaciones
- Documento de códigos de error (ERROR_CODES.md)
- Manejo de errores estructurado y consistente
- Degradación graciosa ante fallos parciales

**Etapa 10 - Completada ✓**
- Cliente mejorado con opciones --process, --pretty, --verbose
- Formateo legible de resultados con emojis
- tests/test_scraper.py con 18 tests unitarios
- tests/test_processor.py con 30+ tests unitarios
- Cobertura completa de funcionalidades críticas
- Documentación exhaustiva con ejemplos
- Todos los requisitos del TP cumplidos

**🎉 PROYECTO COMPLETADO - 100% de los requisitos implementados**

**Funcionalidades finales:**
- ✅ Servidor asíncrono con asyncio + aiohttp
- ✅ Servidor de procesamiento con multiprocessing
- ✅ Protocolo de comunicación inter-servidor personalizado
- ✅ Web scraping completo (HTML, meta tags, estructura)
- ✅ Screenshots reales con Selenium
- ✅ Análisis de rendimiento web (timing, resources, paint)
- ✅ Procesamiento de imágenes (thumbnails, resize, optimize)
- ✅ Validación robusta de inputs
- ✅ Límites de recursos y seguridad
- ✅ Manejo de errores estructurado
- ✅ 48+ tests unitarios
- ✅ Documentación completa

### Contribuir



## Tecnologías Utilizadas

- **asyncio**: Programación asíncrona
- **aiohttp**: Cliente/servidor HTTP asíncrono
- **multiprocessing**: Paralelismo con múltiples procesos
- **BeautifulSoup4**: Parsing HTML
- **Selenium**: Screenshots y automation
- **Pillow**: Procesamiento de imágenes
- **pytest**: Testing

## Licencia

Proyecto académico para Computación II - Facultad de Ingeniería

## Autores

- Agustín Benavídez (@abenavidezUM)
- Legajo: 62344

## Fecha de Entrega

14 de Noviembre de 2025

