# ROADMAP DE DESARROLLO - TP2 Computación II

**Proyecto:** Sistema de Scraping y Análisis Web Distribuido  
**Usuario GitHub:** abenavidezUM  
**Repositorio:** https://github.com/abenavidezUM/Computacion_II_TP2.git  
**Fecha de entrega:** 14/11/2025

---

## OBJETIVO GENERAL

Desarrollar un sistema distribuido con dos servidores:
- **Servidor A (asyncio):** Scraping web asíncrono + coordinación
- **Servidor B (multiprocessing):** Procesamiento intensivo paralelo
- **Transparencia:** El cliente solo interactúa con Servidor A

---

## ETAPA 1: ESTRUCTURA BASE Y CONFIGURACIÓN

### Objetivos
- Crear estructura de carpetas según especificación
- Configurar dependencias en requirements.txt
- Implementar CLI con argparse para ambos servidores
- README básico con instrucciones

### Archivos a crear
```
TP2/
├── server_scraping.py
├── server_processing.py
├── client.py
├── scraper/
│   ├── __init__.py
│   ├── html_parser.py
│   ├── metadata_extractor.py
│   └── async_http.py
├── processor/
│   ├── __init__.py
│   ├── screenshot.py
│   ├── performance.py
│   └── image_processor.py
├── common/
│   ├── __init__.py
│   ├── protocol.py
│   └── serialization.py
├── tests/
│   ├── test_scraper.py
│   └── test_processor.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Criterios de éxito
- [✓] Estructura de carpetas creada
- [✓] CLI de server_scraping.py funcional (-h, -i, -p, -w)
- [✓] CLI de server_processing.py funcional (-h, -i, -p, -n)
- [✓] requirements.txt con todas las dependencias
- [✓] .gitignore configurado correctamente
- [✓] README con instrucciones básicas

### Notas técnicas
- Usar argparse para parseo de argumentos
- Validar IPv4 e IPv6 en argparse
- Puerto válido: 1-65535

---

## ETAPA 2: SERVIDOR A - BASE ASYNCIO

### Objetivos
- Implementar servidor HTTP asíncrono con aiohttp
- Crear endpoint básico `/scrape` que reciba URLs
- Soportar IPv4 e IPv6
- Responder con JSON simple

### Funcionalidades
- Servidor aiohttp.web con Application
- Handler para GET/POST `/scrape?url=<URL>`
- Validación básica de URL
- Respuesta JSON con estructura base

### Criterios de éxito
- [✓] Servidor levanta correctamente en IPv4
- [✓] Servidor levanta correctamente en IPv6
- [✓] Endpoint /scrape responde correctamente
- [✓] Manejo básico de errores (400, 500)
- [✓] Logging de requests

### Testing
```bash
# Probar IPv4
python server_scraping.py -i 127.0.0.1 -p 8000

# Probar IPv6
python server_scraping.py -i ::1 -p 8000

# Request de prueba
curl "http://localhost:8000/scrape?url=https://example.com"
```

---

## ETAPA 3: SCRAPING BÁSICO

### Objetivos
- Implementar extracción de contenido HTML
- Parsear con BeautifulSoup4
- Extraer: título, enlaces, meta tags, imágenes, estructura

### Módulos a implementar
- `scraper/html_parser.py`: Funciones de parsing HTML
- `scraper/metadata_extractor.py`: Extracción de metadatos
- `scraper/async_http.py`: Cliente HTTP asíncrono con aiohttp

### Funciones principales
```python
async def fetch_html(url: str, timeout: int = 30) -> str
def extract_title(soup: BeautifulSoup) -> str
def extract_links(soup: BeautifulSoup, base_url: str) -> list[str]
def extract_meta_tags(soup: BeautifulSoup) -> dict
def count_images(soup: BeautifulSoup) -> int
def analyze_structure(soup: BeautifulSoup) -> dict
```

### Criterios de éxito
- [✓] Extrae título correctamente
- [✓] Extrae todos los enlaces (absolutos)
- [✓] Extrae meta tags (description, keywords, OG)
- [✓] Cuenta imágenes
- [✓] Analiza estructura H1-H6
- [✓] Timeout de 30 segundos funciona
- [✓] Maneja páginas inaccesibles

### Testing
- Probar con: example.com, wikipedia.org, github.com
- Probar con URL inválida
- Probar con timeout

---

## ETAPA 4: SERVIDOR B - BASE MULTIPROCESSING

### Objetivos
- Servidor TCP con socketserver
- Pool de procesos con multiprocessing
- Protocolo de comunicación básico
- Manejo de múltiples conexiones concurrentes

### Implementación
- Usar socketserver.ThreadingTCPServer
- Crear ProcessPoolExecutor para workers
- Protocolo: [LENGTH(4 bytes)][JSON payload]

### Criterios de éxito
- [✓] Servidor escucha en puerto configurado
- [✓] Pool de N procesos creado
- [✓] Recibe y parsea mensajes
- [✓] Responde correctamente
- [✓] Maneja múltiples conexiones

### Testing
```bash
python server_processing.py -i 127.0.0.1 -p 9000 -n 4
```

---

## ETAPA 5: COMUNICACIÓN ENTRE SERVIDORES

### Objetivos
- Protocolo de serialización (JSON)
- Cliente socket asíncrono en Servidor A
- Integración completa A <-> B

### Protocolo definido
```json
// Request de A hacia B
{
  "task": "screenshot|performance|thumbnails",
  "url": "https://example.com",
  "params": {...}
}

