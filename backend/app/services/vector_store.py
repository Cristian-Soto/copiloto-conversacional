# vector_store.py
# Gestor de base de datos vectorial con ChromaDB
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid
from datetime import datetime

class VectorDatabase:
    def __init__(self, db_host: str = "chromadb", db_port: int = 8000):
        """
        Inicializa la conexión con la base de datos vectorial.
        
        Args:
            db_host (str): Host del servidor ChromaDB
            db_port (int): Puerto del servidor ChromaDB
        """
        try:
            # FIXME: Agregar retry logic para conexión
            self.chroma_client = chromadb.HttpClient(
                host=db_host,
                port=db_port,
                settings=Settings(allow_reset=True)
            )
            
            # NOTE: Usando colección específica para documentos PDF
            self.document_collection_name = "processed_documents"
            self.doc_collection = self.chroma_client.get_or_create_collection(
                name=self.document_collection_name,
                metadata={"description": "Documentos PDF procesados y vectorizados"}
            )
        except Exception as e:
            raise Exception(f"Error conectando a la base vectorial: {str(e)}")
    
    def store_document_chunks(self, text_fragments: List[str], embedding_vectors: List[List[float]], 
                             chunk_metadata: List[Dict[str, Any]]) -> List[str]:
        """
        Almacena fragmentos de documento con sus vectores y metadatos.
        
        Args:
            text_fragments (List[str]): Fragmentos de texto del documento
            embedding_vectors (List[List[float]]): Vectores embedding correspondientes
            chunk_metadata (List[Dict[str, Any]]): Metadatos de cada fragmento
            
        Returns:
            List[str]: Identificadores únicos generados
        """
        try:
            # Generación de IDs únicos para cada fragmento
            chunk_ids = [str(uuid.uuid4()) for _ in text_fragments]
            
            # Almacenar en la colección vectorial
            self.doc_collection.add(
                documents=text_fragments,
                embeddings=embedding_vectors,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            
            return chunk_ids
        except Exception as e:
            raise Exception(f"Error almacenando en base vectorial: {str(e)}")
    
    def find_similar_content(self, query_vector: List[float], max_results: int = 5) -> Dict[str, Any]:
        """
        Busca contenido similar usando búsqueda vectorial.
        
        Args:
            query_vector (List[float]): Vector de consulta
            max_results (int): Número máximo de resultados
            
        Returns:
            Dict[str, Any]: Resultados de similitud
        """
        try:
            similarity_results = self.doc_collection.query(
                query_embeddings=[query_vector],
                n_results=max_results
            )
            return similarity_results
        except Exception as e:
            raise Exception(f"Error en búsqueda vectorial: {str(e)}")
    
    def get_database_status(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la base de datos vectorial.
        
        Returns:
            Dict[str, Any]: Estado de la base de datos
        """
        try:
            total_documents = self.doc_collection.count()
            return {
                "collection_name": self.document_collection_name,
                "total_chunks": total_documents,
                "collection_metadata": self.doc_collection.metadata
            }
        except Exception as e:
            raise Exception(f"Error obteniendo estado de BD: {str(e)}")
    
    def remove_document_by_name(self, document_name: str) -> bool:
        """
        Elimina todos los fragmentos de un documento específico.
        
        Args:
            document_name (str): Nombre del documento a eliminar
            
        Returns:
            bool: True si se eliminaron fragmentos
        """
        try:
            # Buscar fragmentos por nombre de documento
            document_chunks = self.doc_collection.get(
                where={"filename": document_name}
            )
            
            if document_chunks["ids"]:
                self.doc_collection.delete(ids=document_chunks["ids"])
                return True
            return False
        except Exception as e:
            raise Exception(f"Error eliminando documento: {str(e)}")

# Instancia global de la base de datos vectorial
vector_db = VectorDatabase()
