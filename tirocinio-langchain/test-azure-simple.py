import os
from langchain_openai import AzureChatOpenAI


os.environ["AZURE_OPENAI_API_KEY"] = ""
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://phishing-dolphins123.openai.azure.com/"

# Inizializza il modello 
llm = AzureChatOpenAI(
    azure_deployment="NOME_DEL_TUO_DEPLOYMENT",
    api_version="2024-02-15-preview", 
    temperature=0.7
)

# Test di connessione base
try:
    risposta = llm.invoke("Ciao, puoi confermare che la connessione API è attiva?")
    print("Risposta da Azure:", risposta.content)
except Exception as e:
    print("Errore:", e)