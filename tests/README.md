# 🧪 Tests Básicos para Demostración

## Tests de Integración Mínimos

```python
# test_basic.py
import requests
import pytest

def test_health_check():
    """Verifica que el sistema esté operativo"""
    response = requests.get("http://localhost:8000/api/chat/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_summary_types():
    """Verifica que los tipos de resumen estén disponibles"""
    response = requests.get("http://localhost:8000/api/chat/summarize/types")
    assert response.status_code == 200
    data = response.json()
    assert "comprehensive" in data["summary_types"]
    assert "executive" in data["summary_types"]

def test_classification_labels():
    """Verifica que las etiquetas de clasificación estén disponibles"""
    response = requests.get("http://localhost:8000/api/chat/classify/labels")
    assert response.status_code == 200
    data = response.json()
    assert len(data["default_labels"]) >= 10
```

## Comandos de Testing

```bash
# Instalar pytest
pip install pytest requests

# Ejecutar tests básicos
pytest test_basic.py -v

# Con coverage
pip install pytest-cov
pytest test_basic.py --cov=app
```
