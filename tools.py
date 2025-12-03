from crewai_tools import SerperDevTool
from dotenv import load_dotenv
import os

load_dotenv()

os.environ['SERPER_API_KEY'] = os.getenv('SERPER_API_KEY')
serp_tool = SerperDevTool()   

from langchain_openai import OpenAIEmbeddings
embed_model = OpenAIEmbeddings(model="text-embedding-3-small")

def embedding_tool(text_list):
    return embed_model.embed_documents(text_list)

from langchain_community.vectorstores import Chroma

_vectorstore = None

def vectorstore_create(chunks, embeddings):
    global _vectorstore
    _vectorstore = Chroma.from_embeddings(
        embeddings=embeddings,
        texts=chunks
    )
    return "vectorstore_created"

def vectorstore_query(query_embedding, top_k=5):
    if _vectorstore is None:
        return []
    docs = _vectorstore.similarity_search_by_vector(query_embedding, k=top_k)
    return [{"text": d.page_content, "source": d.metadata} for d in docs]

vectorstore_tool = {"create": vectorstore_create, "query": vectorstore_query}

def seo_keyword_tool(topic):
    return {
        "main": topic,
        "keywords": [
            topic,
            f"{topic} guide",
            f"{topic} tips",
            f"{topic} examples",
            f"{topic} best practices"
        ]
    }

def seo_score_tool(content):
    score = 70
    words = len(content.split())

    if words > 700: score += 10
    if "H2" in content or "H3" in content: score += 5

    suggestions = [
        "Add more keyword-rich headings.",
        "Add outbound authoritative links.",
        "Write a meta description of 120-155 characters."
    ]

    return {"score": score, "suggestions": suggestions}

def prompt_template_tool(format="blog", tone="professional"):
    return f"Write a {format} in a {tone} tone using the research and citations."

def style_check_tool(text):
    words = len(text.split())
    suggestions = []
    if words < 50:
        suggestions.append("Consider expanding the introduction for clarity.")
    if words > 1200:
        suggestions.append("Consider splitting long sections with H2/H3 headings.")
    return {"suggestions": suggestions}
