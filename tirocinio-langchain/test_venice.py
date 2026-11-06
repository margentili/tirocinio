import os
from langchain_openai import ChatOpenAI
apikey = os.environ["TOGETHER_API_KEY"] = ""

llm = ChatOpenAI(
    model="venice-uncensored-1-2",
    api_key= apikey,
    base_url="https://api.venice.ai/api/v1",
    temperature=0.7,
)

response = llm.invoke("Ciao, mi confermi che funzioni?")
print(response.content)