#!/usr/bin/env python3
"""
Test directo del análisis de performance.
"""

import sys
sys.path.insert(0, '/Users/agus/Documents/Facultad/Computacion_II/TP2/TP2')

from processor.performance import analyze_performance
import json

print("=" * 70)
print("TEST DIRECTO DE PERFORMANCE")
print("=" * 70)
print("\nEste test puede tardar 30-60s...")
print("(Selenium descarga ChromeDriver y analiza la página)\n")

url = "https://example.com"
print(f"Analizando performance de: {url}")

try:
    metrics = analyze_performance(url, timeout=30)
    
    if metrics:
        print(f"\n✅ Análisis completado!")
        print(f"\nMétricas:")
        print(json.dumps(metrics, indent=2))
        sys.exit(0)
    else:
        print("\n❌ El análisis retornó None")
        sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

