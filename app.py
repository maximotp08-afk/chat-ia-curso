import os
import requests
import base64
import streamlit as st

st.set_page_config(page_title="Tutor IA del Curso", page_icon="🤖")
st.title("🤖 Asistente del Curso de IA")
st.caption("Escribe tu duda o sube una imagen para interactuar con la IA.")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("Error: No se ha encontrado la clave GEMINI_API_KEY en los Secrets.")
    st.stop()

SYSTEM_PROMPT = (
    "Eres un tutor educativo amable, paciente y didáctico para niños de entre 12 y 14 años. "
    "Explica conceptos de forma sencilla y fomenta la curiosidad. "
    "No des respuestas directas a deberes; guía al alumno paso a paso. "
    "Rechaza responder a contenidos inapropiados para menores."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Botón para subir imágenes
uploaded_file = st.file_uploader("Adjuntar captura o imagen (opcional)", type=["png", "jpg", "jpeg"])

# Mostrar conversación anterior
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image_bytes" in msg:
            st.image(msg["image_bytes"], width=300)
        st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Guardar datos del usuario
    user_data = {"role": "user", "content": prompt}
    
    # Procesar imagen si se ha subido
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        user_data["image_bytes"] = file_bytes
        user_data["image_b64"] = base64.b64encode(file_bytes).decode("utf-8")
        user_data["mime_type"] = uploaded_file.type

    st.session_state.messages.append(user_data)
    
    with st.chat_message("user"):
        if uploaded_file is not None:
            st.image(file_bytes, width=300)
        st.markdown(prompt)

    # Preparar el historial para la API
    contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        parts = [{"text": msg["content"]}]
        
        # Añadir la imagen al payload de la API
        if "image_b64" in msg:
            parts.append({
                "inline_data": {
                    "mime_type": msg["mime_type"],
                    "data": msg["image_b64"]
                }
            })
            
        contents.append({"role": role, "parts": parts})

    # AQUÍ ESTÁ LA LÍNEA CORRECTA QUE ARREGLAMOS ANTES
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": contents
    }

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            data = response.json()
            
            if response.status_code == 200:
                answer = data["candidates"][0]["content"]["parts"][0]["text"]
                message_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                error_msg = data.get("error", {}).get("message", "Error desconocido.")
                st.error(f"Error de conexión ({response.status_code}): {error_msg}")
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")
