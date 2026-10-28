import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

api = os.environ["TOGETHER_API_KEY"] = "key_CfW9QHWF4pf2gDLng7gpj"

llm = ChatOpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=api,
    # Se la stringa esatta del modello ti dà errore, controlla sulla dashboard di Together 
    # la voce "API string" del modello scelto. Di solito per Qwen è simile a questa:
    model="Qwen/Qwen-3.8-Flash", 
    temperature=0.7 # Un po' di creatività per l'attaccante
)

messaggi= [
SystemMessage(content="Sei un esperto di cybersecurity. Rispondi in italiano."),
HumanMessage("Il mio script LangChain è connesso correttamente. Dimmi una frase da hacker per festeggiare.")
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