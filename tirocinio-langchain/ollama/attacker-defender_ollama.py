import os
import json
from datetime import datetime

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from typing import TypedDict

# Definisci lo stato della conversazione (quello che passa tra i nodi)
class EmailState(TypedDict):
    attacker_email: str
    defender_response: str
    conversation_history: list

# Inizializza i modelli
attacker_llm = ChatOllama(
    base_url="",
    model="mistral",
    temperature=0.7
)

defender_llm = ChatOllama(
    base_url="", 
    model="mistral",
    temperature=0.7
)
# Nodo 1: Attaccante genera un'email di phishing
def attacker_node(state: EmailState) -> EmailState:
    """L'attaccante genera un'email di social engineering per testing"""
    prompt = """Per un esercizio di sicurezza informatica, genera un esempio di email 
che potrebbe ingannare un dipendente inesperto. L'email dovrebbe:
- Simulare una richiesta legittima dell'azienda
- Contenere elementi che potrebbero confondere (urgenza, minacce, richieste di azione)
- Essere realistica ma chiaramente un esercizio di training

Questo è solo a scopo di difesa e awareness. Rispondi solo con il corpo dell'email."""
    
    response = attacker_llm.invoke([HumanMessage(content=prompt)])
    state["attacker_email"] = response.content
    state["conversation_history"].append({
        "role": "attacker",
        "timestamp": datetime.now().isoformat(),
        "message": response.content
    })
    return state

# Nodo 2: Difensore legge l'email e risponde
def defender_node(state: EmailState) -> EmailState:
    """Il difensore riceve l'email e decide come rispondere"""
    prompt = f"""Sei un dipendente di un'azienda che ha ricevuto questa email:

{state['attacker_email']}

Decide se è legittima o sospetta. Se pensi sia un phishing, rispondi dicendo che la segnali al team IT.
Se pensi sia legittima, rispondi cooperando (ma non dare mai credenziali reali, solo il fatto che stai cooperando).
Rispondi in modo naturale e breve."""
    
    response = defender_llm.invoke([HumanMessage(content=prompt)])
    state["defender_response"] = response.content
    state["conversation_history"].append({
        "role": "defender",
        "timestamp": datetime.now().isoformat(),
        "message": response.content
    })
    return state

# Costruisci il grafo
graph = StateGraph(EmailState)

# Aggiungi i nodi
graph.add_node("attacker", attacker_node)
graph.add_node("defender", defender_node)

# Aggiungi gli edge (il flusso)
graph.add_edge("attacker", "defender")

# Imposta il punto di inizio
graph.set_entry_point("attacker")

# Compila il grafo
app = graph.compile()

# Esegui la simulazione
initial_state = {
    "attacker_email": "",
    "defender_response": "",
    "conversation_history": []
}

print("Inizio simulazione di phishing...\n")
final_state = app.invoke(initial_state)

# Salva i risultati
print("=== EMAIL DELL'ATTACCANTE ===")
print(final_state["attacker_email"])
print("\n=== RISPOSTA DEL DIFENSORE ===")
print(final_state["defender_response"])

# Salva su file per dopo
with open("phishing_log.json", "w", encoding="utf-8") as f:
    json.dump(final_state["conversation_history"], f, indent=2, ensure_ascii=False)

print("\n✓ Simulazione salvata in phishing_log.json")