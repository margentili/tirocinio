import os
from langchain_openai import AzureChatOpenAI

# Inserisci i dati che hai trovato nel portale
os.environ["AZURE_OPENAI_API_KEY"] = "EyrfMUpu3qYyeGYWkfK4AsmoKc1lQEMt8liwzXM6alGy4w8NiDkKJQQJ99CJACgEuAYXJ3w3AAABACOGWQEQ"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://phishing-dolphins123.openai.azure.com/"

# Inizializza il modello 
llm = AzureChatOpenAI(
    azure_deployment="NOME_DEL_TUO_DEPLOYMENT", # Quello che hai creato nell'AI Studio
    api_version="2024-02-15-preview", 
    temperature=0.7
)

# Test di connessione base
try:
    risposta = llm.invoke("Ciao, puoi confermare che la connessione API è attiva?")
    print("Risposta da Azure:", risposta.content)
except Exception as e:
    print("Errore:", e)