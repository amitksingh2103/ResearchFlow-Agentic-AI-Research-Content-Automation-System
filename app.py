import streamlit as st
from crew import research_crew
import io
from contextlib import redirect_stdout
import asyncio
import types
import json
import re
from typing import Any, Union

st.set_page_config(page_title="ResearchFlow", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    :root {
      --accent: #6C63FF;
      --muted: #6b7280;
      --card: #0f172a;
      --glass: rgba(255,255,255,0.03);
    }
    .page-header {
      display:flex;
      align-items:center;
      gap:16px;
      padding:18px 20px;
      border-radius:12px;
      background: linear-gradient(90deg, rgba(108,99,255,0.12), rgba(108,99,255,0.06));
      box-shadow: 0 6px 18px rgba(12,12,20,0.12);
      margin-bottom: 10px;
    }
    .title {
      font-size:22px;
      font-weight:700;
      margin:0;
    }
    .subtitle {
      margin:0;
      color:var(--muted);
      font-size:13px;
    }
    .card {
      background: var(--glass);
      border-radius:12px;
      padding:16px;
      box-shadow: 0 4px 12px rgba(2,6,23,0.35);
    }
    .small-muted { color: var(--muted); font-size:13px; }
    .pill {
      display:inline-block;
      padding:6px 10px;
      border-radius:999px;
      background:rgba(108,99,255,0.16);
      color: #6C63FF;
      font-weight:600;
      font-size:13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-header">
      <div style="display:flex;flex-direction:column;">
         <h1 class="title">ResearchFlow — Agentic Research & Content</h1>
         <div class="subtitle">Run multi-agent research pipelines and get blog + social copy + SEO-ready outputs.</div>
      </div>
      <div style="flex:1"></div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;">
         <span class="pill">Agentic • RAG • SEO</span>
         <div style="height:6px"></div>
         <span class="small-muted">Fast demo • Portfolio-ready</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Run ResearchFlow")
    topic = st.text_input("Topic / Keywords", value="Gen AI vs Humans")
    tone = st.selectbox("Tone", ["professional", "casual", "friendly"], index=0)
    length = st.selectbox("Length", ["short", "medium", "long"], index=1)
    run = st.button("Run", key="run_button")
    st.markdown("---")
    st.write("Options")
    show_console_by_default = st.checkbox("Auto-open console output", value=False)
    show_quick_view = st.checkbox("Show Quick View", value=True)
    st.markdown("---")
    st.caption("Made with crew.ai ")

ANSI_ESCAPE_RE = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

def _maybe_awaitable(val):
    """If val is an awaitable/coroutine, run it and return result; otherwise return val."""
    if asyncio.iscoroutine(val):
        return asyncio.run(val)
    if isinstance(val, types.CoroutineType):
        return asyncio.run(val)
    return val

def strip_ansi(s: str) -> str:
    if not isinstance(s, str):
        return s
    return ANSI_ESCAPE_RE.sub("", s)

def safe_parse_result(result: Any) -> Union[dict, list, str]:
    """
    Try a series of safe conversions so st.json() can accept the value.
    Returns either a JSON-serializable object (dict/list) or a cleaned string (for display).
    """
    if isinstance(result, (bytes, bytearray)):
        try:
            result = result.decode()
        except Exception:
            result = str(result)

    if isinstance(result, str):
        cleaned = strip_ansi(result).strip()
        if cleaned.startswith("{") or cleaned.startswith("["):
            try:
                return json.loads(cleaned)
            except Exception:
                try:
                    return json.loads(cleaned.replace("'", '"'))
                except Exception:
                    return cleaned
        else:
            return cleaned

    if isinstance(result, (dict, list)):
        try:
            dumped = json.dumps(result, default=str)
            return json.loads(dumped)
        except Exception:
            return json.loads(json.dumps(result, default=str))

    try:
        json.dumps(result)  
        return result
    except Exception:
        return str(result)

left_col, right_col = st.columns([1.2, 1])

if run and topic.strip():
    buf = io.StringIO()
    with st.spinner("Running ResearchFlow agents... (this may take a few seconds)"):
        try:
            with redirect_stdout(buf):
                maybe = research_crew.kickoff(inputs={"topic": topic, "tone": tone, "length": length})
                result = _maybe_awaitable(maybe)
        except Exception as e:
            buf.write(f"\n\nException during crew run: {repr(e)}\n")
            result = {"error": str(e)}

    st.success("Run completed")

    console_output = buf.getvalue()
    with st.expander("Agent Console Output", expanded=show_console_by_default):
        if console_output:
            st.code(strip_ansi(console_output), language=None)
        else:
            st.info("No console output was produced by the crew run.")

    parsed = safe_parse_result(result)

    raw_json_str = None
    try:
        if isinstance(parsed, (dict, list)):
            raw_json_str = json.dumps(parsed, indent=2, ensure_ascii=False)
        else:
            raw_json_str = str(parsed)
    except Exception:
        raw_json_str = str(parsed)

    with st.container():
        c1, c2, c3 = st.columns([1,1,1])
        with c1:
            st.download_button("📥 Download result (JSON)", data=raw_json_str, file_name="researchflow_result.json", mime="application/json")
        with c2:
            st.button("🔎 Copy result to clipboard", key="copy_button")  
        with c3:
            st.button("⭐ Save snapshot", key="save_snapshot")

    with left_col:
        st.markdown("### Results (raw)")
        if isinstance(parsed, (dict, list)):
            st.json(parsed)
        else:
            st.text(parsed)

        if isinstance(parsed, dict) and "content_writing_task" in parsed:
            cw = parsed["content_writing_task"]
            if isinstance(cw, dict):
                st.markdown("### Content Outputs")

                if "blog" in cw and cw["blog"]:
                    st.markdown("#### Blog (Preview)")
                    st.markdown(cw["blog"])
                    st.divider()
                
                social_cols = st.columns(3)
                if "linkedin" in cw:
                    with social_cols[0]:
                        st.caption("LinkedIn")
                        st.code(cw["linkedin"])
                if "x_thread" in cw:
                    with social_cols[1]:
                        st.caption("X / Thread")
                        st.code(cw["x_thread"])
                if "newsletter" in cw:
                    with social_cols[2]:
                        st.caption("Newsletter")
                        st.code(cw["newsletter"])

    with right_col:
        st.markdown("### Quick View")
        if isinstance(parsed, dict) and show_quick_view:
            
            if "research_task" in parsed:
                with st.expander("Research — extracted sources", expanded=True):
                    st.write(parsed["research_task"])
            if "rag_answering_task" in parsed:
                with st.expander("RAG — build info / chunks", expanded=False):
                    st.write(parsed["rag_answering_task"])

            if "seo_optimization_task" in parsed:
                st.markdown("### SEO")
                seo = parsed["seo_optimization_task"]
                st.write(seo)

            if isinstance(parsed.get("content_writing_task"), dict):
                top10 = parsed["content_writing_task"].get("top10") or parsed["content_writing_task"].get("top_10") or parsed["content_writing_task"].get("top10_insights")
                if top10:
                    with st.expander("Top 10 Insights", expanded=True):
                        for i, t in enumerate(top10, 1):
                            st.markdown(f"**{i}.** {t}")

        else:
            st.info("Quick View not available for non-dict results.")

    st.markdown("---")
    st.markdown("#### Raw output")
    with st.expander("Show raw output (string)", expanded=False):
        st.text(raw_json_str)

else:

    st.markdown(
        """
        <div class="card">
          <h3 style="margin:0 0 6px 0;">How to use</h3>
          <p class="small-muted" style="margin:0;">
            Enter a topic in the sidebar, pick tone and length, then click <strong>Run</strong>.
            ResearchFlow will run the multi-agent pipeline and return structured research + content outputs.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
