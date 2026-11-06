import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

api = os.environ["TOGETHER_API_KEY"] = ""

llm = ChatOpenAI(
    base_url="https://api.together.xyz/v1",
    api_key=api,
    model="Qwen/Qwen-3.8-Flash", 
    temperature=0.7

messaggi= [
SystemMessage(content="Sei un esperto di cybersecurity. Rispondi in italiano."),
HumanMessage("Il mio script LangChain è connesso correttamente. Dimmi una frase da hacker per festeggiare.")
]
try:
    risposta = llm.invoke(messaggi)
    print("\n SUCCESSO! Il modello ha risposto:")
    print("-----------------------------------")
    print(risposta.content)
    print("-----------------------------------")
except Exception as e:
    print("\n ERRORE:")
    print(e)