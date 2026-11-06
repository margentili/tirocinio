import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


os.environ["VENICE_API_KEY"] = ""

# 2. CONFIGURAZIONE DEL MODELLO PER OPENROUTER
llm = ChatOpenAI(
    base_url="https://api.venice.ai/api/v1",
    api_key=os.environ["VENICE_API_KEY"],
    model="olafangensan-glm-4.7-flash-heretic",
    temperature=0.7
)

# 3. TEST DI CONNESSIONE
print("Contattando OpenRouter...")

messaggi = [
    SystemMessage(content="Sei un hacker. Rispondi in italiano con una frase a tema cybersecurity per festeggiare il successo del test."),
    HumanMessage(content="Ciao! Il mio script LangChain è online.")
]

try:
    risposta = llm.invoke(messaggi)
    print("\n✅ SUCCESSO! Il modello ha risposto:")
    print("-----------------------------------")
    print(risposta.content)
    print("-----------------------------------")
except Exception as e:
    print("\n❌ ERRORE:")
    print(e)