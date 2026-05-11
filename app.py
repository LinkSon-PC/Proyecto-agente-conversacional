#!pip install -U langchain

#!pip install langchain-google-genai

#!pip install python-dotenv

import math
import os

# Install Gradio
#!pip install -qU gradio
import gradio as gr
from dotenv import load_dotenv
from google.auth.exceptions import GoogleAuthError
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.tools import tool

#!pip install -qU ddgs langchain-community
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

GEMINI_API_KEY_LOADED_SUCCESSFULLY = False
if "GEMINI_API_KEY" in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
    GEMINI_API_KEY_LOADED_SUCCESSFULLY = True
else:
    print(
        "Warning: 'GEMINI_API_KEY' not found in environment variables. Please set it to use the Gemini model."
    )

# Create a LangChain Tool from the DuckDuckGoSearchRun instance

# Initialize the DuckDuckGoSearchRun instance
ddg_search_runner = DuckDuckGoSearchRun()


# Create a LangChain Tool from the DuckDuckGoSearchRun instance
@tool(
    "search_web",
    description="Use this tool to search the internet for general knowledge or current events.",
)
def search(query: str) -> str:
    """
    Search the web for the given query using DuckDuckGo.

    Args:
        query (str): The search query string to look up on the internet.

    Returns:
        str: The search results from DuckDuckGo, or an error message if the search fails.
    """
    try:
        return ddg_search_runner.run(query)
    except Exception as e:
        return f"Error al realizar la búsqueda web: {e}. Por favor, intente con una consulta diferente o verifique su conexión."


@tool(
    "calculator",
    description="Performs arithmetic calculations. Use this for any math problems.",
)
def calc(expression: str) -> str:
    """
    Evaluate mathematical expressions safely using eval with restricted globals.

    Args:
        expression (str): A string containing a valid mathematical expression.

    Returns:
        str: The result of the evaluation as a string, or an error message if evaluation fails.
    """
    # Define a safe global dictionary for eval, making math.sqrt available as sqrt()
    safe_globals = {
        "__builtins__": {},  # Restrict built-ins for security
        "math": math,  # Keep math module available if user uses math. prefix
        "sqrt": math.sqrt,  # Make sqrt directly accessible without 'math.' prefix
    }

    try:
        result = eval(expression, safe_globals)
        return str(result)
    except Exception as e:
        return f"Error: {e}. Please ensure the expression is valid."


@tool("get_weather", description="Get the current weather for a given location.")
def get_weather(city: str) -> str:
    """
    Get the current weather for a given city.

    Note: This is a placeholder implementation that always returns sunny weather.

    Args:
        city (str): The name of the city to get weather for.

    Returns:
        str: A string indicating the weather in the specified city.
    """
    return f"It's always sunny in {city}!"


# Configura el modelo Gemini con la temperatura y el máximo de tokens deseados
if GEMINI_API_KEY_LOADED_SUCCESSFULLY:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",  # Puedes usar 'gemini-pro' o 'gemini-1.5-flash' u otro modelo disponible
        temperature=0.7,  # Un valor entre 0.0 (determinista) y 1.0 (creativo)
        max_output_tokens=800,  # Número máximo de tokens en la respuesta
    )
    print("Gemini LLM inicializado correctamente.")
else:
    llm = None
    print(
        "Gemini LLM no inicializado porque la clave API no fue cargada. Asegúrate de que 'GEMINI_API_KEY' esté configurada en los secretos."
    )

# La SummarizationMiddleware también usa un modelo.
# Si quieres configurar su temperatura y max_output_tokens también,
# deberías instanciar otro ChatGoogleGenerativeAI para ella.
# Por ahora, la dejaremos con la configuración por defecto de 'gemini-2.5-flash-lite'.

checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,  # Usamos la instancia 'llm' configurada con temperatura y max_output_tokens
    tools=[get_weather, search, calc],
    checkpointer=checkpointer,  # This uses the InMemorySaver for checkpointing
    middleware=[
        SummarizationMiddleware(
            model="google_genai:gemini-2.5-flash-lite",  # Puedes configurar un modelo específico para la summarización aquí si es necesario
            trigger=("tokens", 2000),
            keep=("messages", 20),
        )
    ],
    system_prompt="You are a helpful assistant",
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}


"""### Interfaz de Chat con Gradio

Ahora, crearemos una función que el Gradio ChatInterface usará para interactuar con el agente. Esta función tomará el mensaje del usuario y el historial de chat, invocará al agente y devolverá la respuesta del agente junto con el historial actualizado.
"""


def chat_with_agent(message, history):
    """
    Handle chat interaction with the LangChain agent for Gradio ChatInterface.

    This function processes user messages and chat history, converts them to LangChain format,
    invokes the agent, and returns the agent's response. It handles API key validation and
    various exceptions.

    Args:
        message (str): The current user message.
        history (list): List of previous chat exchanges, each as [human_message, ai_message].

    Returns:
        str: The agent's response to the user's message, or an error message if something fails.
    """
    global config  # Ensure config (thread_id) is accessible
    global GEMINI_API_KEY_LOADED_SUCCESSFULLY  # Access the global flag

    if not GEMINI_API_KEY_LOADED_SUCCESSFULLY:
        return "Lo siento, la clave API de Gemini ('GEMINI_API_KEY') no está configurada. Por favor, añádela a los secretos para que el agente funcione."

    langchain_messages = []
    # Gradio history is a list of lists: [[user_msg, bot_msg], ...]
    # Convert Gradio history to LangChain message format for the agent
    for i, item in enumerate(history):
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            print(
                f"Warning: History item at index {i} is not a valid [human, ai] pair and will be skipped: {item}"
            )
            continue

        human, ai = item
        if human:
            langchain_messages.append(HumanMessage(content=human))
        if ai:
            langchain_messages.append(AIMessage(content=ai))

    # Add the current user message
    langchain_messages.append(HumanMessage(content=message))

    try:
        # Invoke the agent
        response = agent.invoke({"messages": langchain_messages}, config)

        # Extract the agent's latest response
        agent_response = response["messages"][-1].content
    except GoogleAuthError:
        agent_response = "Lo siento, parece que hay un problema de autenticación con tu clave API de Gemini. Por favor, verifica que la clave sea válida y esté configurada correctamente en los secretos de Colab."
    except Exception as e:
        agent_response = f"Lo siento, ha ocurrido un error al procesar tu solicitud: {e}. Asegúrate de que la clave API de Gemini está configurada correctamente."

    # For this example, we'll just return the final AI message content.
    # The Gradio `ChatInterface` automatically handles appending the user's message
    # and then expects our function to return the agent's response for that last message.

    return agent_response


"""### Lanzar la Interfaz de Chat

Finalmente, creamos y lanzamos la interfaz de Gradio.
"""

iface = gr.ChatInterface(
    fn=chat_with_agent,
    chatbot=gr.Chatbot(height=400),
    textbox=gr.Textbox(
        placeholder="Escribe tu mensaje aquí...", container=False, scale=7
    ),
    title="Agente Conversacional con LangChain y Gradio",
    description="Interactúa con el agente LangChain usando esta interfaz de chat impulsada por Gradio. Puedes preguntar sobre tu nombre, poemas, e investigar temas en la web.",
    examples=[
        "Hi, my name is Alice",
        "Write a short poem about the ocean",
        "How is the weather in Guatemala City",
        "What is the square root of 2?",
    ],
    cache_examples=True,
)

iface.launch(debug=True, share=True)
