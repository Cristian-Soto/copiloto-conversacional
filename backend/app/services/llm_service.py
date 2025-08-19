# llm_service.py
# Servicio para integración con LLM local usando Ollama y LangChain
import requests
import json
import os
from typing import List, Dict, Any, Optional

# Importaciones de LangChain
try:
    from langchain.llms import Ollama
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.chains import LLMChain
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class LocalLLMService:
    def __init__(self, ollama_host: str = "localhost", ollama_port: int = 11434, model_name: str = "llama3"):
        """
        Inicializa el servicio LLM con soporte para LangChain y Ollama directo.
        
        Args:
            ollama_host (str): Host donde está ejecutándose Ollama
            ollama_port (int): Puerto de Ollama  
            model_name (str): Nombre del modelo a usar
        """
        self.ollama_host = ollama_host
        self.ollama_port = ollama_port
        self.ollama_base_url = f"http://{ollama_host}:{ollama_port}"
        self.model_name = model_name
        self.generate_url = f"{self.ollama_base_url}/api/generate"
        
        # Inicializar LangChain si está disponible
        self.langchain_available = LANGCHAIN_AVAILABLE
        self.llm = None
        self.chains = {}
        
        if self.langchain_available:
            self._setup_langchain()
        
        # Verificar disponibilidad del modelo
        self.model_available = self._check_model_availability()
    
    def _setup_langchain(self):
        """Configura LangChain con Ollama."""
        try:
            # Inicializar LLM de LangChain
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.ollama_base_url,
                temperature=0.7,
                num_predict=500
            )
            
            # Configurar prompts estructurados
            self._setup_prompt_templates()
            
            # Configurar chains
            self._setup_chains()
            
        except Exception as e:
            print(f"Error configurando LangChain: {e}")
            self.langchain_available = False
    
    def _setup_prompt_templates(self):
        """Configura templates de prompts estructurados."""
        # Template para Q&A con contexto de documentos
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""Eres un asistente especializado en análisis de documentos. Responde basándote únicamente en el contexto proporcionado.

CONTEXTO DE DOCUMENTOS:
{context}

INSTRUCCIONES:
- Responde únicamente con información del contexto proporcionado
- Si el contexto no contiene información suficiente, indícalo claramente
- Cita el documento específico cuando sea relevante
- Mantén un tono profesional y conciso

PREGUNTA: {question}

