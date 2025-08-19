# chat.py
# Router para endpoints de chat con documentos usando LangChain
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..services.embeddings import document_embedding_manager
from ..services.vector_store import vector_db
from ..services.retrieval import contextual_retriever
from ..services.llm_service import local_llm_service
from ..services.summarizer import document_summarizer
from ..services.topic_classifier import topic_classifier

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    max_results: int = 5
    similarity_threshold: float = 0.5

class ChatResponse(BaseModel):
    question: str
    answer: str
    relevant_documents: list
    confidence_score: float
    llm_used: str
    method: str

class SummaryRequest(BaseModel):
    document_id: Optional[str] = None
    max_length: int = 500

class AdvancedSummaryRequest(BaseModel):
    summary_type: str = "comprehensive"  # comprehensive, executive, technical, bullet_points
    document_ids: Optional[List[str]] = None
    max_tokens: int = 800

class ComparativeSummaryRequest(BaseModel):
    doc1_query: str
    doc2_query: str
    max_results: int = 3

class TopicClassificationRequest(BaseModel):
    document_ids: Optional[List[str]] = None
    custom_labels: Optional[List[str]] = None
    confidence_threshold: float = 0.3

class ComparisonRequest(BaseModel):
    doc1_query: str
    doc2_query: str
    max_results: int = 3

@router.get("/status")
async def chat_status():
    """Verifica el estado del sistema de chat."""
    try:
        # Verificar estado de LLM 
        llm_status = local_llm_service.get_llm_status()
        
        # Verificar base de datos vectorial
        vector_status = vector_db.get_database_info()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "operational",
                "llm_service": llm_status,
                "vector_database": vector_status,
                "chat_features": {
                    "contextual_search": True,
                    "langchain_integration": llm_status.get("langchain_available", False),
                    "document_summarization": True,
                    "advanced_summarization": True,
                    "comparative_analysis": True,
                    "topic_classification": True,
                    "conversation_memory": True,
                    "document_comparison": llm_status.get("langchain_available", False),
                    "summary_types": ["comprehensive", "executive", "technical", "bullet_points"],
                    "classification_methods": ["llm_local", "keyword_fallback", "huggingface_future"]
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error verificando estado del chat: {str(e)}"}
        )

@router.get("/documents")
async def list_documents():
    """Obtiene la lista de documentos procesados en el sistema."""
    try:
        # Obtener todos los documentos de muestra (aumentamos el límite)
        all_docs_sample = vector_db.get_all_documents_sample(limit=200)
        
        # Obtener estadísticas generales
        db_status = vector_db.get_database_status()
        
        # Procesar documentos únicos y calcular estadísticas
        unique_docs = {}
        fragment_counts = {}
        
        for doc in all_docs_sample:
            metadata = doc.get("metadata", {})
            filename = metadata.get("filename", "unknown")
            
            # Contar fragmentos
            fragment_counts[filename] = fragment_counts.get(filename, 0) + 1
            
            # Mantener solo un documento único por filename
            if filename not in unique_docs:
                unique_docs[filename] = {
                    "filename": filename,
                    "upload_date": metadata.get("upload_date", "Fecha no disponible"),
                    "file_size": metadata.get("file_size", 0),
                    "total_pages": metadata.get("total_pages", 0),
                    "content_preview": doc.get("content", "")[:200] + "..." if len(doc.get("content", "")) > 200 else doc.get("content", ""),
                    "fragment_count": 0  # Se actualizará después
                }
        
        # Actualizar conteos de fragmentos
        for filename, doc_info in unique_docs.items():
            doc_info["fragment_count"] = fragment_counts.get(filename, 0)
        
        # Convertir a lista y ordenar por fecha
        processed_docs = list(unique_docs.values())
        try:
            processed_docs.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
        except:
            pass  # Si hay error en el ordenamiento, continúa sin ordenar
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "documents": processed_docs,
                "total_documents": len(processed_docs),
                "total_fragments": db_status.get("total_chunks", 0),
                "database_status": db_status
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error obteniendo lista de documentos: {str(e)}",
                "documents": [],
                "total_documents": 0,
                "total_fragments": 0
            }
        )

