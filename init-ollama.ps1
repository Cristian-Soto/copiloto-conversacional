# Script de inicialización de Ollama para Windows
# Este script configura Ollama con los modelos necesarios

Write-Host "🚀 Deteniendo servicios existentes..." -ForegroundColor Yellow
docker-compose down

Write-Host "🔄 Iniciando servicios (esto puede tomar unos minutos)..." -ForegroundColor Green
docker-compose up -d

Write-Host "⏳ Esperando a que Ollama esté listo..." -ForegroundColor Blue
Start-Sleep -Seconds 20

Write-Host "🔍 Verificando estado de Ollama..." -ForegroundColor Cyan
$maxRetries = 10
$retryCount = 0

do {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method GET -TimeoutSec 5
        Write-Host "✅ Ollama está respondiendo!" -ForegroundColor Green
        break
    catch {
        $retryCount++
        Write-Host "⏳ Intento $retryCount/$maxRetries - Esperando a Ollama..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
} while ($retryCount -lt $maxRetries)

if ($retryCount -eq $maxRetries) {
    Write-Host "❌ Error: Ollama no responde después de $maxRetries intentos" -ForegroundColor Red
    Write-Host "🔧 Verifica los logs: docker-compose logs ollama" -ForegroundColor Yellow
    exit 1
}

Write-Host "📥 Descargando Llama 3.2:3b (modelo ligero y rápido)..." -ForegroundColor Blue
Write-Host "   Esto puede tomar 5-10 minutos dependiendo de tu conexión..." -ForegroundColor Gray
docker-compose exec ollama ollama pull llama3.2:3b

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Llama 3.2:3b descargado correctamente!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Error descargando Llama 3.2:3b, intentando con modelo alternativo..." -ForegroundColor Yellow
    docker-compose exec ollama ollama pull llama3:8b
}

Write-Host "🧪 Probando conexión con el modelo..." -ForegroundColor Magenta
$testResponse = docker-compose exec ollama ollama run llama3.2:3b "Responde solo: CONEXION OK"

if ($testResponse -like "*CONEXION OK*") {
    Write-Host "✅ ¡IA local configurada correctamente!" -ForegroundColor Green
} else {
    Write-Host "⚠️ El modelo se descargó pero hay problemas en la respuesta" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 ¡Configuración completada!" -ForegroundColor Green
Write-Host "📱 Servicios disponibles:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend: http://localhost:8501" -ForegroundColor White
Write-Host "   🔧 Backend: http://localhost:8000" -ForegroundColor White  
Write-Host "   🤖 Ollama: http://localhost:11434" -ForegroundColor White
Write-Host "   🗄️ ChromaDB: http://localhost:8001" -ForegroundColor White
Write-Host ""
Write-Host "💡 Ahora puedes usar el copiloto con IA local!" -ForegroundColor Yellow
Write-Host "   Ve a http://localhost:8501 y verás 'IA Local Activa'" -ForegroundColor Gray