// Response de B hacia A
{
  "status": "success|error",
  "result": {...},
  "error": "mensaje de error si aplica"
}
```

### Funciones en common/protocol.py
```python
def encode_message(data: dict) -> bytes
def decode_message(data: bytes) -> dict
async def send_to_processor(host: str, port: int, task: dict) -> dict
```

### Criterios de éxito
- [ ] Serialización/deserialización funciona
- [ ] Servidor A se conecta a Servidor B
- [ ] Envío de tareas funciona
- [ ] Respuestas se reciben correctamente
- [ ] Manejo de errores de conexión

---

## ETAPA 6: SCREENSHOT CON SELENIUM/PLAYWRIGHT

### Objetivos
- Configurar navegador headless
- Generar screenshot de página completa
- Codificar en base64
- Ejecutar en proceso separado

### Implementación en processor/screenshot.py
```python
def generate_screenshot(url: str, timeout: int = 30) -> str
    # Usa Selenium + ChromeDriver headless
    # O Playwright (más moderno)
    # Retorna base64 del PNG
```

### Consideraciones
- Modo headless para eficiencia
- Timeout configurado
- Tamaño de viewport estándar (1920x1080)
- Cleanup de recursos

### Criterios de éxito
- [ ] Screenshot se genera correctamente
- [ ] Codificación base64 funciona
- [ ] Timeout respetado
- [ ] No hay memory leaks
- [ ] Funciona con páginas JavaScript-heavy

---

## ETAPA 7: ANÁLISIS DE RENDIMIENTO

### Objetivos
- Medir tiempo de carga
- Calcular tamaño total de recursos
- Contar número de requests

### Implementación en processor/performance.py
```python
def analyze_performance(url: str) -> dict
    # Usa Selenium + performance API
    # O herramientas de network monitoring
    # Retorna: load_time_ms, total_size_kb, num_requests
