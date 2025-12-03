from crewai import Crew, Process
from agents import (
    Web_Researcher,
    RAG_Answering_Agent,
    Content_Writer_Agent,
    SEO_Optimization_Agent
)
from tasks import (
    research_task,
    rag_answering_task,
    content_writing_task,
    seo_optimization_task
)

research_crew = Crew(
    agents=[
        Web_Researcher,
        RAG_Answering_Agent,
        Content_Writer_Agent,
        SEO_Optimization_Agent
    ],
    tasks=[
        research_task,
        rag_answering_task,
        content_writing_task,
        seo_optimization_task
    ],
    process=Process.sequential
)

