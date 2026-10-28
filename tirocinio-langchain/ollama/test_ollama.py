import json
from datetime import datetime

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph
from typing import TypedDict

# Definisci lo stato della conversazione
class EmailState(TypedDict):
    attacker_email: str
    defender_response: str
    conversation_history: list

# Inizializza Ollama con Mistral
attacker_llm = ChatOllama(
    base_url="http://100.72.54.78:11434",  # l'IP del tuo Tailscale
    model="mistral",
    temperature=0.7
)

defender_llm = ChatOllama(
    base_url="http://100.72.54.78:11434",  # stesso IP
    model="mistral",
    temperature=0.7
)
# Nodo 1: Attaccante genera un'email di phishing
def attacker_node(state: EmailState) -> EmailState:
    """L'attaccante genera un'email di social engineering"""
    prompt = """Genera un'email di phishing convincente che simula una richiesta 
dell'azienda. L'email deve contenere urgenza, minacce o richieste di azione.
Rispondi solo con il corpo dell'email."""
    
    print("→ Attaccante genera email...")
    response = attacker_llm.invoke(prompt)
    state["attacker_email"] = response.content
    state["conversation_history"].append({
        "role": "attacker",
        "timestamp": datetime.now().isoformat(),
        "message": response.content
    })
    print("✓ Email generata")
    return state

# Nodo 2: Difensore legge l'email e risponde
def defender_node(state: EmailState) -> EmailState:
    """Difensore - segretario senza training in cybersecurity"""
    prompt = f"""Sei un segretario amministrativo di una PMI. Non hai formazione in cybersecurity 
e tendi a fidarti dei messaggi ufficiali. Leggi velocemente le email perché hai fretta.

Email ricevuta:
{state['attacker_email']}

Rispondi naturalmente se è legittima o sospetta. Sii breve."""
    
    print("→ Difensore legge email...")
    response = defender_llm.invoke(prompt)
    state["defender_response"] = response.content
    state["conversation_history"].append({
        "role": "defender",
        "timestamp": datetime.now().isoformat(),
        "message": response.content
    })
    print("✓ Risposta ricevuta")
    return state

# Costruisci il grafo
graph = StateGraph(EmailState)
graph.add_node("attacker", attacker_node)
graph.add_node("defender", defender_node)
graph.add_edge("attacker", "defender")
graph.set_entry_point("attacker")
app = graph.compile()

# Esegui la simulazione
initial_state = {
    "attacker_email": "",
    "defender_response": "",
    "conversation_history": []
}

print("Inizio simulazione con Ollama/Mistral...\n")
final_state = app.invoke(initial_state)

print("\n=== EMAIL DELL'ATTACCANTE ===")
print(final_state["attacker_email"])
print("\n=== RISPOSTA DEL DIFENSORE ===")
print(final_state["defender_response"])

with open("phishing_log_ollama.json", "w", encoding="utf-8") as f:
    json.dump(final_state["conversation_history"], f, indent=2, ensure_ascii=False)

print("\n✓ Simulazione salvata in phishing_log_ollama.json")