# Códigos de Error y Manejo de Errores

## Sistema de Respuestas

Todas las respuestas del sistema siguen el formato estándar:

```json
{
  "status": "success" | "error" | "warning",
  "message": "Mensaje descriptivo",
  "details": "Detalles adicionales (opcional)",
  "data": {}  // Datos específicos según el endpoint
}
```

---

## Códigos HTTP

### Servidor de Scraping (Puerto 8000)

| Código | Significado | Cuándo ocurre |
|--------|-------------|---------------|
| 200 | OK | Scraping exitoso |
| 400 | Bad Request | URL inválida o parámetros incorrectos |
| 500 | Internal Server Error | Error inesperado en el servidor |
| 503 | Service Unavailable | Servidor de procesamiento no disponible |

### Servidor de Procesamiento (Puerto 9000)

| Tipo | Significado | Cuándo ocurre |
|------|-------------|---------------|
| success | Éxito | Tarea completada correctamente |
| error | Error | Error al procesar la tarea |
| warning | Advertencia | Tarea completada parcialmente |

---

## Errores Comunes

### Errores de Validación de URL

**Error:** URL vacía
```json
{
  "status": "error",
  "message": "URL parameter is required",
  "details": "Provide url as query parameter (?url=...) or in JSON body"
}
```

**Error:** URL con formato inválido
```json
{
  "status": "error",
  "message": "Invalid URL",
  "details": "URL must start with http:// or https://"
}
```

**Error:** URL demasiado larga
```json
{
  "status": "error",
  "message": "Invalid URL",
  "details": "URL demasiado larga (máximo 2048 caracteres)"
}
```

**Error:** Dominio bloqueado
```json
{
  "status": "error",
  "message": "Invalid URL",
  "details": "Dominio bloqueado por seguridad: 'localhost'"
}
```

**Error:** IP privada bloqueada
```json
{
  "status": "error",
  "message": "Invalid URL",
  "details": "IP privada bloqueada por seguridad: '192.168.1.1'"
}
```

---

### Errores de Comunicación

**Error:** Timeout en scraping
```json
{
  "status": "error",
  "message": "Request timeout",
  "details": "Failed to fetch URL within 30 seconds"
}
```

**Error:** Servidor de procesamiento no disponible
```json
{
  "status": "error",
  "message": "Processing server unavailable",
  "details": "Could not connect to processing server"
}
```

**Error:** Error de red
```json
{
  "status": "error",
  "message": "Network error",
  "details": "Connection refused / DNS resolution failed"
}
```

---

### Errores de Procesamiento de Imágenes

**Error:** No se pudo descargar imagen
```json
{
  "status": "warning",
  "message": "No thumbnails could be generated",
  "thumbnails": [],
  "total_processed": 0,
  "total_requested": 5
}
```

**Error:** Formato de imagen inválido
```json
{
  "status": "error",
  "message": "Invalid image format",
  "details": "Formato inválido: 'BMP'. Formatos permitidos: JPEG, PNG, WEBP, GIF"
}
```

**Error:** Dimensiones inválidas
```json
{
  "status": "error",
  "message": "Invalid dimensions",
  "details": "Dimensiones demasiado grandes: 5000x5000. Máximo: 4096x4096"
}
```

**Error:** Calidad inválida
```json
{
  "status": "error",
  "message": "Invalid quality",
  "details": "Calidad inválida: 150. Debe estar entre 1 y 100"
}
```

---

### Errores de Screenshot

**Error:** Timeout en captura
```json
{
  "status": "error",
  "task_type": "screenshot",
  "message": "Failed to capture screenshot",
  "details": "Timeout loading page"
}
```

**Error:** Página no accesible
```json
{
  "status": "error",
  "task_type": "screenshot",
  "message": "Failed to capture screenshot",
  "details": "Page returned HTTP 404"
}
```

---

### Errores de Performance

**Error:** No se pudo analizar
```json
{
  "status": "error",
  "task_type": "performance",
  "message": "Failed to analyze performance",
  "details": "WebDriver error"
}
```

---

## Límites del Sistema

### Límites Generales

