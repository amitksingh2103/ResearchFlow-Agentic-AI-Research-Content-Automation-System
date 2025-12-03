from crewai import Task
from agents import Web_Researcher, Content_Writer_Agent, SEO_Optimization_Agent, RAG_Answering_Agent
from tools import (
    serp_tool,
    embedding_tool,
    vectorstore_tool,
    style_check_tool,
    prompt_template_tool,
    seo_keyword_tool,
    seo_score_tool
)

research_task = Task(
    description="Search the web for the provided {topic}; return structured source records (title, link, snippet, key_points).",
    expected_output="List[dict] where each dict has: title, link, snippet, key_points",
    agent=Web_Researcher
)

rag_answering_task = Task(
    description="Take the researcher's extracted text chunks, create embeddings, build a temporary vectorstore, and provide a retrieval endpoint for top-k relevant chunks for a query.",
    expected_output="On build: {'status':'vectorstore_created','num_chunks':int}. On query: List[dict]{'text','metadata'}.",
    agent=RAG_Answering_Agent,
)

content_writing_task = Task(
    description="Using retrieved RAG context + user specs (tone, length, format), produce: blog, LinkedIn post, X thread, newsletter blurb, and Top 10 insights. Include editor notes mapping claims to sources.",
    expected_output="Dict with keys: blog, linkedin, x_thread, newsletter, top10, editor_notes",
    agent=Content_Writer_Agent,
)

seo_optimization_task = Task(
    description="Optimize the selected draft for SEO: suggest target keywords, H1/H2/H3 headings, meta title & description, 3-6 FAQ Q&A pairs, and an SEO score with action items.",
    expected_output="Dict with keys: meta_title, meta_description, headings, faq_schema, seo_score, suggestions",
    agent=SEO_Optimization_Agent,
    output_file="Content.md"
)
