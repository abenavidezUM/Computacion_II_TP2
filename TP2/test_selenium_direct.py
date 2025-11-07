#!/usr/bin/env python3
"""
Test directo de Selenium sin pasar por servidores.
"""

import sys
sys.path.insert(0, '/Users/agus/Documents/Facultad/Computacion_II/TP2/TP2')

from processor.screenshot import generate_screenshot_with_options
import base64

print("=" * 70)
print("TEST DIRECTO DE SELENIUM")
print("=" * 70)
print("\nEste test puede tardar 30-60s la primera vez...")
print("(Selenium descarga ChromeDriver automáticamente)\n")

url = "https://example.com"
print(f"Capturando screenshot de: {url}")

screenshot_b64 = generate_screenshot_with_options(
    url,
    width=1280,
    height=720,
    full_page=True,
    timeout=30
)

if screenshot_b64:
    size_kb = len(screenshot_b64) / 1024
    print(f"\n✅ Screenshot capturado exitosamente!")
    print(f"   Tamaño: {size_kb:.2f} KB (base64)")
    
    # Guardar
    screenshot_bytes = base64.b64decode(screenshot_b64)
    filepath = '/tmp/test_direct_selenium.png'
    with open(filepath, 'wb') as f:
        f.write(screenshot_bytes)
    print(f"   Guardado en: {filepath}")
    print(f"\nPuedes verificar el screenshot con: open {filepath}")
    sys.exit(0)
else:
    print("\n❌ Fallo al capturar screenshot")
    sys.exit(1)