| Recurso | Límite | Descripción |
|---------|--------|-------------|
| URL Length | 2048 caracteres | Longitud máxima de URL |
| Scraping Timeout | 60 segundos | Tiempo máximo para scraping |
| Processing Timeout | 120 segundos | Tiempo máximo para procesamiento |
| Workers | 32 | Número máximo de workers |

### Límites de Imágenes

| Recurso | Límite | Descripción |
|---------|--------|-------------|
| URLs por request | 20 | Máximo de URLs de imágenes |
| Imágenes a procesar | 10 | Máximo a procesar efectivamente |
| Tamaño de imagen | 10 MB | Tamaño máximo por imagen |
| Dimensión máxima | 4096x4096 | Dimensiones máximas |
| Dimensión thumbnail | 500x500 | Tamaño máximo de thumbnail |
| Calidad | 1-100 | Rango de calidad JPEG/WEBP |

### Límites de Puertos

| Tipo | Rango | Descripción |
|------|-------|-------------|
| Mínimo | 1024 | Evita puertos privilegiados |
| Máximo | 65535 | Puerto máximo válido |

---

## Manejo de Errores en el Código

### Servidor A (Asíncrono)

```python
try:
    # Operación asíncrona
    result = await async_operation()
except asyncio.TimeoutError:
    logger.error("Timeout en operación")
    return error_response("Timeout", 504)
except aiohttp.ClientError as e:
    logger.error(f"Error de red: {e}")
    return error_response("Network error", 503)
except Exception as e:
    logger.error(f"Error inesperado: {e}", exc_info=True)
    return error_response("Internal error", 500)
```

### Servidor B (Multiprocessing)

```python
try:
    # Operación intensiva
    result = process_task(task)
except TimeoutException:
    logger.error("Timeout en procesamiento")
    return {'status': 'error', 'message': 'Timeout'}
except Exception as e:
    logger.error(f"Error en worker: {e}", exc_info=True)
    return {'status': 'error', 'message': str(e)}
finally:
    # Cleanup de recursos
    cleanup_resources()
```

---

## Logs del Sistema

### Niveles de Log

| Nivel | Uso | Ejemplo |
|-------|-----|---------|
| DEBUG | Debugging detallado | "Descargando imagen: https://..." |
| INFO | Operaciones normales | "Request recibido desde 127.0.0.1" |
| WARNING | Situaciones anormales | "URL inválida desde cliente" |
| ERROR | Errores recuperables | "Error descargando imagen" |
| CRITICAL | Errores fatales | "Servidor no pudo iniciar" |

### Formato de Log

```
2025-11-07 17:00:00,000 - module_name - LEVEL - Message
```

Ejemplo:
```
2025-11-07 17:01:44 - processor.image_processor - INFO - Procesando imagen 1/5
2025-11-07 17:01:46 - processor.image_processor - WARNING - Error descargando imagen: HTTP 503
```

---

## Recuperación de Errores

### Reintentos Automáticos

- **Descargas de imágenes**: Sin reintentos (falla rápidamente)
- **Screenshots**: Sin reintentos (timeout configurable)
- **Performance**: Sin reintentos (timeout configurable)

### Degradación Grasa (Graceful Degradation)

Si una parte del procesamiento falla, el resto continúa:

```json
{
  "status": "success",
  "scraping_data": { ... },  // Exitoso
  "processing_data": {
    "screenshot": { ... },     // Exitoso
    "performance": {           // Falló
      "status": "error",
      "message": "Timeout"
    },
    "thumbnails": []          // Falló silenciosamente
  }
}
```

---

## Checklist de Robustez

- [x] Validación de todos los inputs
- [x] Timeouts en todas las operaciones de red
- [x] Try-except en funciones críticas
- [x] Logging estructurado en todos los niveles
- [x] Límites de recursos (tamaño, cantidad, tiempo)
- [x] Sanitización de datos de usuario
- [x] Respuestas de error consistentes
- [x] Cleanup de recursos (finally blocks)
- [x] Degradación graciosa (continuar pese a errores parciales)
- [x] Documentación de códigos de error

