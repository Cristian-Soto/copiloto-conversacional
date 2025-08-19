# Script para inicializar Ollama
Write-Host "Iniciando configuracion de Ollama..." -ForegroundColor Green

# Detener servicios existentes
Write-Host "Deteniendo servicios existentes..." -ForegroundColor Yellow
docker-compose down

# Iniciar servicios con Ollama
Write-Host "Iniciando servicios con Ollama..." -ForegroundColor Blue
docker-compose up -d

# Esperar a que Ollama este listo
Write-Host "Esperando 30 segundos para que Ollama este listo..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Descargar modelo
Write-Host "Descargando modelo Llama 3.2:3b..." -ForegroundColor Magenta
Write-Host "Esto puede tomar 5-10 minutos" -ForegroundColor Gray
docker-compose exec ollama ollama pull llama3.2:3b

Write-Host "Configuracion completada!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:8501" -ForegroundColor White
Write-Host "Ollama: http://localhost:11434" -ForegroundColor White
