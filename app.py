import os
import requests
import streamlit as st

# Configuración básica de la página
st.set_page_config(page_title="Tutor IA del Curso", page_icon="🤖")
st.title("🤖 Asistente del Curso de IA")
st.caption("Escribe tu duda o pregunta para interactuar con la IA.")

# Obtener la API Key desde los Secrets de Streamlit
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Error: No se ha encontrado la clave GEMINI_API_KEY en los Secrets.")
    st.stop()

# Instrucciones del sistema para adaptar la IA a niños de 12 a 14 años
SYSTEM_PROMPT = (
    "Eres un tutor educativo amable, paciente y didáctico para niños de entre 12 y 14 años. "
    "Explica conceptos de forma sencilla y fomenta la curiosidad. "
    "No des respuestas directas a deberes; guía al alumno paso a paso. "
    "Rechaza responder a contenidos inapropiados para menores."
)

# Inicializar historial de conversación
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar conversación anterior
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada de texto del usuario
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparar los contenidos para enviarlos a la API
    contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    # Enlace con el modelo activo (gemini-2.5-flash)
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
                error_msg = data.get("error", {}).get("message", "Error desconocido en la API.")
                st.error(f"Error de conexión ({response.status_code}): {error_msg}")
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")
