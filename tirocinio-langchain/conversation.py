import os
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage

# Inizializza il modello
llm = ChatOllama(
    base_url="http://100.72.54.78:11434",  # l'IP del tuo Tailscale
    model="mistral",
    temperature=0.7
)

# Lista che mantiene la storia della conversazione
chat_history = []

def chat(user_input):
    """Aggiunge il messaggio dell'utente e genera una risposta"""
    # Aggiungi il messaggio dell'utente alla storia
    chat_history.append(HumanMessage(content=user_input))
    
    # Genera la risposta usando tutta la storia
    response = llm.invoke(chat_history)
    
    # Aggiungi la risposta alla storia
    chat_history.append(AIMessage(content=response.content))
    
    return response.content

# Test della conversazione
print("Inizio conversazione (scrivi 'exit' per uscire):\n")

while True:
    user_input = input("Tu: ").strip()
    
    if user_input.lower() == "exit":
        break
    
    if not user_input:
        continue
    
    response = chat(user_input)
    print(f"AI: {response}\n")