```

### Métricas a capturar
- Tiempo de carga completo (DOMContentLoaded)
- Tamaño de HTML, CSS, JS, imágenes
- Número total de requests HTTP

### Criterios de éxito
- [ ] Métricas precisas capturadas
- [ ] Ejecución en proceso separado
- [ ] No interfiere con screenshot
- [ ] Timeout manejado

---

## ETAPA 8: PROCESAMIENTO DE IMÁGENES

### Objetivos
- Descargar imágenes principales
- Generar thumbnails optimizados
- Codificar en base64

### Implementación en processor/image_processor.py
```python
async def download_images(urls: list[str], max_images: int = 5) -> list[bytes]
def generate_thumbnail(image_data: bytes, size: tuple = (150, 150)) -> str
def process_page_images(url: str, image_urls: list[str]) -> list[str]
```

### Consideraciones
- Limitar a 5-10 imágenes principales
- Thumbnails de 150x150px
- Usar Pillow para redimensionar
- Formato JPEG para thumbnails (menor tamaño)

### Criterios de éxito
- [ ] Descarga imágenes principales
- [ ] Genera thumbnails correctamente
- [ ] Codificación base64 funciona
- [ ] Maneja imágenes corruptas
- [ ] Timeout por imagen

---

## ETAPA 9: MANEJO DE ERRORES Y ROBUSTEZ

### Objetivos
- Timeouts en todas las operaciones
- Manejo de URLs inválidas
- Errores de red y comunicación
- Límites de recursos

### Errores a manejar

#### En Servidor A (asyncio)
- URL inválida o malformada
- Timeout de scraping (30s)
- Servidor B no disponible
- asyncio.TimeoutError
- aiohttp.ClientError

#### En Servidor B (multiprocessing)
- Proceso worker falla
- Timeout en screenshot/performance
- Página no carga
- Recursos no disponibles

### Implementación
- Try-except en todas las funciones async
- Logging estructurado con logging module
- Respuestas de error consistentes

### Criterios de éxito
- [ ] Ningún error crashea el servidor
- [ ] Todos los errores loguean información útil
- [ ] Respuestas de error claras para el cliente
- [ ] Timeouts funcionan correctamente
- [ ] Manejo de recursos (cleanup)

---

## ETAPA 10: TESTING, CLIENTE Y DOCUMENTACIÓN

### Objetivos
- Cliente de prueba funcional
- Tests unitarios básicos
- Documentación completa
- Verificación de requerimientos

### Cliente de prueba (client.py)
```python
# Cliente que hace requests al Servidor A
# Muestra resultados formateados
# Maneja diferentes URLs
# Muestra errores claramente
```

### Tests en tests/
- `test_scraper.py`: Tests de funciones de scraping
- `test_processor.py`: Tests de funciones de procesamiento
- Tests de integración básicos

### README.md completo
- Descripción del proyecto
- Instalación de dependencias
- Instrucciones de ejecución
- Ejemplos de uso
- Arquitectura del sistema
- Troubleshooting

### Criterios de éxito
- [ ] Cliente funciona correctamente
- [ ] Al menos 10 tests unitarios
- [ ] README completo y claro
- [ ] Todos los requerimientos cumplidos
- [ ] Sistema funciona end-to-end

---

## ETAPA 11 (OPCIONAL): BONUS TRACK

### Opción 1: Sistema de Cola con Task IDs
- Respuesta inmediata con task_id
- Endpoint `/status/{task_id}`
- Endpoint `/result/{task_id}`
- Estados: pending, scraping, processing, completed, failed
- Almacenamiento en memoria o Redis

### Opción 2: Rate Limiting y Caché
- Rate limiting por dominio (max N req/min)
- Sistema de caché con TTL (1 hora)
- Usar diccionario con timestamps
- Opcional: Redis para caché persistente

### Opción 3: Análisis Avanzado
- Detección de tecnologías (Wappalyzer-like)
- Score de SEO básico
- Extracción de JSON-LD / Schema.org
- Análisis de accesibilidad

### Criterios de éxito
- [ ] Al menos UN bonus implementado
- [ ] Documentado en README
- [ ] Tests para funcionalidad bonus

---

## CHECKLIST DE REQUERIMIENTOS OBLIGATORIOS

### Funcionalidad Mínima
- [ ] 1. Scraping de contenido HTML
- [ ] 2. Extracción de metadatos
- [ ] 3. Generación de screenshot
- [ ] 4. Análisis de rendimiento

### Networking
- [ ] Servidor A soporta IPv4
- [ ] Servidor A soporta IPv6
- [ ] Manejo de timeouts
- [ ] Manejo de conexiones rechazadas
- [ ] Servidor B en puerto diferente
- [ ] Protocolo binario eficiente

### Concurrencia y Paralelismo
- [ ] Servidor A usa asyncio
- [ ] Requests HTTP asíncronos (aiohttp)
- [ ] Múltiples clientes concurrentes
- [ ] Servidor B usa multiprocessing
- [ ] Pool de workers
- [ ] Sincronización entre procesos

### Interfaz CLI
- [ ] server_scraping.py: -i, -p, -w, -h
- [ ] server_processing.py: -i, -p, -n, -h
- [ ] Validación de argumentos
- [ ] Mensajes de ayuda claros

### Manejo de Errores
- [ ] URLs inválidas
- [ ] Timeout 30s por página
- [ ] Errores de comunicación entre servidores
- [ ] Recursos no disponibles
- [ ] Límites de memoria

### Formato de Respuesta
- [ ] Estructura JSON correcta
- [ ] Campo "url"
- [ ] Campo "timestamp"
- [ ] Campo "scraping_data" con subcampos
- [ ] Campo "processing_data" con subcampos
- [ ] Campo "status"

---

## STACK TECNOLÓGICO

### Core
- Python 3.8+
- asyncio (built-in)
- multiprocessing (built-in)
- socketserver (built-in)
- argparse (built-in)

### HTTP y Scraping
- aiohttp: Cliente/servidor HTTP asíncrono
- beautifulsoup4: Parsing HTML
- lxml: Parser XML/HTML rápido

### Procesamiento
- Pillow: Procesamiento de imágenes
- selenium: Screenshots y automation
- aiofiles: I/O asíncrono de archivos

### Testing
- pytest: Framework de testing
- pytest-asyncio: Testing de código asíncrono

---

## PATRONES Y ARQUITECTURA

### Patrones aplicados
- **Client-Server Pattern**: Arquitectura distribuida
- **Worker Pool Pattern**: Pool de procesos
- **Protocol Pattern**: Comunicación estandarizada
- **Separation of Concerns**: Módulos independientes
- **Error Handling Pattern**: Try-except sistemático

### Principios de diseño
- **DRY**: Don't Repeat Yourself
- **KISS**: Keep It Simple, Stupid
- **SOLID**: Especialmente SRP (Single Responsibility)
- **Código limpio**: Funciones pequeñas y descriptivas

---

## CONVENCIONES DE CÓDIGO

### Nombres
- Funciones: `snake_case` descriptivo
  - Ejemplos: `extract_html_title`, `generate_page_screenshot`
- Variables: `snake_case` descriptivo
  - Ejemplos: `scraping_results`, `processing_pool`
- Clases: `PascalCase`
  - Ejemplos: `ScrapingServer`, `ProcessingHandler`
- Constantes: `UPPER_SNAKE_CASE`
  - Ejemplos: `DEFAULT_TIMEOUT`, `MAX_WORKERS`

### Documentación
- Docstrings en todas las funciones públicas
- Type hints donde sea útil
- Comentarios para lógica compleja
- README actualizado

### NO usar
- Emojis en código o logs
- Nombres genéricos (func1, data, temp)
- Código comentado (eliminar)
- Magic numbers (usar constantes)

---

## COMANDOS ÚTILES

### Instalación
```bash
pip install -r requirements.txt
```

### Ejecución
```bash
# Terminal 1: Servidor de procesamiento
python server_processing.py -i 127.0.0.1 -p 9000 -n 4

