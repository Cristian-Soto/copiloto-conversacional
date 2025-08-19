# 🗑️ Guía de Eliminación de Documentos y Fragmentos

## Funcionalidades Implementadas

### 1. Eliminación de Documentos Individuales
**Ubicación**: Página "📄 Documentos" → Expandir documento → Botón "❌ Eliminar"

**Qué hace**:
- Elimina un documento específico y TODOS sus fragmentos
- Requiere confirmación antes de eliminar
- Actualiza automáticamente la lista después de eliminar

**Uso**:
1. Ve a la página "📄 Documentos"
2. Encuentra el documento que quieres eliminar
3. Haz clic en "❌ Eliminar"
4. Confirma con "✅ Sí, eliminar"

### 2. Limpieza Completa de la Base de Datos
**Ubicación**: Página "📄 Documentos" → Sección "🛠️ Administración de Base de Datos" → Botón "🗑️ Limpiar todo"

**Qué hace**:
- Elimina TODOS los documentos y fragmentos
- ⚠️ **ACCIÓN IRREVERSIBLE**
- Requiere doble confirmación

**Uso**:
1. Ve a la página "📄 Documentos"
2. Desplázate hasta "🛠️ Administración de Base de Datos"
3. Haz clic en "🗑️ Limpiar todo"
4. Lee la advertencia cuidadosamente
5. Confirma con "💀 SÍ, ELIMINAR TODO"

### 3. Vista Detallada de Fragmentos
**Ubicación**: Página "📄 Documentos" → Sección "🛠️ Administración de Base de Datos" → Botón "📊 Ver fragmentos"

**Qué hace**:
- Muestra todos los fragmentos de un documento específico
- Permite eliminar fragmentos individuales
- Muestra contenido y metadatos de cada fragmento

**Uso**:
1. Ve a la página "📄 Documentos"
2. Haz clic en "📊 Ver fragmentos"
3. Selecciona un documento del dropdown
4. Haz clic en "🔍 Ver fragmentos"
5. Opcionalmente, elimina fragmentos individuales

### 4. Eliminación de Fragmentos Específicos
**Ubicación**: Vista detallada de fragmentos → Botón "🗑️ Eliminar fragmento"

**Qué hace**:
- Elimina un fragmento específico por su ID
- Útil para limpiar contenido problemático
- No afecta otros fragmentos del mismo documento

## Endpoints de API Implementados

### Backend (Para desarrolladores)

```bash
# Listar todos los documentos
GET /api/chat/documents

# Obtener fragmentos de un documento específico
GET /api/chat/documents/{document_name}/fragments

# Eliminar un documento específico
DELETE /api/chat/documents/{document_name}

# Limpiar toda la base de datos
DELETE /api/chat/documents

# Eliminar fragmentos específicos por ID
DELETE /api/chat/fragments
```

## Ejemplos de Uso con curl

```bash
# Ver documentos disponibles
curl -X GET "http://localhost:8000/api/chat/documents"

# Ver fragmentos de un documento
curl -X GET "http://localhost:8000/api/chat/documents/mi_documento.pdf/fragments"

# Eliminar un documento específico
curl -X DELETE "http://localhost:8000/api/chat/documents/mi_documento.pdf"

# Limpiar toda la base de datos
curl -X DELETE "http://localhost:8000/api/chat/documents"

# Eliminar fragmentos específicos
curl -X DELETE "http://localhost:8000/api/chat/fragments" \
  -H "Content-Type: application/json" \
  -d '["fragment-id-1", "fragment-id-2"]'
```

## Precauciones de Seguridad

⚠️ **IMPORTANTE**: 
- La eliminación de documentos es **IRREVERSIBLE**
- Siempre haz backup de documentos importantes antes de eliminar
- La función "Limpiar todo" elimina TODA la base de datos
- Los fragmentos eliminados no se pueden recuperar

## Casos de Uso Comunes

### 🧹 Limpieza de Documentos Obsoletos
- Elimina versiones antiguas de documentos actualizados
- Remueve documentos de prueba

### 🔧 Resolución de Problemas
- Elimina documentos que no se procesaron correctamente
- Limpia fragmentos duplicados o corruptos

### 📊 Gestión de Espacio
- Elimina documentos grandes que consumen mucho espacio
- Mantén solo los documentos más relevantes

### 🚀 Reinicio Completo
- Limpia toda la base para empezar desde cero
- Útil en desarrollo y testing

## Estado Actual del Sistema

Después de las pruebas:
- ✅ Eliminación individual funcional
- ✅ Limpieza completa implementada  
- ✅ Vista de fragmentos operativa
- ✅ Eliminación de fragmentos específicos
- ✅ Interfaz web intuitiva
- ✅ Confirmaciones de seguridad

## Próximas Mejoras Sugeridas

- 🔄 Función de respaldo antes de eliminar
- 📈 Estadísticas de uso de fragmentos
- 🏷️ Etiquetado de documentos para eliminación en lote
- 📅 Eliminación automática de documentos antiguos
- 🔍 Búsqueda y filtrado avanzado antes de eliminar
