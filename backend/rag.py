def run_rag(question, sop_content):
    # In real implementation: chunk SOPs, embed, search vector DB, then call LLM
    sources = sop_content[:200]  # first 200 chars as source
    answer = f"Based on SOP: {sources}..."
    return answer, sources
