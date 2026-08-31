import os
import streamlit as st
from google import genai

# Configuración básica de la página web
st.set_page_config(page_title="Tutor IA del Curso", page_icon="🤖")
st.title("🤖 Asistente del Curso de IA")
st.caption("Escribe tu duda o pregunta para interactuar con la IA.")

# Obtener la API Key guardada de forma segura
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Error: La API Key no está configurada correctamente.")
    st.stop()

# Inicializar el cliente oficial de Gemini
client = genai.Client(api_key=api_key)

# Definir las instrucciones del sistema (System Prompt) para adecuar el comportamiento a menores
SYSTEM_PROMPT = (
    "Eres un tutor educativo amable, paciente y didáctico para niños de entre 12 y 14 años. "
    "Tu objetivo es explicar conceptos de forma sencilla y fomentar la curiosidad. "
    "No des respuestas directamente si te piden hacer la tarea; en su lugar, guía al alumno paso a paso. "
    "Rechaza tajantemente responder a contenidos violentos, explícitos, de acoso o inapropiados para menores."
)

# Guardar el historial de chat en la sesión del usuario
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial de conversación en la pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de texto para el alumno
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Guardar y mostrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparar el historial en el formato requerido por la API
    contents = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    # Llamada a la API de Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config={"system_instruction": SYSTEM_PROMPT}
            )
            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Ocurrió un error al procesar tu solicitud: {e}")
