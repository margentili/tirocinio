import os
from langchain_ollama import ChatOllama
llm = ChatOllama(
    base_url="http://100.72.54.78:11434",
    model = "mistral",
    temperature = 0.7)

response = llm.invoke("Ciao, mi confermi che funzioni?")
print(response.content)
