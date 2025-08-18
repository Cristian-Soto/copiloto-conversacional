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
        ["Subir Documentos", "Chat", "Resúmenes", "Resumen Avanzado", "Clasificación de Temas", "Comparaciones"]
    )
    
    if page == "Subir Documentos":
        upload_page()
    elif page == "Chat":
        chat_page()
    elif page == "Resúmenes":
        summary_page()
    elif page == "Resumen Avanzado":
        advanced_summary_page()
    elif page == "Clasificación de Temas":
        topic_classification_page()
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
    
    # Verificar estado del sistema
    try:
        status_response = requests.get(f"{API_BASE_URL}/api/chat/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            llm_status = status_data.get("llm_service", {})
            
            # Mostrar estado del sistema
            col1, col2, col3 = st.columns(3)
            with col1:
                if llm_status.get("ollama_connected", False):
                    st.success("🤖 Ollama Conectado")
                else:
                    st.error("❌ Ollama Desconectado")
            
            with col2:
                if llm_status.get("langchain_available", False):
                    st.success("🔗 LangChain Activo")
                else:
                    st.warning("⚠️ LangChain No Disponible")
            
            with col3:
                vector_db = status_data.get("vector_database", {})
                total_chunks = vector_db.get("total_chunks", 0)
                st.info(f"📚 {total_chunks} fragmentos disponibles")
        else:
            st.error("❌ No se puede conectar al sistema de chat")
            return
    except Exception as e:
        st.error(f"❌ Error verificando estado: {str(e)}")
        return
    
    # Inicializar historial de chat en session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = 0
    
    # Configuración del chat
    st.subheader("⚙️ Configuración")
    col1, col2 = st.columns(2)
    
    with col1:
        max_results = st.slider(
            "� Máximo de fragmentos relevantes:", 
            min_value=1, max_value=10, value=5,
            help="Número máximo de fragmentos de documentos a considerar"
        )
    
    with col2:
        similarity_threshold = st.slider(
            "🎯 Umbral de similitud:", 
            min_value=0.0, max_value=1.0, value=0.5, step=0.1,
            help="Umbral mínimo de similitud para considerar un fragmento relevante"
        )
    
    # Área de chat
    st.subheader("💬 Conversación")
    
    # Mostrar historial de chat
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    
                    # Mostrar metadatos si están disponibles
                    if "metadata" in message:
                        metadata = message["metadata"]
                        with st.expander("📊 Detalles de la respuesta"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Método:** {metadata.get('method', 'N/A')}")
                                st.write(f"**Fragmentos usados:** {metadata.get('relevant_documents', 0)}")
                            with col2:
                                if metadata.get('langchain_used'):
                                    st.success("🔗 LangChain utilizado")
                                else:
                                    st.info("🤖 Ollama directo")
    
    # Campo de entrada para nueva pregunta
    st.subheader("✍️ Haz tu pregunta")
    
    # Usar form para mejor UX
    with st.form(key=f"chat_form_{st.session_state.chat_input_key}", clear_on_submit=True):
        user_question = st.text_area(
            "Pregunta:",
            placeholder="Ej: ¿Cuáles son los puntos principales del documento?",
            height=100,
            help="Escribe tu pregunta sobre los documentos subidos"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submit_button = st.form_submit_button("🚀 Enviar", type="primary")
        with col2:
            clear_button = st.form_submit_button("🗑️ Limpiar Chat")
    
    # Procesar envío de pregunta
    if submit_button and user_question.strip():
        # Agregar pregunta del usuario al historial
        st.session_state.chat_history.append({
            "role": "user", 
            "content": user_question
        })
        
        # Mostrar la pregunta inmediatamente
        with chat_container:
            st.chat_message("user").write(user_question)
        
        # Enviar pregunta al backend
        with st.spinner("🤔 Generando respuesta..."):
            try:
                chat_request = {
                    "question": user_question,
                    "max_results": max_results,
                    "similarity_threshold": similarity_threshold
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/api/chat/simple",
                    json=chat_request,
                    timeout=30
                )
                
                if response.status_code == 200:
                    chat_response = response.json()
                    
                    if "error" in chat_response:
                        answer = f"❌ Error: {chat_response['error']}"
                        metadata = {"method": "error", "relevant_documents": 0}
                    else:
                        answer = chat_response.get("response", "No se recibió respuesta")
                        metadata = {
                            "method": chat_response.get("method", "unknown"),
                            "relevant_documents": chat_response.get("relevant_documents", 0),
                            "langchain_used": chat_response.get("langchain_used", False)
                        }
                    
                    # Agregar respuesta al historial
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "metadata": metadata
                    })
                    
                    # Mostrar respuesta inmediatamente
                    with chat_container:
                        with st.chat_message("assistant"):
                            st.write(answer)
                            
                            with st.expander("📊 Detalles de la respuesta"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Método:** {metadata.get('method', 'N/A')}")
                                    st.write(f"**Fragmentos usados:** {metadata.get('relevant_documents', 0)}")
                                with col2:
                                    if metadata.get('langchain_used'):
                                        st.success("🔗 LangChain utilizado")
                                    else:
                                        st.info("🤖 Ollama directo")
                else:
                    error_msg = f"❌ Error del servidor: {response.status_code}"
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "metadata": {"method": "error", "relevant_documents": 0}
                    })
                    
                    with chat_container:
                        st.chat_message("assistant").write(error_msg)
                        
            except requests.exceptions.Timeout:
                timeout_msg = "⏱️ Tiempo de espera agotado. El modelo puede estar procesando una consulta compleja."
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": timeout_msg,
                    "metadata": {"method": "timeout", "relevant_documents": 0}
                })
                
                with chat_container:
                    st.chat_message("assistant").write(timeout_msg)
                    
            except Exception as e:
                error_msg = f"❌ Error inesperado: {str(e)}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg,
                    "metadata": {"method": "error", "relevant_documents": 0}
                })
                
                with chat_container:
                    st.chat_message("assistant").write(error_msg)
        
        # Incrementar key para limpiar el form
        st.session_state.chat_input_key += 1
        st.rerun()
    
    # Procesar limpieza de chat
    if clear_button:
        st.session_state.chat_history = []
        st.session_state.chat_input_key += 1
        st.success("🗑️ Chat limpiado exitosamente")
        st.rerun()
    
    # Botones adicionales
    st.subheader("🛠️ Acciones Adicionales")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generar Resumen de Chat"):
            if st.session_state.chat_history:
                # Combinar todas las preguntas y respuestas
                chat_text = "\n\n".join([
                    f"{'Usuario' if msg['role'] == 'user' else 'Asistente'}: {msg['content']}"
                    for msg in st.session_state.chat_history
                ])
                
                st.text_area("📄 Resumen de la conversación:", chat_text, height=200)
            else:
                st.info("No hay conversación para resumir")
    
    with col2:
        if st.button("💾 Descargar Chat"):
            if st.session_state.chat_history:
                # Crear archivo de descarga
                chat_export = {
                    "timestamp": str(st.timestamp if hasattr(st, 'timestamp') else ""),
                    "messages": st.session_state.chat_history
                }
                
                st.download_button(
                    label="⬇️ Descargar JSON",
                    data=json.dumps(chat_export, indent=2, ensure_ascii=False),
                    file_name="chat_conversation.json",
                    mime="application/json"
                )
            else:
                st.info("No hay conversación para descargar")
    
    # Ayuda y ejemplos
    with st.expander("💡 Ejemplos de preguntas"):
        st.markdown("""
        **Preguntas de análisis:**
        - ¿Cuáles son los puntos principales del documento?
        - ¿Qué conclusiones presenta el autor?
        - ¿Hay datos estadísticos relevantes?
        
        **Preguntas específicas:**
        - ¿Qué dice sobre [tema específico]?
        - ¿Cuáles son las recomendaciones mencionadas?
        - ¿Hay fechas o números importantes?
        
        **Preguntas comparativas:**
        - ¿Cómo se relaciona esto con [concepto]?
        - ¿Cuáles son las ventajas y desventajas mencionadas?
        """)
    
    # Información técnica
    with st.expander("🔧 Información Técnica"):
        st.markdown(f"""
        **Configuración actual:**
        - Fragmentos máximos: {max_results}
        - Umbral de similitud: {similarity_threshold}
        - Mensajes en historial: {len(st.session_state.chat_history)}
        
        **Estado del sistema:**
        - Backend: {API_BASE_URL}
        - LLM: {"Ollama + LangChain" if llm_status.get("langchain_available") else "Ollama directo"}
        - Base vectorial: ChromaDB
        """)

