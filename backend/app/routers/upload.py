# upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from ..services.pdf_processing import extract_text_content, extract_document_metadata, process_pdf_document
from ..services.embeddings import document_embedding_manager
from ..services.vector_store import vector_db
import os
import tempfile
from datetime import datetime

router = APIRouter()

@router.post("/upload")
async def process_pdf_upload(uploaded_file: UploadFile = File(...)):
    """
    Endpoint para procesar y almacenar documentos PDF.
    
    Args:
        uploaded_file: Archivo PDF subido por el usuario
        
    Returns:
        JSONResponse: Resultado del procesamiento
    """
    # Validación de tipo de archivo
    if uploaded_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF.")
    
    # Crear archivo temporal para procesamiento
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        file_content = await uploaded_file.read()
        temp_file.write(file_content)
        temporary_path = temp_file.name
    
    try:
        #Extraer contenido textual del PDF
        document_text = extract_text_content(temporary_path)
        document_metadata = extract_document_metadata(temporary_path)
        
        #Fragmentar el contenido en chunks procesables
        text_fragments = process_pdf_document(temporary_path, fragment_size=1000, fragment_overlap=200)
        
        #Generar vectores embedding para los fragmentos
        embedding_vectors = document_embedding_manager.create_embeddings(text_fragments)
        
        #Preparar metadatos detallados para cada fragmento
        fragments_metadata = []
        for fragment_index, fragment_text in enumerate(text_fragments):
            fragment_meta = {
                "filename": uploaded_file.filename,
                "fragment_index": fragment_index,
                "fragment_length": len(fragment_text),
                "processing_timestamp": datetime.now().isoformat(),
                "total_pages": document_metadata.get('total_pages', 0),
                "document_title": document_metadata.get('title', ''),
                "document_author": document_metadata.get('author', ''),
                "document_subject": document_metadata.get('subject', ''),
                "content_preview": fragment_text[:100] + "..." if len(fragment_text) > 100 else fragment_text
            }
            fragments_metadata.append(fragment_meta)
        
        #Almacenar en base de datos vectorial
        stored_fragment_ids = vector_db.store_document_chunks(text_fragments, embedding_vectors, fragments_metadata)
        
        # Limpiar archivo temporal
        os.unlink(temporary_path)
        
        # Respuesta con información del procesamiento
        return JSONResponse(content={
            "filename": uploaded_file.filename,
            "status": "Documento procesado y almacenado exitosamente.",
            "document_stats": {
                "text_length": len(document_text),
                "total_pages": document_metadata.get('total_pages', 0),
                "fragments_count": len(text_fragments),
                "embeddings_count": len(embedding_vectors),
                "vector_dimension": len(embedding_vectors[0]) if embedding_vectors else 0,
            },
            "stored_fragment_ids": stored_fragment_ids,
            "sample_fragments": text_fragments[:3],  # Primeros 3 fragmentos como muestra
            "document_metadata": document_metadata,
            "model_info": document_embedding_manager.get_transformer_info(),
            "database_status": vector_db.get_database_status()
        })
    except Exception as e:
        # Limpiar archivo temporal en caso de error
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)
        raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")
