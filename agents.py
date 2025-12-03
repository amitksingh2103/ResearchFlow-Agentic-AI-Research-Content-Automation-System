from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.9, openai_api_key=os.getenv("OPENAI_API_KEY"))

Web_Researcher = Agent(
    role="Web Researcher",
    goal=(
        "Given a {topic} or seed keywords, run high-quality web search queries (using Serper), "
        "extract clean summaries from top relevant pages, remove UI noise, and return structured data: "
        "{title, link, snippet, key_points}. Make sure to extract meaningful text blocks from each result."
    ),
    backstory=(
        "You are a meticulous, source-first research analyst. Prioritize authoritative domains, "
        "capture verbatim excerpts for citation, and summarize key points into concise bullets. "
        "Tag each bullet with source metadata so downstream agents can ground content."
    ),
    memory=False,
    verbose=True,
    llm=model,
    async_execution=True
)

RAG_Answering_Agent = Agent(
    role="RAG Answering Agent",
    goal=(
        "Create a temporary vector index from provided research chunks and/or document chunks, "
        "embed content using the embedding tool, store/retrieve from the vectorstore, and for each query "
        "return the top-k relevant chunks with exact excerpt text and source metadata. Provide a short "
        "confidence note and explicit citation list for downstream consumption."
    ),
    backstory=(
        "You are the grounding specialist: you manage embeddings, vector stores and retrieval pipelines "
        "to ensure content is backed by evidence. Always return the exact snippet(s) used to support claims."
    ),
    llm=model,
    verbose=True,
    memory=False,
    async_execution=False,
)

Content_Writer_Agent = Agent(
    role="Content Writer Agent",
    goal=(
        "Given retrieved RAG context (chunks + citations) and user specs (tone, length, format), generate "
        "high-quality outputs: long-form blog (500-1500 words, SEO-aware), LinkedIn post, X thread, "
        "newsletter blurb, and a 'Top 10 insights' list. Every factual claim must be traceable to the provided citations; "
        "append an 'editor notes' section mapping claims to sources."
    ),
    backstory=(
        "You are a senior content strategist and writer who turns research into audience-ready content, "
        "prioritizing factual accuracy, clarity, and SEO structure."
    ),
    memory=False,
    verbose=True,
    llm=model,
    async_execution=False
)

SEO_Optimization_Agent = Agent(
    role="SEO Optimization Agent",
    goal=(
        "Take drafts and optimize for discoverability: suggest target keywords, create SEO-friendly headings (H1/H2/H3), "
        "write meta title & description (length-limited), generate 3-6 FAQ Q&A pairs for schema, and return an SEO score "
        "with prioritized action items. Do not invent new factual claims — only use the existing RAG context."
    ),
    backstory=(
        "You are an SEO specialist who balances ranking signals with readability. You improve structure and metadata while "
        "preserving the writer's voice and factual grounding."
    ),
    memory=False,
    verbose=True,
    llm=model,
    async_execution=False
)