# Terminal 2: Servidor de scraping
python server_scraping.py -i 127.0.0.1 -p 8000 -w 4

# Terminal 3: Cliente
python client.py --url https://example.com
```

### Testing
```bash
pytest tests/ -v
pytest tests/test_scraper.py::test_extract_title
```

### Git
```bash
git add .
git commit -m "Mensaje descriptivo"
git push origin main
```

---

## NOTAS IMPORTANTES

### Archivos que NO se pushean
- `consigna.txt` (archivo de la cátedra)
- `ROADMAP.md` (este archivo de planificación)
- `__pycache__/`
- `*.pyc`
- `.env`
- Screenshots y archivos temporales

### Deadlines internos sugeridos
- Etapa 1-3: Primera semana
- Etapa 4-5: Segunda semana
- Etapa 6-8: Tercera semana
- Etapa 9-10: Cuarta semana
- Bonus: Si hay tiempo adicional

### Testing continuo
- Testear cada función al crearla
- Testear integración entre módulos
- No avanzar si algo no funciona
- Mantener servidores funcionando siempre

---

## ESTADO ACTUAL

**Última actualización:** 22/10/2025

**Etapa actual:** Etapa 7 - COMPLETADA

**Logros de la Etapa 7:**
- ✓ Análisis de rendimiento implementado con Selenium y Performance API
- ✓ Navigation Timing API: DNS, TCP, Request/Response, DOM metrics
- ✓ Paint Metrics: First Paint, First Contentful Paint
- ✓ Resource Performance: Análisis de recursos cargados por tipo
- ✓ Timing Metrics: load time, DOM interactive, DOM content loaded
- ✓ Performance Insights: Score (good/fair/poor) y recomendaciones
- ✓ Métricas detalladas: dns_lookup_ms, tcp_connection_ms, dom_processing_ms
- ✓ Análisis de navegación: tipo (navigate/reload) y redirect count
- ✓ Testing verificado con test directo exitoso
- ✓ Integración con servidor de procesamiento

**Próximos pasos - Etapa 8:**
1. Implementar procesamiento de imágenes
2. Generación de thumbnails
3. Redimensionamiento de imágenes
4. Optimización y compresión
5. Múltiples formatos (JPEG, PNG, WebP)

---

## RECURSOS Y REFERENCIAS

- AsyncIO: https://docs.python.org/3/library/asyncio.html
- aiohttp: https://docs.aiohttp.org/
- Multiprocessing: https://docs.python.org/3/library/multiprocessing.html
- SocketServer: https://docs.python.org/3/library/socketserver.html
- BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Selenium: https://selenium-python.readthedocs.io/
- Playwright: https://playwright.dev/python/

---

**¡IMPORTANTE!** Completar cada etapa antes de avanzar. Testing continuo es clave.

