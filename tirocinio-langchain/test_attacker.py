from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

# Setup con l'IP di Tailscale
llm = ChatOllama(
    base_url="http://100.72.54.78:11434", # Metti qui l'IP del fisso
    model="mistral", 
    temperature=0.7
)

print("Contattando la belva a casa...")

messaggi = [
    SystemMessage(content="Sei un red teamer. Rispondi con una frase breve per confermare la connessione remota."),
    HumanMessage(content="Ci sei?")
]

try:
    risposta = llm.invoke(messaggi)
    print("\n✅ SUCCESSO! Il fisso ha risposto al portatile:")
    print("-----------------------------------")
    print(risposta.content)
    print("-----------------------------------")
except Exception as e:
    print("\n❌ ERRORE:")
    print(e)