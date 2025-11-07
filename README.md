# TP2 - Sistema de Scraping y Análisis Web Distribuido

Sistema distribuido de scraping y análisis web que utiliza programación asíncrona y paralelismo para extraer y procesar información de sitios web de forma eficiente.

**Trabajo Práctico N°2 - Computación II**  
**Fecha de entrega:** 14 de Noviembre de 2025

---

## 📋 Descripción

El sistema consta de dos servidores que trabajan de forma coordinada:

- **Servidor de Scraping (Parte A)**: Servidor HTTP asíncrono que maneja requests de scraping utilizando `asyncio`. Extrae información estructural de páginas web.
- **Servidor de Procesamiento (Parte B)**: Servidor con `multiprocessing` que ejecuta tareas CPU-intensivas como generación de screenshots, análisis de rendimiento y procesamiento de imágenes.

## 🗂️ Estructura del Repositorio

```
.
├── README.md           # Este archivo
└── TP2/                # Carpeta principal del proyecto
    ├── server_scraping.py
    ├── server_processing.py
    ├── client.py
    ├── scraper/
    ├── processor/
    ├── common/
    ├── tests/
    ├── requirements.txt
    └── README.md       # Documentación completa del proyecto
```

## 📖 Documentación

**Para instrucciones detalladas de instalación, uso y arquitectura, consulta el [README completo dentro de TP2/](./TP2/README.md)**

## 🚀 Inicio Rápido

```bash
# Clonar el repositorio
git clone https://github.com/abenavidezUM/Computacion_II_TP2.git
cd Computacion_II_TP2/TP2

# Instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Iniciar servidores
python server_processing.py -i 127.0.0.1 -p 9000
python server_scraping.py -i 127.0.0.1 -p 8000
```

## 🛠️ Tecnologías

- **asyncio**: Programación asíncrona
- **aiohttp**: Cliente/servidor HTTP asíncrono
- **multiprocessing**: Paralelismo con múltiples procesos
- **BeautifulSoup4**: Parsing HTML
- **Selenium**: Screenshots y automation
- **Pillow**: Procesamiento de imágenes

## 📊 Estado del Proyecto

- ✅ **Etapa 1**: Estructura base y configuración
- ✅ **Etapa 2**: Servidor HTTP asíncrono completo
- ✅ **Etapa 3**: Implementación de scraping con BeautifulSoup
- ✅ **Etapa 4**: Servidor de procesamiento con multiprocessing
- ✅ **Etapa 5**: Integración completa A↔B
- ✅ **Etapa 6**: Screenshots con Selenium WebDriver
- ✅ **Etapa 7**: Análisis de rendimiento web
- ✅ **Etapa 8**: Procesamiento de imágenes y thumbnails
- ✅ **Etapa 9**: Manejo de errores y robustez
- ✅ **Etapa 10**: Testing y documentación final
- 🎉 **PROYECTO COMPLETADO** (100%)

## 👤 Autor

- **Agustín Benavídez** ([@abenavidezUM](https://github.com/abenavidezUM))
- **Legajo:** 62344

## 📅 Fecha de Entrega

14 de Noviembre de 2025

---

**Universidad de Mendoza - Facultad de Ingeniería - Computación II**
