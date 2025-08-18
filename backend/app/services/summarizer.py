# summarizer.py
# Servicio de resumen avanzado de documentos usando Llama local
import requests
import json
from typing import List, Dict, Any, Optional
from .vector_store import vector_db
from .llm_service import local_llm_service

class DocumentSummarizer:
    def __init__(self):
        """Inicializa el servicio de resumen de documentos."""
        self.ollama_available = False
        self.check_ollama_availability()
    
    def check_ollama_availability(self):
        """Verifica si Ollama está disponible."""
        try:
            status = local_llm_service.get_llm_status()
            self.ollama_available = status.get("ollama_connected", False)
        except Exception:
            self.ollama_available = False
    
    def generate_document_summary(self, document_content: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Genera resumen estructurado de un documento.
        
        Args:
            document_content (str): Contenido del documento
            summary_type (str): Tipo de resumen (comprehensive, executive, technical, bullet_points)
            
        Returns:
            Dict[str, Any]: Resumen estructurado
        """
        try:
            # Preparar prompt según el tipo de resumen
            prompt = self._get_summary_prompt(document_content, summary_type)
            
            if self.ollama_available:
                return self._generate_with_ollama(prompt, summary_type)
            else:
                return self._generate_extractive_summary(document_content, summary_type)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary_type": summary_type
            }
    
    def generate_multi_document_summary(self, document_ids: List[str] = None, 
                                      summary_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Genera resumen de múltiples documentos.
        
        Args:
            document_ids (List[str]): IDs específicos de documentos, None para todos
            summary_type (str): Tipo de resumen
            
        Returns:
            Dict[str, Any]: Resumen consolidado
        """
        try:
            # Obtener contenido de documentos
            if document_ids:
                # TODO: Implementar búsqueda por IDs específicos
                documents_content = self._get_documents_by_ids(document_ids)
            else:
                # Obtener muestra representativa de todos los documentos
                documents_sample = vector_db.get_all_documents_sample(limit=15)
                documents_content = [doc.get("content", "") for doc in documents_sample]
            
            if not documents_content:
                return {
                    "success": False,
                    "error": "No se encontraron documentos para resumir"
                }
            
            # Combinar y estructurar contenido
            combined_content = self._prepare_multi_document_content(documents_content)
            
            # Generar resumen consolidado
            prompt = self._get_multi_document_prompt(combined_content, summary_type)
            
            if self.ollama_available:
                result = self._generate_with_ollama(prompt, f"multi_{summary_type}")
                result["documents_processed"] = len(documents_content)
                return result
            else:
                return self._generate_extractive_multi_summary(documents_content, summary_type)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary_type": f"multi_{summary_type}"
            }
    
    def generate_comparative_summary(self, doc1_content: str, doc2_content: str) -> Dict[str, Any]:
        """
        Genera resumen comparativo entre dos documentos.
        
        Args:
            doc1_content (str): Contenido del primer documento
            doc2_content (str): Contenido del segundo documento
            
        Returns:
            Dict[str, Any]: Resumen comparativo
        """
        try:
            prompt = f"""Analiza y compara los siguientes dos documentos, generando un resumen comparativo estructurado:

DOCUMENTO 1:
{doc1_content[:2000]}{'...' if len(doc1_content) > 2000 else ''}

DOCUMENTO 2:
{doc2_content[:2000]}{'...' if len(doc2_content) > 2000 else ''}

Genera un análisis comparativo que incluya:

1. RESUMEN DE CADA DOCUMENTO
   - Documento 1: [resumen ejecutivo]
   - Documento 2: [resumen ejecutivo]

2. SIMILITUDES PRINCIPALES
   - [lista de temas, enfoques o conclusiones similares]

3. DIFERENCIAS CLAVE
   - [aspectos donde difieren significativamente]

4. ANÁLISIS COMPLEMENTARIO
   - [cómo se complementan o contrastan los documentos]

5. SÍNTESIS GENERAL
   - [conclusiones del análisis comparativo]

ANÁLISIS COMPARATIVO:"""

            if self.ollama_available:
                return self._generate_with_ollama(prompt, "comparative")
            else:
                return {
                    "success": False,
                    "summary": "Resumen comparativo requiere LLM. Ambos documentos contienen información relevante pero se necesita IA para el análisis comparativo.",
                    "method": "fallback_comparative",
                    "documents_compared": 2
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary_type": "comparative"
            }
    
    def _get_summary_prompt(self, content: str, summary_type: str) -> str:
        """Genera prompt especializado según el tipo de resumen."""
        base_content = content[:3000] + ('...' if len(content) > 3000 else '')
        
        prompts = {
            "comprehensive": f"""Analiza el siguiente documento y genera un resumen completo y estructurado:

DOCUMENTO:
{base_content}

Genera un resumen que incluya:

1. RESUMEN EJECUTIVO (2-3 párrafos)
   - Propósito y contexto del documento
   - Hallazgos o argumentos principales
   - Conclusiones relevantes

2. PUNTOS CLAVE
   - [5-7 puntos más importantes del documento]

3. METODOLOGÍA/ENFOQUE (si aplica)
   - [descripción del enfoque utilizado]

4. DATOS Y EVIDENCIA PRINCIPAL
   - [estadísticas, datos, ejemplos relevantes]

5. CONCLUSIONES Y RECOMENDACIONES
   - [conclusiones del autor]
   - [recomendaciones o implicaciones]

RESUMEN ESTRUCTURADO:""",

            "executive": f"""Genera un resumen ejecutivo conciso y profesional del siguiente documento:

DOCUMENTO:
{base_content}

RESUMEN EJECUTIVO:
- Problema/Situación: [descripción breve]
- Hallazgos Principales: [3-4 puntos clave]
- Conclusiones: [resultado principal]
- Recomendaciones: [acciones sugeridas]
- Impacto: [relevancia e implicaciones]

RESUMEN:""",

            "technical": f"""Analiza el siguiente documento desde una perspectiva técnica:

DOCUMENTO:
{base_content}

ANÁLISIS TÉCNICO:
1. ASPECTOS TÉCNICOS PRINCIPALES
2. METODOLOGÍAS Y HERRAMIENTAS
3. DATOS Y MÉTRICAS RELEVANTES
4. LIMITACIONES Y CONSIDERACIONES
5. APLICABILIDAD TÉCNICA

ANÁLISIS:""",

            "bullet_points": f"""Extrae los puntos más importantes del siguiente documento en formato de lista:

DOCUMENTO:
{base_content}

PUNTOS CLAVE:
• [punto principal 1]
• [punto principal 2]
• [punto principal 3]
• [punto principal 4]
• [punto principal 5]
• [conclusión principal]

RESUMEN EN PUNTOS:"""
        }
        
        return prompts.get(summary_type, prompts["comprehensive"])
    
    def _get_multi_document_prompt(self, combined_content: str, summary_type: str) -> str:
        """Genera prompt para resumen de múltiples documentos."""
        return f"""Analiza la siguiente colección de documentos y genera un resumen consolidado:

CONTENIDO DE MÚLTIPLES DOCUMENTOS:
{combined_content}

Genera un resumen consolidado que incluya:

1. PANORAMA GENERAL
   - Temas principales que emergen de los documentos
   - Patrones comunes identificados

2. HALLAZGOS PRINCIPALES
   - Puntos clave recurrentes
   - Conclusiones significativas

3. PERSPECTIVAS DIVERSAS
   - Diferentes enfoques encontrados
   - Variaciones en las conclusiones

4. SÍNTESIS INTEGRADA
   - Conclusiones generales de toda la colección
   - Recomendaciones basadas en el conjunto completo

RESUMEN CONSOLIDADO:"""
    
    def _prepare_multi_document_content(self, documents_content: List[str]) -> str:
        """Prepara contenido de múltiples documentos para resumen."""
        prepared_content = []
        
        for i, content in enumerate(documents_content[:10]):  # Máximo 10 documentos
            doc_preview = content[:800] + ('...' if len(content) > 800 else '')
            prepared_content.append(f"DOCUMENTO {i+1}:\n{doc_preview}\n---")
        
        return "\n\n".join(prepared_content)
    
    def _generate_with_ollama(self, prompt: str, summary_type: str) -> Dict[str, Any]:
        """Genera resumen usando Ollama/Llama."""
        try:
            # Usar el servicio LLM local
            response = local_llm_service.generate_contextual_response(
                question="Genera el resumen solicitado",
                context_fragments=[{"content": prompt}],
                max_tokens=800
            )
            
            if response.get("success", False):
                return {
                    "success": True,
                    "summary": response.get("response", ""),
                    "method": "llama_local",
                    "summary_type": summary_type,
                    "model_used": response.get("model_used", "unknown"),
                    "tokens_used": response.get("tokens_used", 0)
                }
            else:
                return {
                    "success": False,
                    "error": response.get("error", "Error generando resumen"),
                    "summary_type": summary_type
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary_type": summary_type
            }
    
    def _generate_extractive_summary(self, content: str, summary_type: str) -> Dict[str, Any]:
        """Genera resumen extractivo básico cuando no hay LLM."""
        try:
            # Dividir en oraciones
            sentences = content.replace('\n', ' ').split('. ')
            sentences = [s.strip() + '.' for s in sentences if len(s.strip()) > 20]
            
            # Seleccionar oraciones clave (primeras, últimas, y algunas del medio)
            if len(sentences) <= 5:
                key_sentences = sentences
            else:
                key_sentences = []
                key_sentences.extend(sentences[:2])  # Primeras 2
                key_sentences.extend(sentences[len(sentences)//3:len(sentences)//3+2])  # Del medio
                key_sentences.extend(sentences[-2:])  # Últimas 2
            
            summary = ' '.join(key_sentences)
            
            return {
                "success": True,
                "summary": f"RESUMEN EXTRACTIVO:\n\n{summary}\n\nNota: Este es un resumen básico. Para resúmenes más sofisticados, configure Ollama/Llama.",
                "method": "extractive_fallback",
                "summary_type": summary_type,
                "sentences_selected": len(key_sentences),
                "total_sentences": len(sentences)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary_type": summary_type
            }
    
    def _generate_extractive_multi_summary(self, documents_content: List[str], summary_type: str) -> Dict[str, Any]:
        """Genera resumen extractivo de múltiples documentos."""
        try:
            all_key_sentences = []
            
            for i, content in enumerate(documents_content):
                sentences = content.replace('\n', ' ').split('. ')
                sentences = [s.strip() + '.' for s in sentences if len(s.strip()) > 20]
                
                # Tomar 2-3 oraciones clave de cada documento
                if len(sentences) >= 3:
                    key_sentences = [sentences[0], sentences[len(sentences)//2], sentences[-1]]
                else:
                    key_sentences = sentences
                
                doc_summary = f"Documento {i+1}: " + ' '.join(key_sentences[:2])
                all_key_sentences.append(doc_summary)
            
            consolidated_summary = '\n\n'.join(all_key_sentences)
            
            return {
                "success": True,
                "summary": f"RESUMEN CONSOLIDADO EXTRACTIVO:\n\n{consolidated_summary}\n\nNota: Resumen básico de {len(documents_content)} documentos. Configure Ollama para análisis más avanzado.",
                "method": "extractive_multi_fallback",
                "summary_type": summary_type,
                "documents_processed": len(documents_content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary_type": summary_type
            }
    
    def _get_documents_by_ids(self, document_ids: List[str]) -> List[str]:
        """Obtiene documentos específicos por sus IDs."""
        # TODO: Implementar búsqueda específica por IDs en ChromaDB
        # Por ahora, retornar muestra general
        documents_sample = vector_db.get_all_documents_sample(limit=len(document_ids))
        return [doc.get("content", "") for doc in documents_sample]

# Instancia global del resumidor
document_summarizer = DocumentSummarizer()
