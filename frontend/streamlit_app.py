import streamlit as st
import requests
import json
from typing import Optional

# Configuración de la API
API_BASE_URL = "http://backend:8000"

def send_document_to_api(uploaded_file) -> Optional[dict]:
    """
    Envía un documento PDF al backend para su procesamiento.
    
    Args:
        uploaded_file: Archivo subido desde Streamlit
        
    Returns:
        dict: Respuesta del backend o None si hay error
    """
    try:
        files = {"uploaded_file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error del servidor: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("No se puede conectar al backend. Verifica que los servicios estén ejecutándose.")
        return None
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Copiloto Conversacional",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Copiloto Conversacional")
    st.markdown("### Sube tus documentos PDF para procesarlos con IA")
    
    # Sidebar para navegación
    st.sidebar.title("Navegación")
    page = st.sidebar.selectbox(
        "Selecciona una página:",
        ["Subir Documentos", "Chat", "Resúmenes", "Comparaciones"]
    )
    
    if page == "Subir Documentos":
        upload_page()
    elif page == "Chat":
        chat_page()
    elif page == "Resúmenes":
        summary_page()
    elif page == "Comparaciones":
        comparison_page()

def upload_page():
    """Página para subir archivos PDF"""
    st.header("📤 Subir Documentos PDF")
    
    # Mostrar información sobre el procesamiento
    with st.expander("ℹ️ ¿Cómo funciona el procesamiento?"):
        st.markdown("""
        1. **Extracción de texto**: Se extrae todo el texto del PDF usando PyMuPDF
        2. **División en fragmentos**: El texto se divide en chunks de ~1000 caracteres
        3. **Generación de embeddings**: Cada chunk se convierte en un vector usando IA
        4. **Almacenamiento**: Los vectores se guardan en ChromaDB para búsquedas rápidas
        """)
    
    # Subida de archivo
    uploaded_file = st.file_uploader(
        "Selecciona un archivo PDF",
        type=['pdf'],
        help="Solo se permiten archivos PDF"
    )
    
    if uploaded_file is not None:
        # Mostrar información del archivo
        st.success(f"📄 Archivo seleccionado: {uploaded_file.name}")
        st.info(f"📊 Tamaño: {uploaded_file.size / 1024:.2f} KB")
        
        # Botón para procesar
        if st.button("🚀 Procesar Documento", type="primary"):
            with st.spinner("Procesando documento... Esto puede tomar unos momentos."):
                processing_result = send_document_to_api(uploaded_file)
                
                if processing_result:
                    st.success("✅ ¡Documento procesado exitosamente!")
                    
                    # Mostrar estadísticas del procesamiento en columnas
                    col1, col2, col3 = st.columns(3)
                    
                    doc_stats = processing_result.get('document_stats', {})
                    with col1:
                        st.metric("📄 Páginas", doc_stats.get('total_pages', 0))
                        st.metric("📝 Caracteres", doc_stats.get('text_length', 0))
                    
                    with col2:
                        st.metric("🧩 Fragmentos", doc_stats.get('fragments_count', 0))
                        st.metric("🔢 Embeddings", doc_stats.get('embeddings_count', 0))
                    
                    with col3:
                        transformer_info = processing_result.get('model_info', {})
                        st.metric("📐 Dimensión", doc_stats.get('vector_dimension', 0))
                        st.metric("🤖 Modelo", transformer_info.get('model_name', 'N/A').split('/')[-1])
                    
                    # Mostrar metadatos del documento
                    with st.expander("📋 Metadatos del Documento"):
                        doc_metadata = processing_result.get('document_metadata', {})
                        if doc_metadata.get('title'):
                            st.write(f"**Título:** {doc_metadata.get('title')}")
                        if doc_metadata.get('author'):
                            st.write(f"**Autor:** {doc_metadata.get('author')}")
                        if doc_metadata.get('subject'):
                            st.write(f"**Tema:** {doc_metadata.get('subject')}")
                        if doc_metadata.get('creator'):
                            st.write(f"**Creador:** {doc_metadata.get('creator')}")
                    
                    # Mostrar vista previa de fragmentos
                    with st.expander("👀 Vista Previa de Fragmentos"):
                        sample_fragments = processing_result.get('sample_fragments', [])
                        for index, fragment in enumerate(sample_fragments[:3]):
                            st.write(f"**Fragmento {index+1}:**")
                            st.text_area(f"fragment_{index}", fragment, height=100, disabled=True)
                    
                    # Información de la base de datos vectorial
                    with st.expander("🗄️ Estado de la Base de Datos"):
                        db_status = processing_result.get('database_status', {})
                        st.json(db_status)

def chat_page():
    """Página para chat con documentos"""
    st.header("💬 Chat con Documentos")
    st.info("🚧 Funcionalidad en desarrollo")
    st.markdown("Aquí podrás hacer preguntas sobre tus documentos subidos.")

def summary_page():
    """Página para generar resúmenes"""
    st.header("📄 Generar Resúmenes")
    st.info("🚧 Funcionalidad en desarrollo")
    st.markdown("Aquí podrás generar resúmenes automáticos de tus documentos.")

def comparison_page():
    """Página para comparar documentos"""
    st.header("⚖️ Comparar Documentos")
    st.info("🚧 Funcionalidad en desarrollo")
    st.markdown("Aquí podrás comparar similitudes entre diferentes documentos.")

if __name__ == "__main__":
    main()