@router.delete("/documents/{document_name}")
async def delete_document(document_name: str):
    """Elimina un documento específico y todos sus fragmentos."""
    try:
        # Intentar eliminar el documento
        success = vector_db.remove_document_by_name(document_name)
        
        if success:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Documento '{document_name}' eliminado exitosamente",
                    "document_name": document_name
                }
            )
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"No se encontró el documento '{document_name}'"
                }
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error eliminando documento: {str(e)}"
            }
        )

@router.delete("/documents")
async def clear_all_documents():
    """Elimina todos los documentos de la base de datos."""
    try:
        result = vector_db.clear_all_documents()
        
        if result.get("success", False):
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            return JSONResponse(
                status_code=500,
                content=result
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error limpiando base de datos: {str(e)}"
            }
        )

@router.get("/documents/{document_name}/fragments")
async def get_document_fragments(document_name: str):
    """Obtiene información detallada de fragmentos de un documento específico."""
    try:
        result = vector_db.get_document_fragments_info(document_name)
        
        if result.get("success", False):
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            return JSONResponse(
                status_code=404,
                content=result
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error obteniendo fragmentos: {str(e)}"
            }
        )

@router.delete("/fragments")
async def delete_fragments(fragment_ids: List[str]):
    """Elimina fragmentos específicos por sus IDs."""
    try:
        if not fragment_ids:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Se requiere una lista de IDs de fragmentos"
                }
            )
        
        result = vector_db.delete_fragments_by_ids(fragment_ids)
        
        if result.get("success", False):
            return JSONResponse(
                status_code=200,
                content=result
            )
        else:
            return JSONResponse(
                status_code=400,
                content=result
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error eliminando fragmentos: {str(e)}"
            }
        )

