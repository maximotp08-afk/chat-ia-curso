import os
import streamlit as st
import google.generativeai as genai

# Configuración de la página web
st.set_page_config(page_title="Tutor IA del Curso", page_icon="🤖")
st.title("🤖 Asistente del Curso de IA")
st.caption("Escribe tu duda o pregunta para interactuar con la IA.")

# Obtener la clave de API desde las variables de entorno de Streamlit
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("Error: La API Key no está configurada en los Secrets de Streamlit.")
    st.stop()

# Configurar el cliente de Google Gemini
genai.configure(api_key=api_key)

# Instrucciones del sistema para adaptar la IA a menores
SYSTEM_PROMPT = (
    "Eres un tutor educativo amable, paciente y didáctico para niños de entre 12 y 14 años. "
    "Tu objetivo es explicar conceptos de forma sencilla y fomentar la curiosidad. "
    "No des respuestas directamente si te piden hacer la tarea; en su lugar, guía al alumno paso a paso. "
    "Rechaza tajantemente responder a contenidos violentos, explícitos, de acoso o inapropiados para menores."
)

# Inicializar el modelo actualizado
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT
)

# Mantener el historial de la conversación en la sesión
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Mostrar mensajes anteriores en pantalla
for message in st.session_state.chat_session.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Entrada de texto para el alumno
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Mostrar el mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)

    # Enviar la respuesta y mostrarla
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = st.session_state.chat_session.send_message(prompt)
            message_placeholder.markdown(response.text)
        except Exception as e:
            st.error(f"Error al procesar la solicitud: {e}")
