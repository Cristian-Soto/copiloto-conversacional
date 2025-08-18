# topic_classifier.py
# Servicio de clasificación de temas usando HuggingFace zero-shot classification
import requests
import json
from typing import List, Dict, Any, Optional
from .vector_store import vector_db
from .llm_service import local_llm_service

class TopicClassifier:
    def __init__(self):
        """Inicializa el clasificador de temas."""
        self.default_labels = [
            "tecnología", "ciencia", "negocios", "salud", "educación",
            "política", "deportes", "entretenimiento", "finanzas", "investigación",
            "marketing", "recursos humanos", "legal", "medio ambiente", "arte"
        ]
        self.huggingface_available = False
        self.check_huggingface_availability()
    
    def check_huggingface_availability(self):
        """Verifica si HuggingFace API está disponible."""
        try:
            # TODO: Implementar verificación de API de HuggingFace
            # Por ahora usar clasificación local
            self.huggingface_available = False
        except Exception:
            self.huggingface_available = False
    
    def classify_document(self, content: str, custom_labels: Optional[List[str]] = None, 
                         confidence_threshold: float = 0.3) -> Dict[str, Any]:
        """
        Clasifica un documento en categorías temáticas.
        
        Args:
            content (str): Contenido del documento
            custom_labels (List[str]): Etiquetas personalizadas (opcional)
            confidence_threshold (float): Umbral mínimo de confianza
            
        Returns:
            Dict[str, Any]: Resultado de clasificación
        """
        try:
            labels = custom_labels if custom_labels else self.default_labels
            
            if self.huggingface_available:
                return self._classify_with_huggingface(content, labels, confidence_threshold)
            else:
                return self._classify_with_local_llm(content, labels, confidence_threshold)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "classification": "unknown"
            }
    
    def classify_document_collection(self, document_ids: Optional[List[str]] = None,
                                   custom_labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Clasifica una colección de documentos y genera estadísticas.
        
        Args:
            document_ids (List[str]): IDs específicos (opcional, None para todos)
            custom_labels (List[str]): Etiquetas personalizadas (opcional)
            
        Returns:
            Dict[str, Any]: Estadísticas de clasificación
        """
        try:
            # Obtener documentos
            if document_ids:
                documents = self._get_documents_by_ids(document_ids)
            else:
                documents_sample = vector_db.get_all_documents_sample(limit=20)
                documents = [{"content": doc.get("content", ""), 
                            "filename": doc.get("metadata", {}).get("filename", f"doc_{i}")}
                           for i, doc in enumerate(documents_sample)]
            
            if not documents:
                return {
                    "success": False,
                    "error": "No se encontraron documentos para clasificar"
                }
            
            labels = custom_labels if custom_labels else self.default_labels
            classifications = []
            topic_stats = {label: 0 for label in labels}
            topic_stats["unknown"] = 0
            
            # Clasificar cada documento
            for i, doc in enumerate(documents):
                content = doc.get("content", "")[:2000]  # Limitar contenido
                
                classification_result = self.classify_document(content, labels)
                
                if classification_result.get("success", False):
                    primary_topic = classification_result.get("primary_topic", "unknown")
                    confidence = classification_result.get("confidence", 0.0)
                    
                    classifications.append({
                        "document": doc.get("filename", f"documento_{i+1}"),
                        "primary_topic": primary_topic,
                        "confidence": confidence,
                        "all_scores": classification_result.get("scores", {})
                    })
                    
                    # Actualizar estadísticas
                    if primary_topic in topic_stats:
                        topic_stats[primary_topic] += 1
                    else:
                        topic_stats["unknown"] += 1
                else:
                    classifications.append({
                        "document": doc.get("filename", f"documento_{i+1}"),
                        "primary_topic": "unknown",
                        "confidence": 0.0,
                        "error": classification_result.get("error", "Error desconocido")
                    })
                    topic_stats["unknown"] += 1
            
            # Calcular estadísticas finales
            total_docs = len(documents)
            topic_percentages = {
                topic: (count / total_docs) * 100 
                for topic, count in topic_stats.items()
            }
            
            # Encontrar temas dominantes
            sorted_topics = sorted(topic_stats.items(), key=lambda x: x[1], reverse=True)
            dominant_topics = [(topic, count) for topic, count in sorted_topics if count > 0][:5]
            
            return {
                "success": True,
                "total_documents": total_docs,
                "classifications": classifications,
                "topic_statistics": topic_stats,
                "topic_percentages": topic_percentages,
                "dominant_topics": dominant_topics,
                "labels_used": labels,
                "method": "local_llm" if not self.huggingface_available else "huggingface"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_topic_insights(self, classification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera insights adicionales sobre la clasificación de temas.
        
        Args:
            classification_result: Resultado de classify_document_collection
            
        Returns:
            Dict[str, Any]: Insights y recomendaciones
        """
        try:
            if not classification_result.get("success", False):
                return {"error": "Resultado de clasificación inválido"}
            
            topic_stats = classification_result.get("topic_statistics", {})
            total_docs = classification_result.get("total_documents", 0)
            dominant_topics = classification_result.get("dominant_topics", [])
            
            insights = {
                "collection_profile": {},
                "diversity_analysis": {},
                "recommendations": []
            }
            
            # Perfil de la colección
            if dominant_topics:
                primary_topic = dominant_topics[0][0]
                primary_percentage = (dominant_topics[0][1] / total_docs) * 100
                
                insights["collection_profile"] = {
                    "primary_focus": primary_topic,
                    "focus_percentage": round(primary_percentage, 1),
                    "is_specialized": primary_percentage > 50,
                    "is_diverse": len([t for t in dominant_topics if t[1] > 0]) >= 5
                }
            
            # Análisis de diversidad
            non_zero_topics = len([count for count in topic_stats.values() if count > 0])
            diversity_score = non_zero_topics / len(topic_stats) * 100
            
            insights["diversity_analysis"] = {
                "topics_present": non_zero_topics,
                "diversity_score": round(diversity_score, 1),
                "classification": self._get_diversity_classification(diversity_score)
            }
            
            # Recomendaciones
            recommendations = []
            
            if primary_percentage > 70:
                recommendations.append("Colección muy especializada - considere diversificar temas")
            elif primary_percentage < 20:
                recommendations.append("Colección muy diversa - puede beneficiarse de organización temática")
            
            if topic_stats.get("unknown", 0) > total_docs * 0.3:
                recommendations.append("Alto porcentaje de documentos sin clasificar - revise contenido o ajuste etiquetas")
            
            if non_zero_topics >= 8:
                recommendations.append("Buena diversidad temática - ideal para análisis comparativo")
            
            insights["recommendations"] = recommendations
            
            return {
                "success": True,
                "insights": insights,
                "generated_at": "timestamp_placeholder"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _classify_with_huggingface(self, content: str, labels: List[str], 
                                 confidence_threshold: float) -> Dict[str, Any]:
        """Clasifica usando HuggingFace API (placeholder para implementación futura)."""
        # TODO: Implementar integración con HuggingFace zero-shot classification
        return {
            "success": False,
            "error": "HuggingFace API no implementada aún",
            "method": "huggingface_placeholder"
        }
    
    def _classify_with_local_llm(self, content: str, labels: List[str], 
                               confidence_threshold: float) -> Dict[str, Any]:
        """Clasifica usando LLM local como alternativa."""
        try:
            # Preparar prompt de clasificación
            labels_str = ", ".join(labels)
            prompt = f"""Clasifica el siguiente texto en una de estas categorías: {labels_str}

TEXTO A CLASIFICAR:
{content[:1500]}

Instrucciones:
1. Lee el texto cuidadosamente
2. Determina cuál categoría describe mejor el contenido principal
3. Asigna una puntuación de confianza (0.0 a 1.0)
4. Si ninguna categoría encaja bien, usa "unknown"

Responde SOLO con el formato:
CATEGORÍA: [categoría]
CONFIANZA: [0.0-1.0]
RAZÓN: [breve explicación]

CLASIFICACIÓN:"""

            # Usar LLM local para clasificación
            llm_response = local_llm_service.generate_contextual_response(
                question="Clasifica este contenido según las categorías proporcionadas",
                context_fragments=[{"content": prompt}],
                max_tokens=200
            )
            
            if llm_response.get("success", False):
                response_text = llm_response.get("response", "")
                return self._parse_llm_classification(response_text, labels, confidence_threshold)
            else:
                return self._fallback_keyword_classification(content, labels)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "local_llm_error"
            }
    
    def _parse_llm_classification(self, response: str, labels: List[str], 
                                confidence_threshold: float) -> Dict[str, Any]:
        """Parsea la respuesta del LLM para extraer clasificación."""
        try:
            lines = response.strip().split('\n')
            category = "unknown"
            confidence = 0.0
            reason = "No se pudo determinar"
            
            for line in lines:
                if line.startswith("CATEGORÍA:"):
                    category = line.split(":", 1)[1].strip().lower()
                elif line.startswith("CONFIANZA:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                    except:
                        confidence = 0.5
                elif line.startswith("RAZÓN:"):
                    reason = line.split(":", 1)[1].strip()
            
            # Validar categoría
            if category not in [label.lower() for label in labels]:
                category = "unknown"
                confidence = 0.0
            
            # Aplicar umbral de confianza
            if confidence < confidence_threshold:
                category = "unknown"
            
            # Crear scores simulados
            scores = {label: 0.1 for label in labels}
            if category in [label.lower() for label in labels]:
                matching_label = next(label for label in labels if label.lower() == category)
                scores[matching_label] = confidence
            
            return {
                "success": True,
                "primary_topic": category,
                "confidence": confidence,
                "reason": reason,
                "scores": scores,
                "method": "local_llm_parsed"
            }
            
        except Exception as e:
            return self._fallback_keyword_classification(response, labels)
    
    def _fallback_keyword_classification(self, content: str, labels: List[str]) -> Dict[str, Any]:
        """Clasificación básica por palabras clave cuando no hay LLM."""
        try:
            content_lower = content.lower()
            keyword_matches = {label: 0 for label in labels}
            
            # Palabras clave básicas por categoría
            keyword_map = {
                "tecnología": ["software", "tecnología", "programación", "código", "sistema", "digital", "tech"],
                "ciencia": ["investigación", "estudio", "científico", "experimento", "análisis", "datos"],
                "negocios": ["empresa", "negocio", "mercado", "cliente", "venta", "estrategia", "business"],
                "salud": ["salud", "médico", "tratamiento", "paciente", "enfermedad", "hospital"],
                "educación": ["educación", "estudiante", "enseñanza", "aprendizaje", "curso", "escuela"],
                "finanzas": ["dinero", "financiero", "banco", "inversión", "costo", "precio", "economic"]
            }
            
            # Contar coincidencias
            for label in labels:
                label_lower = label.lower()
                if label_lower in keyword_map:
                    keywords = keyword_map[label_lower]
                    for keyword in keywords:
                        keyword_matches[label] += content_lower.count(keyword)
            
            # Encontrar mejor coincidencia
            best_match = max(keyword_matches.items(), key=lambda x: x[1])
            best_label, best_count = best_match
            
            if best_count > 0:
                confidence = min(best_count * 0.2, 0.8)  # Score conservador
                return {
                    "success": True,
                    "primary_topic": best_label.lower(),
                    "confidence": confidence,
                    "reason": f"Coincidencias de palabras clave: {best_count}",
                    "scores": {label: count * 0.1 for label, count in keyword_matches.items()},
                    "method": "keyword_fallback"
                }
            else:
                return {
                    "success": True,
                    "primary_topic": "unknown",
                    "confidence": 0.0,
                    "reason": "No se encontraron palabras clave relevantes",
                    "scores": keyword_matches,
                    "method": "keyword_fallback_no_match"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "keyword_fallback_error"
            }
    
    def _get_diversity_classification(self, diversity_score: float) -> str:
        """Clasifica el nivel de diversidad de la colección."""
        if diversity_score >= 70:
            return "Muy diversa"
        elif diversity_score >= 50:
            return "Diversa"
        elif diversity_score >= 30:
            return "Moderadamente diversa"
        else:
            return "Poco diversa"
    
    def _get_documents_by_ids(self, document_ids: List[str]) -> List[Dict[str, Any]]:
        """Obtiene documentos específicos por IDs."""
        # TODO: Implementar búsqueda por IDs específicos
        # Por ahora retornar muestra general
        documents_sample = vector_db.get_all_documents_sample(limit=len(document_ids))
        return [{"content": doc.get("content", ""), 
                "filename": doc.get("metadata", {}).get("filename", f"doc_{i}")}
               for i, doc in enumerate(documents_sample)]

# Instancia global del clasificador
topic_classifier = TopicClassifier()
