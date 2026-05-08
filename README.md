# Proyecto Agente Conversacional

## Descripción

Este proyecto crea un agente conversacional usando LangChain, Gemini de Google y Gradio. El agente integra herramientas para realizar búsquedas web, cálculos matemáticos y respuestas de ejemplo sobre el clima.

## Funcionalidades

- Uso de `google_genai:gemini-2.5-flash-lite` como modelo de lenguaje.
- Herramienta de búsqueda en internet mediante DuckDuckGo.
- Calculadora segura para evaluar expresiones matemáticas.
- Respuesta de clima simulado para una ciudad dada.
- Interfaz web interactiva con Gradio para chatear con el agente.
- Middleware de resumen para limitar la memoria de mensajes cuando el historial crece.

## Requisitos

- Python 3.10+ recomendado
- Paquetes principales:
  - `langchain`
  - `langchain-google-genai`
  - `langchain-community`
  - `python-dotenv`
  - `gradio`
  - `langgraph`

## Configuración

1. Crea un archivo `.env` en la raíz del proyecto.
2. Añade la clave de API de Gemini:

```env
GEMINI_API_KEY=tu_api_key_aqui
```

### Variables de Entorno Necesarias

| Variable | Descripción | Requerida | Ejemplo |
|----------|-------------|-----------|---------|
| `GEMINI_API_KEY` | Clave de API de Google Gemini para usar el modelo de lenguaje | ✅ Sí | `AIwewwDxxx...` |

**Obtener la clave de API:**
- Ve a [Google AI Studio](https://aistudio.google.com/apikey)
- Crea una nueva clave de API
- Cópiala y pégala en tu archivo `.env`

3. Instala las dependencias necesarias usando `pip`:

```bash
pip install -r requirements.txt
```

O instala manualmente:

```bash
pip install -U langchain langchain-google-genai python-dotenv gradio langchain-community langgraph
```

## Uso

Ejecuta el script principal con:

```bash
python proyectoia_ml.py
```

Esto iniciará la interfaz de Gradio en tu navegador. Escribe un mensaje en la caja de chat y el agente responderá usando el modelo y sus herramientas.

## Ejemplos de uso

- "Hi, my name is Alice"
- "Write a short poem about the ocean"
- "How is the weather in Guatemala City"
- "What is the square root of 2?"

## Estructura del código

- `proyectoia_ml.py`: Script principal que carga el agente, define herramientas, crea la interfaz Gradio y lanza el chat.
- `.env`: Archivo opcional para variables de entorno como la clave de API.

## Notas

- La función `get_weather` actualmente devuelve una respuesta fija con la consulta del clima.
- La función `calc` permite realizar operaciones de cálculo.
- El agente usa un `SummarizationMiddleware` para mantener el rendimiento cuando el historial de chat crece.
- La búsqueda se realiza con DuckDuckGo a través de `DuckDuckGoSearchRun`.

## Licencia

Este proyecto puede adaptarse según las necesidades del usuario.
