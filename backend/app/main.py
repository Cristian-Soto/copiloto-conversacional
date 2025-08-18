from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import upload, chat

app = FastAPI(
    title="Copiloto Conversacional API",
    description="API para procesamiento de PDFs con IA",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(upload.router, prefix="", tags=["upload"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Copiloto Conversacional API está funcionando"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
