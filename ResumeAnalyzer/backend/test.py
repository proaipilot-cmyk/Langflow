from langchain_mistralai import MistralAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()


emb = MistralAIEmbeddings(
    model="mistral-embed",
    api_key=os.getenv("MISTRAL_API_KEY")
)


print(emb.embed_query("hello world"))