RESPUESTA BASADA EN EL CONTEXTO:"""
        )
        
        # Template para resumen de documentos
        self.summary_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Analiza el siguiente texto y proporciona un resumen estructurado:

TEXTO:
{text}

Proporciona:
1. RESUMEN EJECUTIVO (2-3 líneas)
2. PUNTOS CLAVE (máximo 5 puntos)
3. TEMAS PRINCIPALES
4. CONCLUSIONES RELEVANTES

ANÁLISIS:"""
        )
        
        # Template para comparación de documentos
        self.comparison_prompt = PromptTemplate(
            input_variables=["doc1", "doc2"],
            template="""Compara los siguientes documentos y proporciona un análisis estructurado:

DOCUMENTO 1:
{doc1}

DOCUMENTO 2:
{doc2}

ANÁLISIS COMPARATIVO:
1. SIMILITUDES
2. DIFERENCIAS CLAVE
3. COMPLEMENTARIEDAD
4. CONCLUSIONES

COMPARACIÓN:"""
        )
    
    def _setup_chains(self):
        """Configura las chains de LangChain."""
        if self.llm:
            # Chain para Q&A con contexto
            self.chains['qa'] = LLMChain(
                llm=self.llm,
                prompt=self.qa_prompt,
                verbose=False
            )
            
            # Chain para resúmenes
            self.chains['summary'] = LLMChain(
                llm=self.llm,
                prompt=self.summary_prompt,
                verbose=False
            )
            
            # Chain para comparaciones
            self.chains['comparison'] = LLMChain(
                llm=self.llm,
                prompt=self.comparison_prompt,
                verbose=False
            )
            
            # Memoria para conversaciones
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
    
    def _check_model_availability(self) -> bool:
        """Verifica si el modelo está disponible en Ollama."""
        try:
            test_payload = {
                "model": self.model_name,
                "prompt": "Test",
                "stream": False
            }
            
            response = requests.post(
                self.generate_url,
                json=test_payload,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception:
            return False
    
    def get_llm_status(self) -> Dict[str, Any]:
        """Obtiene el estado completo del servicio LLM."""
        try:
            models_url = f"{self.ollama_base_url}/api/tags"
            response = requests.get(models_url, timeout=5)
            
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model["name"] for model in models_data.get("models", [])]
                
                return {
                    "ollama_connected": True,
                    "langchain_available": self.langchain_available,
                    "model_name": self.model_name,
                    "model_available": self.model_name in available_models,
                    "available_models": available_models,
                    "base_url": self.ollama_base_url,
                    "chains_configured": len(self.chains) if self.langchain_available else 0,
                    "features": {
                        "structured_prompts": self.langchain_available,
                        "conversation_memory": self.langchain_available,
                        "document_qa": True,
                        "summarization": self.langchain_available,
                        "comparison": self.langchain_available
                    }
                }
            else:
                return {
                    "ollama_connected": False,
                    "error": f"Error conectando con Ollama: {response.status_code}",
                    "model_available": False
                }
        except Exception as e:
            return {
                "ollama_connected": False,
                "error": str(e),
                "model_available": False,
                "recommendation": "Verifica que Ollama esté ejecutándose"
            }
    
    def generate_contextual_response(self, question: str, context_fragments: List[Dict[str, Any]], 
                                   max_tokens: int = 500) -> Dict[str, Any]:
        """
        Genera respuesta contextual usando LangChain si está disponible, sino Ollama directo.
        
        Args:
            question (str): Pregunta del usuario
            context_fragments (List[Dict]): Fragmentos de contexto relevantes
            max_tokens (int): Número máximo de tokens
            
        Returns:
            Dict[str, Any]: Respuesta generada con metadatos
        """
        try:
            if not self.model_available:
                return self._fallback_response(question, context_fragments)
            
            # Construir contexto estructurado
            context_text = self._build_context_from_fragments(context_fragments)
            
            # Usar LangChain si está disponible
            if self.langchain_available and 'qa' in self.chains:
                return self._generate_with_langchain(question, context_text, context_fragments)
            else:
                return self._generate_with_ollama_direct(question, context_text, context_fragments, max_tokens)
                
        except Exception as e:
            return self._fallback_response(question, context_fragments, str(e))
    
    def _generate_with_langchain(self, question: str, context_text: str, 
                               context_fragments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera respuesta usando LangChain."""
        try:
            # Ejecutar chain de Q&A
            response = self.chains['qa'].run(
                context=context_text,
                question=question
            )
            
            return {
                "success": True,
                "response": response.strip(),
                "method": "langchain_structured",
                "model_used": self.model_name,
                "context_fragments_used": len(context_fragments),
                "langchain_used": True,
                "prompt_template": "structured_qa"
            }
            
        except Exception as e:
            # Fallback a Ollama directo si LangChain falla
            return self._generate_with_ollama_direct(question, context_text, context_fragments, 500)
    
    def _generate_with_ollama_direct(self, question: str, context_text: str, 
                                   context_fragments: List[Dict[str, Any]], max_tokens: int) -> Dict[str, Any]:
        """Genera respuesta usando Ollama directamente."""
        try:
            system_prompt = """Eres un asistente de análisis de documentos. Responde basándote SOLO en el contexto proporcionado.

REGLAS:
- Solo usa información del contexto
- Si no hay información suficiente, dilo claramente
- Sé conciso y directo"""

            user_prompt = f"""CONTEXTO:
{context_text}

PREGUNTA: {question}

RESPUESTA BASADA EN EL CONTEXTO:"""

            payload = {
                "model": self.model_name,
                "prompt": f"{system_prompt}\n\n{user_prompt}",
                "stream": False,
                "options": {
                    "num_predict": 200,  # Reducir para respuestas más rápidas
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.generate_url, json=payload, timeout=90)
            
            if response.status_code == 200:
                response_data = response.json()
                generated_text = response_data.get("response", "").strip()
                
                return {
                    "success": True,
                    "response": generated_text,
                    "method": "ollama_direct",
                    "model_used": self.model_name,
                    "context_fragments_used": len(context_fragments),
                    "langchain_used": False,
                    "tokens_used": response_data.get("eval_count", 0),
                    "generation_time": response_data.get("total_duration", 0) / 1e9 if response_data.get("total_duration") else 0
                }
            else:
                raise Exception(f"Error HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            raise e
    
    def generate_document_summary(self, document_content: str) -> Dict[str, Any]:
        """
        Genera resumen estructurado de un documento.
        
        Args:
            document_content (str): Contenido del documento
            
        Returns:
            Dict[str, Any]: Resumen estructurado
        """
        try:
            if not self.model_available:
                return {"success": False, "error": "Modelo no disponible"}
            
            # Truncar contenido si es muy largo
            max_content_length = 3000
            if len(document_content) > max_content_length:
                document_content = document_content[:max_content_length] + "..."
            
            if self.langchain_available and 'summary' in self.chains:
                # Usar LangChain para resumen estructurado
                response = self.chains['summary'].run(text=document_content)
                
                return {
                    "success": True,
                    "summary": response.strip(),
                    "method": "langchain_structured_summary",
                    "original_length": len(document_content),
                    "truncated": len(document_content) > max_content_length
                }
            else:
                # Usar Ollama directo
                prompt = f"""Analiza el siguiente texto y proporciona un resumen estructurado:

TEXTO:
{document_content}

Proporciona:
1. RESUMEN EJECUTIVO (2-3 líneas)
2. PUNTOS CLAVE (máximo 5 puntos)  
3. TEMAS PRINCIPALES
4. CONCLUSIONES RELEVANTES

ANÁLISIS:"""

                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 400, "temperature": 0.7}
                }
                
                response = requests.post(self.generate_url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    response_data = response.json()
                    return {
                        "success": True,
                        "summary": response_data.get("response", "").strip(),
                        "method": "ollama_direct_summary",
                        "original_length": len(document_content),
                        "truncated": len(document_content) > max_content_length
                    }
                else:
                    return {"success": False, "error": f"Error HTTP {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def compare_documents(self, doc1_content: str, doc2_content: str) -> Dict[str, Any]:
        """
        Compara dos documentos usando LangChain o Ollama directo.
        
        Args:
            doc1_content (str): Contenido del primer documento
            doc2_content (str): Contenido del segundo documento
            
        Returns:
            Dict[str, Any]: Análisis comparativo
        """
        try:
            if not self.model_available:
                return {"success": False, "error": "Modelo no disponible"}
            
            # Truncar contenido si es necesario
            max_len = 1500
            if len(doc1_content) > max_len:
                doc1_content = doc1_content[:max_len] + "..."
            if len(doc2_content) > max_len:
                doc2_content = doc2_content[:max_len] + "..."
            
            if self.langchain_available and 'comparison' in self.chains:
                # Usar LangChain para comparación estructurada
                response = self.chains['comparison'].run(
                    doc1=doc1_content,
                    doc2=doc2_content
                )
                
                return {
                    "success": True,
                    "comparison": response.strip(),
                    "method": "langchain_structured_comparison"
                }
            else:
                # Usar Ollama directo
                prompt = f"""Compara los siguientes documentos:

DOCUMENTO 1:
{doc1_content}

DOCUMENTO 2:
{doc2_content}

ANÁLISIS COMPARATIVO:
1. SIMILITUDES
2. DIFERENCIAS CLAVE
3. COMPLEMENTARIEDAD
4. CONCLUSIONES

COMPARACIÓN:"""

                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 500, "temperature": 0.7}
                }
                
                response = requests.post(self.generate_url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    response_data = response.json()
                    return {
                        "success": True,
                        "comparison": response_data.get("response", "").strip(),
                        "method": "ollama_direct_comparison"
                    }
                else:
                    return {"success": False, "error": f"Error HTTP {response.status_code}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def clear_conversation_memory(self):
        """Limpia la memoria de conversación."""
        if hasattr(self, 'memory') and self.memory:
            self.memory.clear()
    
    def _build_context_from_fragments(self, fragments: List[Dict[str, Any]]) -> str:
        """Construye contexto estructurado a partir de fragmentos."""
        context_parts = []
        
        for i, fragment in enumerate(fragments[:3]):  # Límite de 3 fragmentos para reducir tamaño
            filename = fragment.get('metadata', {}).get('filename', f'Documento_{i+1}')
            content = fragment.get('content', '')
            similarity = fragment.get('similarity_score', 0)
            
            # Truncar contenido si es muy largo
            max_content_length = 800  # Reducir longitud máxima
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            context_part = f"""[DOCUMENTO: {filename}]
[RELEVANCIA: {similarity:.3f}]
{content}
---"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _fallback_response(self, question: str, context_fragments: List[Dict[str, Any]], error: str = None) -> Dict[str, Any]:
        """Genera respuesta de respaldo cuando el LLM no está disponible."""
        if context_fragments:
            best_fragment = context_fragments[0]
            filename = best_fragment.get('metadata', {}).get('filename', 'documento')
            content = best_fragment.get('content', '')
            
            response = f"""Información encontrada en {filename}:

{content[:500]}{'...' if len(content) > 500 else ''}

(Respuesta generada sin LLM - Se encontró información relevante pero no se pudo procesar con IA)"""
        else:
            response = "No se encontró información relevante en los documentos para responder tu pregunta."
        
        return {
            "success": False,
            "response": response,
            "method": "fallback",
            "error": error,
            "recommendation": "Configura Ollama para obtener respuestas más inteligentes"
        }

# Instancia global del servicio LLM
ollama_host = os.getenv("OLLAMA_HOST", "ollama")
ollama_port = int(os.getenv("OLLAMA_PORT", "11434"))
ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

local_llm_service = LocalLLMService(
    ollama_host=ollama_host,
    ollama_port=ollama_port,
    model_name=ollama_model
)