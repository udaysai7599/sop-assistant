import re


def run_rag(question, sop_content):
    if not sop_content:
        return "I could not find any SOP guidance for that question.", ""

    normalized_question = re.split(r'[^a-z0-9]+', (question or '').lower())
    normalized_question = [term for term in normalized_question if term]

    sentences = [segment.strip() for segment in re.split(r'(?<=[.!?])\s+', sop_content) if segment.strip()]
    if not sentences:
        sentences = [sop_content.strip()]

    best_sentence = sentences[0]
    best_score = 0

    for sentence in sentences:
        lowered = sentence.lower()
        score = sum(1 for term in normalized_question if term and term in lowered)
        if score > best_score:
            best_score = score
            best_sentence = sentence

    if best_score == 0:
        best_sentence = sentences[0]

    source_excerpt = best_sentence[:500]
    answer = (
        f"According to the SOP, {source_excerpt}"
        if source_excerpt.endswith((".", "!", "?"))
        else f"According to the SOP, {source_excerpt}."
    )
    return answer, source_excerpt
