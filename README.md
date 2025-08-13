# Copiloto Conversacional

## Estructura del proyecto

```
copiloto-conversacional/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── upload.py
│   │   │   ├── chat.py
│   │   ├── services/
│   │   │   ├── pdf_processing.py
│   │   │   ├── embeddings.py
│   │   │   ├── retrieval.py
│   │   │   ├── summarizer.py
│   │   │   ├── comparator.py
│   │   ├── models/
│   │   │   ├── request_models.py
│   │   │   ├── response_models.py
│   ├── requirements.txt
│   ├── Dockerfile
│
├── frontend/
│   ├── streamlit_app.py
│   ├── components/
│   ├── requirements.txt
│   ├── Dockerfile
│
├── docker-compose.yml
├── README.md
├── .env.example
└── tests/
```

## Descripción
- **backend/**: API con FastAPI y servicios de procesamiento.
- **frontend/**: Aplicación Streamlit para la interfaz de usuario.
- **docker-compose.yml**: Orquestación de contenedores.
- **.env.example**: Variables de entorno de ejemplo.
- **tests/**: Pruebas del proyecto.