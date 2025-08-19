# retrieval.py
# Servicio especializado para recuperación de información contextual
from typing import List, Dict, Any, Optional
from .embeddings import document_embedding_manager
from .vector_store import vector_db

class ContextualRetriever:
    def __init__(self):
        """
        Inicializa el sistema de recuperación contextual.
        """
        self.embedding_manager = document_embedding_manager
        self.vector_database = vector_db
    
    def search_relevant_context(self, query: str, max_results: int = 5, 
                               similarity_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Busca contexto relevante en ChromaDB basado en una consulta.
        
        Args:
            query (str): Consulta del usuario
            max_results (int): Número máximo de resultados
            similarity_threshold (float): Umbral mínimo de similitud
            
        Returns:
            Dict[str, Any]: Contexto encontrado con metadatos
        """
        try:
            # STEP 1: Generar embedding de la consulta
            query_embedding = self.embedding_manager.create_single_embedding(query)
            
            # STEP 2: Buscar en la base de datos vectorial
            search_results = self.vector_database.find_similar_content(
                query_vector=query_embedding,
                max_results=max_results
            )
            
            # STEP 3: Procesar y filtrar resultados
            processed_context = self._process_search_results(
                search_results, 
                similarity_threshold
            )
            
            # STEP 4: Generar respuesta estructurada
            return {
                "success": True,
                "query": query,
                "context_found": len(processed_context) > 0,
                "relevant_fragments": processed_context,
                "search_metadata": {
                    "total_results": len(processed_context),
                    "similarity_threshold": similarity_threshold,
                    "max_results_requested": max_results,
                    "embedding_dimension": len(query_embedding)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en búsqueda contextual: {str(e)}",
                "query": query,
                "context_found": False,
                "relevant_fragments": [],
                "search_metadata": {}
            }
    
    def _process_search_results(self, search_results: Dict[str, Any], 
                               threshold: float) -> List[Dict[str, Any]]:
        """
        Procesa los resultados de búsqueda de ChromaDB.
        
        Args:
            search_results: Resultados brutos de ChromaDB
            threshold: Umbral de similitud
            
        Returns:
            List[Dict]: Fragmentos procesados y filtrados
        """
        processed_fragments = []
        
        if not search_results.get('documents') or not search_results['documents'][0]:
            return processed_fragments
        
        documents = search_results['documents'][0]
        metadatas = search_results.get('metadatas', [[]])[0]
        distances = search_results.get('distances', [[]])[0]
        
        for i, document in enumerate(documents):
            # Calcular similitud para distancia coseno
            # ChromaDB devuelve distancias coseno, donde menor distancia = mayor similitud
            distance = distances[i] if i < len(distances) else 2.0
            # Para distancia coseno: similitud = (2 - distancia) / 2
            # Esto mapea distancia 0 -> similitud 1.0, distancia 2 -> similitud 0.0
            similarity_score = max(0, (2 - distance) / 2)
            
            # Filtrar por umbral de similitud
            if similarity_score >= threshold:
                metadata = metadatas[i] if i < len(metadatas) else {}
                
                fragment_info = {
                    "content": document,
                    "similarity_score": round(similarity_score, 4),
                    "metadata": {
                        "filename": metadata.get('filename', 'Desconocido'),
                        "fragment_index": metadata.get('fragment_index', 0),
                        "fragment_length": metadata.get('fragment_length', len(document)),
                        "document_title": metadata.get('document_title', ''),
                        "processing_timestamp": metadata.get('processing_timestamp', ''),
                        "content_preview": metadata.get('content_preview', '')
                    },
                    "relevance_rank": i + 1
                }
                processed_fragments.append(fragment_info)
        
        # Ordenar por similitud descendente
        processed_fragments.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return processed_fragments
    
    def search_by_document(self, document_filename: str, 
                          max_results: int = 10) -> Dict[str, Any]:
        """
        Busca todos los fragmentos de un documento específico.
        
        Args:
            document_filename (str): Nombre del documento
            max_results (int): Número máximo de fragmentos
            
        Returns:
            Dict[str, Any]: Fragmentos del documento
        """
        try:
            # NOTE: Búsqueda directa por metadatos en lugar de similitud semántica
            # Esta funcionalidad requiere implementación específica en ChromaDB
            # Por ahora retornamos un placeholder
            
            return {
                "document_filename": document_filename,
                "fragments_found": [],
                "total_fragments": 0,
                "status": "Funcionalidad en desarrollo - búsqueda por documento específico"
            }
            
        except Exception as e:
            raise Exception(f"Error buscando documento {document_filename}: {str(e)}")
    
    def get_context_summary(self, fragments: List[Dict[str, Any]]) -> str:
        """
        Genera un resumen del contexto encontrado.
        
        Args:
            fragments: Lista de fragmentos relevantes
            
        Returns:
            str: Resumen contextual
        """
        if not fragments:
            return "No se encontró contexto relevante para la consulta."
        
        # Extraer información clave
        unique_documents = set()
        total_content_length = 0
        
        for fragment in fragments:
            unique_documents.add(fragment['metadata']['filename'])
            total_content_length += len(fragment['content'])
        
        best_similarity = max(fragments, key=lambda x: x['similarity_score'])['similarity_score']
        
        summary = f"""
        Contexto encontrado:
        - {len(fragments)} fragmentos relevantes
        - {len(unique_documents)} documentos únicos
        - Mejor similitud: {best_similarity:.3f}
        - Contenido total: {total_content_length} caracteres
        """
        
        return summary.strip()

# Instancia global del recuperador contextual
contextual_retriever = ContextualRetriever()