def summary_page():
    """Página para generar resúmenes"""
    st.header("📄 Generar Resúmenes")
    
    # Verificar estado del sistema
    try:
        status_response = requests.get(f"{API_BASE_URL}/api/chat/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            vector_db = status_data.get("vector_database", {})
            total_chunks = vector_db.get("total_chunks", 0)
            
            if total_chunks == 0:
                st.warning("⚠️ No hay documentos cargados. Ve a 'Subir Documentos' primero.")
                return
            else:
                st.success(f"📚 {total_chunks} fragmentos de documentos disponibles")
        else:
            st.error("❌ No se puede conectar al sistema")
            return
    except Exception as e:
        st.error(f"❌ Error verificando estado: {str(e)}")
        return
    
    st.markdown("Genera resúmenes automáticos de tus documentos usando IA.")
    
    # Opciones de resumen
    st.subheader("⚙️ Configuración del Resumen")
    
    col1, col2 = st.columns(2)
    with col1:
        summary_type = st.selectbox(
            "Tipo de resumen:",
            ["Colección completa", "Documento específico"],
            help="Elige si quieres resumir todos los documentos o uno específico"
        )
    
    with col2:
        max_length = st.slider(
            "Longitud máxima:",
            min_value=100, max_value=1000, value=500,
            help="Número máximo de caracteres en el resumen"
        )
    
    # Generar resumen
    if st.button("📝 Generar Resumen", type="primary"):
        with st.spinner("🤖 Generando resumen..."):
            try:
                summary_request = {
                    "max_length": max_length
                }
                
                if summary_type == "Documento específico":
                    # TODO: Implementar selección de documento específico
                    st.info("🚧 Selección de documento específico en desarrollo")
                    return
                
                response = requests.post(
                    f"{API_BASE_URL}/api/summarize",
                    json=summary_request,
                    timeout=60
                )
                
                if response.status_code == 200:
                    summary_response = response.json()
                    
                    if summary_response.get("success", False):
                        st.success("✅ Resumen generado exitosamente")
                        
                        # Mostrar resumen
                        st.subheader("📋 Resumen Generado")
                        summary_text = summary_response.get("summary", "")
                        st.markdown(summary_text)
                        
                        # Mostrar estadísticas
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("📊 Documentos analizados", summary_response.get("documents_analyzed", 0))
                        with col2:
                            st.metric("🔧 Método usado", summary_response.get("method", "unknown"))
                        
                        # Opción de descarga
                        st.download_button(
                            label="⬇️ Descargar Resumen",
                            data=summary_text,
                            file_name="resumen_documentos.txt",
                            mime="text/plain"
                        )
                        
                    else:
                        st.error(f"❌ Error generando resumen: {summary_response.get('error', 'Error desconocido')}")
                else:
                    st.error(f"❌ Error del servidor: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Tiempo de espera agotado. El resumen puede estar tardando más de lo esperado.")
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")
    
    # Información adicional
    with st.expander("💡 Tipos de resumen disponibles"):
        st.markdown("""
        **Resumen de colección completa:**
        - Analiza todos los documentos cargados
        - Identifica temas principales y patrones comunes
        - Proporciona una vista general de toda la información
        
        **Resumen de documento específico:**
        - Analiza un documento individual
        - Extrae puntos clave específicos del documento
        - Más detallado y enfocado
        """)
    
    with st.expander("🔧 Cómo funciona"):
        st.markdown("""
        1. **Selección de contenido**: Se seleccionan fragmentos representativos de los documentos
        2. **Análisis con IA**: El modelo de lenguaje analiza el contenido
        3. **Estructuración**: Se genera un resumen estructurado con:
           - Resumen ejecutivo
           - Puntos clave
           - Temas principales
           - Conclusiones relevantes
        """)

def comparison_page():
    """Página para comparar documentos"""
    st.header("⚖️ Comparar Documentos")
    
    # Verificar estado del sistema
    try:
        status_response = requests.get(f"{API_BASE_URL}/api/chat/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            vector_db = status_data.get("vector_database", {})
            total_chunks = vector_db.get("total_chunks", 0)
            
            if total_chunks == 0:
                st.warning("⚠️ No hay documentos cargados. Ve a 'Subir Documentos' primero.")
                return
            else:
                st.success(f"📚 {total_chunks} fragmentos de documentos disponibles")
        else:
            st.error("❌ No se puede conectar al sistema")
            return
    except Exception as e:
        st.error(f"❌ Error verificando estado: {str(e)}")
        return
    
    st.markdown("Compara diferentes aspectos o temas entre tus documentos usando IA.")
    
    # Configuración de comparación
    st.subheader("🔍 Configurar Comparación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 Primer conjunto de documentos:**")
        query1 = st.text_area(
            "Describe qué buscar en el primer grupo:",
            placeholder="Ej: metodología de investigación, conclusiones sobre X tema",
            height=100,
            help="Describe el tema o aspecto que quieres encontrar en el primer grupo de documentos"
        )
    
    with col2:
        st.markdown("**📄 Segundo conjunto de documentos:**")
        query2 = st.text_area(
            "Describe qué buscar en el segundo grupo:",
            placeholder="Ej: resultados experimentales, recomendaciones sobre Y tema",
            height=100,
            help="Describe el tema o aspecto que quieres encontrar en el segundo grupo de documentos"
        )
    
    # Configuración adicional
    col1, col2 = st.columns(2)
    with col1:
        max_results = st.slider(
            "📊 Fragmentos por grupo:",
            min_value=1, max_value=5, value=3,
            help="Número máximo de fragmentos relevantes por cada grupo"
        )
    
    with col2:
        comparison_focus = st.selectbox(
            "🎯 Enfoque de comparación:",
            ["Similitudes y diferencias", "Solo similitudes", "Solo diferencias", "Análisis complementario"],
            help="Tipo de análisis comparativo a realizar"
        )
    
    # Generar comparación
    if st.button("⚖️ Generar Comparación", type="primary"):
        if not query1.strip() or not query2.strip():
            st.error("❌ Por favor, completa ambas descripciones de búsqueda")
            return
        
        with st.spinner("🤖 Analizando y comparando documentos..."):
            try:
                comparison_request = {
                    "doc1_query": query1,
                    "doc2_query": query2,
                    "max_results": max_results
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/api/compare",
                    json=comparison_request,
                    timeout=60
                )
                
                if response.status_code == 200:
                    comparison_response = response.json()
                    
                    if comparison_response.get("success", False):
                        st.success("✅ Comparación generada exitosamente")
                        
                        # Mostrar estadísticas de la búsqueda
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📄 Fragmentos Grupo 1", comparison_response.get("doc1_fragments", 0))
                        with col2:
                            st.metric("� Fragmentos Grupo 2", comparison_response.get("doc2_fragments", 0))
                        with col3:
                            st.metric("🔧 Método", comparison_response.get("method", "unknown"))
                        
                        # Mostrar consultas utilizadas
                        with st.expander("🔍 Consultas utilizadas"):
                            queries = comparison_response.get("queries", {})
                            st.write(f"**Grupo 1:** {queries.get('doc1_query', 'N/A')}")
                            st.write(f"**Grupo 2:** {queries.get('doc2_query', 'N/A')}")
                        
                        # Mostrar comparación
                        st.subheader("📊 Análisis Comparativo")
                        comparison_text = comparison_response.get("comparison", "")
                        st.markdown(comparison_text)
                        
                        # Opción de descarga
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="⬇️ Descargar Comparación",
                                data=comparison_text,
                                file_name="comparacion_documentos.txt",
                                mime="text/plain"
                            )
                        
                        with col2:
                            # Descargar datos completos como JSON
                            comparison_data = {
                                "queries": queries,
                                "statistics": {
                                    "doc1_fragments": comparison_response.get("doc1_fragments", 0),
                                    "doc2_fragments": comparison_response.get("doc2_fragments", 0),
                                    "method": comparison_response.get("method", "unknown")
                                },
                                "comparison": comparison_text
                            }
                            
                            st.download_button(
                                label="📋 Descargar Datos JSON",
                                data=json.dumps(comparison_data, indent=2, ensure_ascii=False),
                                file_name="comparacion_completa.json",
                                mime="application/json"
                            )
                        
                    else:
                        st.error(f"❌ Error generando comparación: {comparison_response.get('error', 'Error desconocido')}")
                else:
                    st.error(f"❌ Error del servidor: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Tiempo de espera agotado. La comparación puede estar tardando más de lo esperado.")
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")
    
    # Ejemplos de comparación
    with st.expander("💡 Ejemplos de comparaciones"):
        st.markdown("""
        **Comparación metodológica:**
        - Grupo 1: "metodología cuantitativa"
        - Grupo 2: "metodología cualitativa"
        
        **Comparación temporal:**
        - Grupo 1: "resultados del primer trimestre"
        - Grupo 2: "resultados del segundo trimestre"
        
        **Comparación conceptual:**
        - Grupo 1: "ventajas del enfoque A"
        - Grupo 2: "ventajas del enfoque B"
        
        **Comparación de perspectivas:**
        - Grupo 1: "opinión de expertos"
        - Grupo 2: "datos estadísticos"
        """)
    
    with st.expander("🔧 Cómo funciona la comparación"):
        st.markdown("""
        1. **Búsqueda dirigida**: Se buscan fragmentos relevantes para cada consulta
        2. **Agrupación**: Los fragmentos se organizan en dos grupos basados en las consultas
        3. **Análisis con IA**: El modelo de lenguaje analiza ambos grupos
        4. **Comparación estructurada**: Se genera un análisis que incluye:
           - Similitudes encontradas
           - Diferencias clave identificadas
           - Aspectos complementarios
           - Conclusiones del análisis comparativo
        """)
    
    # Consejos de uso
    with st.expander("📝 Consejos para mejores comparaciones"):
        st.markdown("""
        **Para obtener mejores resultados:**
        - Sé específico en las descripciones de búsqueda
        - Usa términos clave relevantes de tus documentos
        - Considera diferentes perspectivas del mismo tema
        - Experimenta con diferentes enfoques de comparación
        
        **Ejemplos de términos efectivos:**
        - Nombres de metodologías, teorías o conceptos específicos
        - Fechas, períodos o fases temporales
        - Tipos de datos o evidencia
        - Diferentes stakeholders o perspectivas
        """)

def advanced_summary_page():
    """Página para resumen avanzado de documentos"""
    st.header("📊 Resumen Avanzado de Documentos")
    
    # Verificar tipos de resumen disponibles
    try:
        types_response = requests.get(f"{API_BASE_URL}/api/chat/summarize/types", timeout=5)
        if types_response.status_code == 200:
            types_data = types_response.json()
            summary_types = types_data.get("summary_types", {})
        else:
            summary_types = {}
    except:
        summary_types = {}
    
    # Configuración del resumen
    st.subheader("⚙️ Configuración del Resumen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Selección de tipo de resumen
        summary_type = st.selectbox(
            "Tipo de Resumen:",
            options=list(summary_types.keys()) if summary_types else ["comprehensive", "executive", "technical", "bullet_points"],
            format_func=lambda x: summary_types.get(x, {}).get("name", x.title()) if summary_types else x.title(),
            help="Selecciona el tipo de resumen que mejor se adapte a tus necesidades"
        )
        
        # Mostrar descripción del tipo seleccionado
        if summary_types and summary_type in summary_types:
            type_info = summary_types[summary_type]
            st.info(f"**{type_info.get('name', '')}**: {type_info.get('description', '')}")
            st.markdown(f"*Recomendado para: {type_info.get('recommended_for', '')}*")
    
    with col2:
        # Configuraciones adicionales
        max_tokens = st.slider(
            "Longitud máxima (tokens):",
            min_value=200,
            max_value=1500,
            value=800,
            step=50,
            help="Controla la longitud del resumen generado"
        )
        
        # Opción para documentos específicos (placeholder)
        st.markdown("**Documentos a resumir:**")
        all_documents = st.checkbox("Todos los documentos en la base de datos", value=True)
        
        if not all_documents:
            st.info("💡 Función de selección específica de documentos próximamente")
    
    # Botón para generar resumen
    if st.button("📝 Generar Resumen Avanzado", type="primary"):
        with st.spinner(f"Generando resumen {summary_type}... Esto puede tomar unos momentos."):
            try:
                # Preparar request
                request_data = {
                    "summary_type": summary_type,
                    "max_tokens": max_tokens
                }
                
                # Si no se seleccionan todos los documentos, se puede agregar document_ids
                if not all_documents:
                    request_data["document_ids"] = []  # Lista vacía por ahora
                
                # Hacer request al endpoint avanzado
                response = requests.post(
                    f"{API_BASE_URL}/api/chat/summarize/advanced",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get("success", False):
                        st.success("✅ Resumen generado exitosamente!")
                        
                        # Mostrar estadísticas del resumen
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📄 Documentos", result.get("documents_processed", 0))
                        with col2:
                            st.metric("🔤 Tokens usados", result.get("tokens_used", 0))
                        with col3:
                            st.metric("🤖 Método", result.get("method", "Unknown").replace("_", " ").title())
                        with col4:
                            st.metric("📋 Tipo", result.get("summary_type", "").title())
                        
                        # Mostrar el resumen
                        st.subheader(f"📋 Resumen {summary_type.title()}")
                        summary_text = result.get("summary", "")
                        st.markdown(summary_text)
                        
                        # Botón para descargar
                        if summary_text:
                            st.download_button(
                                label="💾 Descargar Resumen",
                                data=summary_text,
                                file_name=f"resumen_{summary_type}_{result.get('documents_processed', 0)}_docs.txt",
                                mime="text/plain"
                            )
                        
                        # Información adicional
                        if result.get("model_used") and result.get("model_used") != "unknown":
                            st.info(f"🤖 Modelo utilizado: {result.get('model_used')}")
                    
                    else:
                        st.error(f"❌ Error generando resumen: {result.get('error', 'Error desconocido')}")
                
                else:
                    st.error(f"❌ Error del servidor: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                st.error("⏰ Timeout: El resumen está tomando más tiempo del esperado")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Error de conexión con el backend")
            except Exception as e:
                st.error(f"❌ Error inesperado: {str(e)}")
    
    # Información sobre tipos de resumen
    if summary_types:
        st.subheader("📖 Información sobre Tipos de Resumen")
        for type_key, type_info in summary_types.items():
            with st.expander(f"📋 {type_info.get('name', type_key.title())}"):
                st.markdown(f"**Descripción:** {type_info.get('description', '')}")
                st.markdown(f"**Recomendado para:** {type_info.get('recommended_for', '')}")
    
    # Información sobre funcionalidades
    with st.expander("ℹ️ Características del Resumen Avanzado"):
        features = {
            "🤖 IA Avanzada": "Usa Llama local cuando está disponible para resúmenes sofisticados",
            "🔄 Fallback Inteligente": "Sistema de respaldo con resumen extractivo si no hay LLM",
            "📚 Multi-documento": "Puede resumir múltiples documentos simultáneamente",
            "🎯 Tipos Especializados": "Diferentes tipos de resumen para diferentes audiencias",
            "⚙️ Configurable": "Control sobre longitud y enfoque del resumen"
        }
        
        for feature, description in features.items():
            st.markdown(f"**{feature}**: {description}")

def topic_classification_page():
    """Página para clasificación de temas de documentos"""
    st.header("🏷️ Clasificación de Temas")
    
    # Obtener etiquetas disponibles
    try:
        labels_response = requests.get(f"{API_BASE_URL}/api/chat/classify/labels", timeout=5)
        if labels_response.status_code == 200:
            labels_data = labels_response.json()
            default_labels = labels_data.get("default_labels", [])
            label_categories = labels_data.get("label_categories", {})
        else:
            default_labels = []
            label_categories = {}
    except:
        default_labels = ["tecnología", "ciencia", "negocios", "salud", "educación"]
        label_categories = {}
    
    # Configuración de clasificación
    st.subheader("⚙️ Configuración de Clasificación")
    
    # Pestañas para diferentes opciones
    tab1, tab2, tab3 = st.tabs(["🏷️ Clasificación por Colección", "📄 Documento Individual", "📊 Análisis de Insights"])
    
    with tab1:
        st.subheader("📚 Clasificar Colección de Documentos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Usar etiquetas por defecto o personalizadas
            use_custom_labels = st.checkbox("Usar etiquetas personalizadas", value=False)
            
            if use_custom_labels:
                st.markdown("**Etiquetas personalizadas:**")
                custom_labels_input = st.text_area(
                    "Ingresa etiquetas separadas por comas:",
                    value=", ".join(default_labels[:5]),
                    help="Ejemplo: tecnología, medicina, educación, finanzas"
                )
                labels_to_use = [label.strip() for label in custom_labels_input.split(",") if label.strip()]
            else:
                labels_to_use = default_labels
                st.markdown("**Etiquetas por defecto:**")
                st.write(", ".join(labels_to_use))
        
        with col2:
            # Configuraciones avanzadas
            confidence_threshold = st.slider(
                "Umbral de confianza:",
                min_value=0.1,
                max_value=0.9,
                value=0.3,
                step=0.1,
                help="Clasificaciones con confianza menor serán marcadas como 'unknown'"
            )
            
            # Selección de documentos (placeholder)
            st.markdown("**Documentos a clasificar:**")
            all_docs_classify = st.checkbox("Todos los documentos", value=True, key="classify_all")
            
            if not all_docs_classify:
                st.info("💡 Selección específica próximamente")
        
        # Botón para clasificar
        if st.button("🏷️ Clasificar Documentos", type="primary", key="classify_collection"):
            with st.spinner("Clasificando documentos... Esto puede tomar unos momentos."):
                try:
                    request_data = {
                        "confidence_threshold": confidence_threshold
                    }
                    
                    if use_custom_labels and labels_to_use:
                        request_data["custom_labels"] = labels_to_use
                    
                    response = requests.post(
                        f"{API_BASE_URL}/api/chat/classify/topics",
                        json=request_data,
                        timeout=45
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get("success", False):
                            st.success("✅ Clasificación completada!")
                            
                            # Estadísticas generales
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📄 Documentos", result.get("total_documents", 0))
                            with col2:
                                st.metric("🏷️ Temas encontrados", len([t for t in result.get("topic_statistics", {}).values() if t > 0]))
                            with col3:
                                st.metric("🎯 Método", result.get("method", "unknown").replace("_", " ").title())
                            
                            # Gráfico de distribución de temas
                            topic_stats = result.get("topic_statistics", {})
                            if topic_stats:
                                st.subheader("📊 Distribución de Temas")
                                
                                # Preparar datos para gráfico
                                topics = list(topic_stats.keys())
                                counts = list(topic_stats.values())
                                
                                # Mostrar en columnas
                                cols = st.columns(min(4, len([c for c in counts if c > 0])))
                                col_idx = 0
                                for topic, count in zip(topics, counts):
                                    if count > 0:
                                        with cols[col_idx % len(cols)]:
                                            st.metric(topic.title(), count)
                                        col_idx += 1
                            
                            # Temas dominantes
                            dominant_topics = result.get("dominant_topics", [])
                            if dominant_topics:
                                st.subheader("🏆 Temas Dominantes")
                                for i, (topic, count) in enumerate(dominant_topics[:5]):
                                    percentage = (count / result.get("total_documents", 1)) * 100
                                    st.write(f"**{i+1}. {topic.title()}**: {count} documentos ({percentage:.1f}%)")
                            
                            # Clasificaciones individuales
                            classifications = result.get("classification_results", {}).get("classifications", [])
                            if classifications:
                                st.subheader("📋 Clasificaciones Individuales")
                                
                                # Filtros
                                show_all = st.checkbox("Mostrar todos los documentos", value=False)
                                if not show_all:
                                    min_confidence = st.slider("Confianza mínima a mostrar:", 0.0, 1.0, 0.3, 0.1)
                                    filtered_classifications = [c for c in classifications if c.get("confidence", 0) >= min_confidence]
                                else:
                                    filtered_classifications = classifications
                                
                                for doc_class in filtered_classifications[:10]:  # Mostrar primeros 10
                                    with st.expander(f"📄 {doc_class.get('document', 'Documento')} - {doc_class.get('primary_topic', 'unknown').title()}"):
                                        st.write(f"**Tema principal:** {doc_class.get('primary_topic', 'unknown').title()}")
                                        st.write(f"**Confianza:** {doc_class.get('confidence', 0):.2f}")
                                        
                                        # Mostrar todos los scores si están disponibles
                                        all_scores = doc_class.get('all_scores', {})
                                        if all_scores:
                                            st.write("**Puntuaciones por tema:**")
                                            for topic, score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
                                                if score > 0.1:  # Solo mostrar scores significativos
                                                    st.write(f"  - {topic.title()}: {score:.3f}")
                            
                            # Insights si están disponibles
                            insights = result.get("insights", {})
                            if insights:
                                st.subheader("💡 Insights de la Colección")
                                
                                collection_profile = insights.get("collection_profile", {})
                                if collection_profile:
                                    st.write(f"**Enfoque principal:** {collection_profile.get('primary_focus', 'Desconocido').title()}")
                                    st.write(f"**Porcentaje de enfoque:** {collection_profile.get('focus_percentage', 0):.1f}%")
                                    
                                    if collection_profile.get('is_specialized'):
                                        st.info("📚 Esta es una colección especializada")
                                    if collection_profile.get('is_diverse'):
                                        st.info("🌈 Esta colección tiene buena diversidad temática")
                                
                                diversity_analysis = insights.get("diversity_analysis", {})
                                if diversity_analysis:
                                    st.write(f"**Clasificación de diversidad:** {diversity_analysis.get('classification', 'Desconocida')}")
                                    st.write(f"**Puntuación de diversidad:** {diversity_analysis.get('diversity_score', 0):.1f}%")
                        
                        else:
                            st.error(f"❌ Error en clasificación: {result.get('error', 'Error desconocido')}")
                    
                    else:
                        st.error(f"❌ Error del servidor: {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏰ Timeout: La clasificación está tomando más tiempo del esperado")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Error de conexión con el backend")
                except Exception as e:
                    st.error(f"❌ Error inesperado: {str(e)}")
    
    with tab2:
        st.subheader("📄 Clasificar Documento Individual")
        
        # Entrada de texto
        document_content = st.text_area(
            "Ingresa el contenido del documento:",
            height=200,
            placeholder="Pega aquí el texto que deseas clasificar..."
        )
        
        if document_content.strip():
            col1, col2 = st.columns(2)
            
            with col1:
                # Configuración para documento individual
                use_custom_single = st.checkbox("Etiquetas personalizadas", value=False, key="single_custom")
                if use_custom_single:
                    custom_single_labels = st.text_input(
                        "Etiquetas (separadas por comas):",
                        value=", ".join(default_labels[:5])
                    )
                    single_labels = [label.strip() for label in custom_single_labels.split(",") if label.strip()]
                else:
                    single_labels = default_labels
            
            with col2:
                single_threshold = st.slider(
                    "Umbral de confianza:",
                    min_value=0.1,
                    max_value=0.9,
                    value=0.3,
                    step=0.1,
                    key="single_threshold"
                )
            
            if st.button("🏷️ Clasificar Texto", type="primary", key="classify_single"):
                with st.spinner("Clasificando contenido..."):
                    try:
                        params = {
                            "content": document_content,
                            "confidence_threshold": single_threshold
                        }
                        
                        if use_custom_single and single_labels:
                            params["custom_labels"] = single_labels
                        
                        response = requests.post(
                            f"{API_BASE_URL}/api/chat/classify/single",
                            params=params,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            if result.get("success", False):
                                st.success("✅ Texto clasificado!")
                                
                                # Resultado principal
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("🏷️ Tema principal", result.get("primary_topic", "unknown").title())
                                with col2:
                                    st.metric("🎯 Confianza", f"{result.get('confidence', 0):.2f}")
                                with col3:
                                    st.metric("📏 Caracteres", result.get("content_length", 0))
                                
                                # Razón de la clasificación
                                if result.get("reason"):
                                    st.info(f"💭 **Razón:** {result.get('reason')}")
                                
                                # Puntuaciones detalladas
                                scores = result.get("scores", {})
                                if scores:
                                    st.subheader("📊 Puntuaciones por Tema")
                                    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                                    
                                    for topic, score in sorted_scores:
                                        if score > 0.05:  # Solo mostrar scores relevantes
                                            progress_val = min(score, 1.0)
                                            st.write(f"**{topic.title()}**")
                                            st.progress(progress_val)
                                            st.write(f"Puntuación: {score:.3f}")
                                            st.write("")
                            
                            else:
                                st.error(f"❌ Error: {result.get('error', 'Error desconocido')}")
                        
                        else:
                            st.error(f"❌ Error del servidor: {response.status_code}")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.subheader("📊 Análisis de Insights")
        st.info("💡 Ejecuta primero una clasificación por colección para ver insights detallados")
        
        # Información sobre qué insights se pueden obtener
        with st.expander("🔍 ¿Qué insights puedes obtener?"):
            st.markdown("""
            **Perfil de la Colección:**
            - Tema principal y su porcentaje de dominancia
            - Si la colección es especializada o diversa
            - Distribución temática general
            
            **Análisis de Diversidad:**
            - Puntuación de diversidad (0-100%)
            - Clasificación cualitativa de la diversidad
            - Número de temas presentes
            
            **Recomendaciones:**
            - Sugerencias basadas en la distribución temática
            - Identificación de posibles mejoras
            - Orientación para análisis adicionales
            """)
    
    # Información sobre categorías de etiquetas
    if label_categories:
        st.subheader("📂 Categorías de Etiquetas Disponibles")
        for category, labels in label_categories.items():
            with st.expander(f"📁 {category.title()}"):
                st.write(", ".join(labels))
    
    # Información sobre funcionalidades
    with st.expander("ℹ️ Características de Clasificación"):
        st.markdown("""
        **🤖 Métodos de Clasificación:**
        - **LLM Local**: Usa Llama para clasificación inteligente cuando está disponible
        - **Palabras Clave**: Sistema de respaldo basado en coincidencias de palabras clave
        - **HuggingFace**: Zero-shot classification (en desarrollo futuro)
        
        **🎯 Características:**
        - Etiquetas personalizables para dominios específicos
        - Control de umbral de confianza
        - Análisis de insights automático
        - Estadísticas detalladas de distribución
        - Clasificación individual o por lotes
        """)

if __name__ == "__main__":
    main()