@router.post("/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """
    Endpoint principal para chat con documentos usando LangChain.
    Busca documentos relevantes y genera respuesta con contexto.
    """
    try:
        print(f"🔍 Chat request recibido: {request.question}")
        
        # Buscar contexto relevante
        print("📚 Buscando contexto relevante...")
        search_result = contextual_retriever.search_relevant_context(
            query=request.question,
            max_results=request.max_results,
            similarity_threshold=request.similarity_threshold
        )
        
        print(f"🔎 Resultado de búsqueda: {search_result.get('success', False)}")
        
        if not search_result["success"]:
            print(f"❌ Error en búsqueda: {search_result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=500, detail=search_result["error"])
        
        context_fragments = search_result.get("relevant_fragments", [])
        print(f"📄 Fragmentos encontrados: {len(context_fragments)}")
        
        if not context_fragments:
            print("⚠️ No se encontraron fragmentos relevantes")
            return ChatResponse(
                question=request.question,
                answer="No encontré información relevante en los documentos cargados para responder tu pregunta.",
                relevant_documents=[],
                confidence_score=0.0,
                llm_used="none",
                method="no_context_found"
            )
        
        # Generar respuesta con LLM (LangChain o Ollama directo)
        print("🤖 Generando respuesta con LLM...")
        llm_response = local_llm_service.generate_contextual_response(
            question=request.question,
            context_fragments=context_fragments
        )
        
        print(f"✅ Respuesta LLM generada: {llm_response.get('method', 'unknown')}")
        
        # Preparar información de documentos relevantes
        relevant_docs = []
        for fragment in context_fragments:
            doc_info = {
                "filename": fragment.get("metadata", {}).get("filename", "documento_desconocido"),
                "similarity_score": fragment.get("similarity_score", 0.0),
                "content_preview": fragment.get("content", "")[:200] + "..." if len(fragment.get("content", "")) > 200 else fragment.get("content", ""),
                "page": fragment.get("metadata", {}).get("page", None)
            }
            relevant_docs.append(doc_info)
        
        # Calcular confidence score basado en similaridad promedio
        if context_fragments:
            avg_similarity = sum(f.get("similarity_score", 0) for f in context_fragments) / len(context_fragments)
            confidence_score = min(avg_similarity * 1.2, 1.0)  # Boost ligeramente
        else:
            confidence_score = 0.0
        
        return ChatResponse(
            question=request.question,
            answer=llm_response.get("response", "No se pudo generar respuesta"),
            relevant_documents=relevant_docs,
            confidence_score=confidence_score,
            llm_used=llm_response.get("model_used", "unknown"),
            method=llm_response.get("method", "unknown")
        )
        
    except Exception as e:
        print(f"💥 Error en chat: {str(e)}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error en chat: {str(e)}")

@router.post("/chat/simple")
async def simple_chat(request: ChatRequest):
    """
    Endpoint simplificado que retorna respuesta directa sin modelo específico.
    Mantiene compatibilidad con frontend existente.
    """
    try:
        # Buscar contexto
        search_result = contextual_retriever.search_relevant_context(
            query=request.question,
            max_results=request.max_results,
            similarity_threshold=request.similarity_threshold
        )
        
        if not search_result["success"] or not search_result.get("relevant_fragments"):
            return {
                "response": "No encontré información relevante en los documentos para responder tu pregunta.",
                "relevant_documents": [],
                "method": "no_context"
            }
        
        # Generar respuesta
        llm_response = local_llm_service.generate_contextual_response(
            question=request.question,
            context_fragments=search_result["relevant_fragments"]
        )
        
        return {
            "response": llm_response.get("response", "Error generando respuesta"),
            "relevant_documents": len(search_result["relevant_fragments"]),
            "method": llm_response.get("method", "unknown"),
            "langchain_used": llm_response.get("method", "").startswith("langchain")
        }
        
    except Exception as e:
        return {"error": f"Error en chat simple: {str(e)}"}

@router.post("/summarize")
async def summarize_document(request: SummaryRequest):
    """
    Genera resumen de un documento específico o de toda la colección.
    """
    try:
        if request.document_id:
            # Resumir documento específico
            # TODO: Implementar búsqueda por ID de documento
            return {"error": "Resumen por ID de documento no implementado aún"}
        else:
            # Resumir colección completa
            # Obtener muestra de documentos
            all_docs = vector_db.get_all_documents_sample(limit=10)
            
            if not all_docs:
                return {"error": "No hay documentos para resumir"}
            
            # Combinar contenido para resumen
            combined_content = "\n\n".join([doc.get("content", "") for doc in all_docs])
            
            # Generar resumen con LLM
            summary_result = local_llm_service.generate_document_summary(combined_content)
            
            return {
                "summary": summary_result.get("summary", "No se pudo generar resumen"),
                "documents_analyzed": len(all_docs),
                "success": summary_result.get("success", False),
                "method": summary_result.get("method", "unknown")
            }
            
    except Exception as e:
        return {"error": f"Error generando resumen: {str(e)}"}

@router.post("/compare")
async def compare_documents(request: ComparisonRequest):
    """
    Compara dos conjuntos de documentos basándose en consultas.
    """
    try:
        # Buscar documentos para la primera consulta
        search1 = contextual_retriever.search_relevant_context(
            query=request.doc1_query,
            max_results=request.max_results,
            similarity_threshold=0.5
        )
        
        # Buscar documentos para la segunda consulta
        search2 = contextual_retriever.search_relevant_context(
            query=request.doc2_query,
            max_results=request.max_results,
            similarity_threshold=0.5
        )
        
        if not search1["success"] or not search2["success"]:
            return {"error": "Error en búsqueda de documentos"}
        
        # Combinar contenido de cada grupo
        content1 = "\n\n".join([
            f"[{frag.get('metadata', {}).get('filename', 'doc')}] {frag.get('content', '')[:500]}"
            for frag in search1.get("relevant_fragments", [])
        ])
        
        content2 = "\n\n".join([
            f"[{frag.get('metadata', {}).get('filename', 'doc')}] {frag.get('content', '')[:500]}"
            for frag in search2.get("relevant_fragments", [])
        ])
        
        if not content1 or not content2:
            return {"error": "No se encontró suficiente contenido para comparar"}
        
        # Generar comparación usando LLM
        comparison_result = local_llm_service.compare_documents(content1, content2)
        
        return {
            "comparison": comparison_result.get("comparison", "No se pudo generar comparación"),
            "success": comparison_result.get("success", False),
            "method": comparison_result.get("method", "unknown"),
            "doc1_fragments": len(search1.get("relevant_fragments", [])),
            "doc2_fragments": len(search2.get("relevant_fragments", [])),
            "queries": {
                "doc1_query": request.doc1_query,
                "doc2_query": request.doc2_query
            }
        }
        
    except Exception as e:
        return {"error": f"Error en comparación: {str(e)}"}

@router.post("/summarize/advanced")
async def advanced_document_summary(request: AdvancedSummaryRequest):
    """
    Genera resumen avanzado con múltiples tipos y opciones.
    Tipos disponibles: comprehensive, executive, technical, bullet_points
    """
    try:
        if request.document_ids:
            # Resumen de documentos específicos
            result = document_summarizer.generate_multi_document_summary(
                document_ids=request.document_ids,
                summary_type=request.summary_type
            )
        else:
            # Resumen de toda la colección
            result = document_summarizer.generate_multi_document_summary(
                document_ids=None,
                summary_type=request.summary_type
            )
        
        return {
            "success": result.get("success", False),
            "summary": result.get("summary", "No se pudo generar resumen"),
            "summary_type": result.get("summary_type", request.summary_type),
            "method": result.get("method", "unknown"),
            "documents_processed": result.get("documents_processed", 0),
            "model_used": result.get("model_used", "unknown"),
            "tokens_used": result.get("tokens_used", 0),
            "error": result.get("error", None)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generando resumen avanzado: {str(e)}",
            "summary_type": request.summary_type
        }

@router.post("/summarize/comparative")
async def comparative_document_summary(request: ComparativeSummaryRequest):
    """
    Genera resumen comparativo entre dos conjuntos de documentos.
    """
    try:
        # Buscar documentos para cada consulta
        search1 = contextual_retriever.search_relevant_context(
            query=request.doc1_query,
            max_results=request.max_results,
            similarity_threshold=0.5
        )
        
        search2 = contextual_retriever.search_relevant_context(
            query=request.doc2_query,
            max_results=request.max_results,
            similarity_threshold=0.5
        )
        
        if not search1["success"] or not search2["success"]:
            return {
                "success": False,
                "error": "Error en búsqueda de documentos para comparación"
            }
        
        # Combinar contenido de cada grupo
        content1 = "\n\n".join([
            frag.get("content", "")[:1000] for frag in search1.get("relevant_fragments", [])
        ])
        
        content2 = "\n\n".join([
            frag.get("content", "")[:1000] for frag in search2.get("relevant_fragments", [])
        ])
        
        if not content1 or not content2:
            return {
                "success": False,
                "error": "No se encontró suficiente contenido para comparar"
            }
        
        # Generar resumen comparativo
        result = document_summarizer.generate_comparative_summary(content1, content2)
        
        return {
            "success": result.get("success", False),
            "comparative_summary": result.get("summary", "No se pudo generar comparación"),
            "method": result.get("method", "unknown"),
            "doc1_fragments": len(search1.get("relevant_fragments", [])),
            "doc2_fragments": len(search2.get("relevant_fragments", [])),
            "queries": {
                "doc1_query": request.doc1_query,
                "doc2_query": request.doc2_query
            },
            "documents_compared": result.get("documents_compared", 2),
            "error": result.get("error", None)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error en resumen comparativo: {str(e)}"
        }

@router.get("/summarize/types")
async def get_summary_types():
    """
    Retorna los tipos de resumen disponibles y sus descripciones.
    """
    return {
        "summary_types": {
            "comprehensive": {
                "name": "Completo",
                "description": "Resumen detallado con estructura completa: ejecutivo, puntos clave, metodología, evidencia y conclusiones",
                "recommended_for": "Análisis profundo de documentos técnicos o académicos"
            },
            "executive": {
                "name": "Ejecutivo",
                "description": "Resumen conciso para directivos: problema, hallazgos, conclusiones y recomendaciones",
                "recommended_for": "Presentaciones gerenciales y toma de decisiones"
            },
            "technical": {
                "name": "Técnico",
                "description": "Enfoque en aspectos técnicos: metodologías, herramientas, datos y consideraciones técnicas",
                "recommended_for": "Equipos técnicos y desarrolladores"
            },
            "bullet_points": {
                "name": "Puntos Clave",
                "description": "Lista de puntos principales en formato de viñetas para fácil lectura",
                "recommended_for": "Revisión rápida y referencias"
            }
        },
        "features": {
            "llm_powered": "Usa Llama local cuando está disponible",
            "fallback_support": "Resumen extractivo cuando no hay LLM",
            "multi_document": "Puede resumir múltiples documentos",
            "comparative": "Análisis comparativo entre conjuntos de documentos"
        }
    }

@router.post("/classify/topics")
async def classify_document_topics(request: TopicClassificationRequest):
    """
    Clasifica documentos por temas usando zero-shot classification.
    """
    try:
        result = topic_classifier.classify_document_collection(
            document_ids=request.document_ids,
            custom_labels=request.custom_labels
        )
        
        if result.get("success", False):
            # Generar insights adicionales
            insights = topic_classifier.get_topic_insights(result)
            
            return {
                "success": True,
                "classification_results": result,
                "insights": insights.get("insights", {}),
                "total_documents": result.get("total_documents", 0),
                "topic_statistics": result.get("topic_statistics", {}),
                "dominant_topics": result.get("dominant_topics", []),
                "method": result.get("method", "unknown")
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Error desconocido en clasificación")
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error en clasificación de temas: {str(e)}"
        }

@router.get("/classify/labels")
async def get_available_labels():
    """
    Retorna las etiquetas de clasificación disponibles y sugerencias.
    """
    return {
        "default_labels": topic_classifier.default_labels,
        "label_categories": {
            "business": ["negocios", "marketing", "finanzas", "recursos humanos", "estrategia"],
            "technology": ["tecnología", "programación", "software", "inteligencia artificial", "datos"],
            "science": ["ciencia", "investigación", "medicina", "biología", "física"],
            "social": ["educación", "política", "sociedad", "cultura", "arte"],
            "general": ["noticias", "entretenimiento", "deportes", "viajes", "estilo de vida"]
        },
        "custom_label_tips": [
            "Use etiquetas específicas para mejor precisión",
            "Máximo 15 etiquetas recomendado",
            "Evite etiquetas muy similares",
            "Use términos en español para mejor coincidencia"
        ],
        "classification_methods": {
            "primary": "LLM local (Llama) cuando disponible",
            "fallback": "Clasificación por palabras clave",
            "future": "HuggingFace zero-shot classification (en desarrollo)"
        }
    }

@router.post("/classify/single")
async def classify_single_document(
    content: str,
    custom_labels: Optional[List[str]] = None,
    confidence_threshold: float = 0.3
):
    """
    Clasifica un documento individual por contenido directo.
    """
    try:
        if not content.strip():
            return {
                "success": False,
                "error": "Contenido vacío para clasificar"
            }
        
        result = topic_classifier.classify_document(
            content=content,
            custom_labels=custom_labels,
            confidence_threshold=confidence_threshold
        )
        
        return {
            "success": result.get("success", False),
            "primary_topic": result.get("primary_topic", "unknown"),
            "confidence": result.get("confidence", 0.0),
            "reason": result.get("reason", ""),
            "scores": result.get("scores", {}),
            "method": result.get("method", "unknown"),
            "content_length": len(content),
            "labels_used": custom_labels or topic_classifier.default_labels,
            "error": result.get("error", None)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error clasificando documento: {str(e)}"
        }

@router.delete("/conversation/clear")
async def clear_conversation():
    """Limpia la memoria de conversación de LangChain."""
    try:
        local_llm_service.clear_conversation_memory()
        return {"message": "Memoria de conversación limpiada exitosamente"}
    except Exception as e:
        return {"error": f"Error limpiando conversación: {str(e)}"}

@router.get("/health")
async def health_check():
    """Health check específico para el servicio de chat."""
    return {
        "status": "healthy",
        "service": "chat_router",
        "langchain_available": local_llm_service.langchain_available,
        "summarizer_available": True,
        "topic_classifier_available": True,
        "endpoints": [
            "/chat",
            "/chat/simple", 
            "/summarize",
            "/summarize/advanced",
            "/summarize/comparative", 
            "/summarize/types",
            "/classify/topics",
            "/classify/labels",
            "/classify/single",
            "/compare",
            "/conversation/clear",
            "/status",
            "/health"
        ]
    }
