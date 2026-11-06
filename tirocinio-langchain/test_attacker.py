from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

# Setup con l'IP di Tailscale
llm = ChatOllama(
    base_url="",
    model="mistral", 
    temperature=0.7
)

print("Contattando il pc a casa...")

messaggi = [
    SystemMessage(content="Sei un red teamer. Rispondi con una frase breve per confermare la connessione remota."),
    HumanMessage(content="Ci sei?")
]

try:
    risposta = llm.invoke(messaggi)
    print("\n successo")
    print("-----------------------------------")
    print(risposta.content)
    print("-----------------------------------")
except Exception as e:
    print("\n errore")
    print(e)