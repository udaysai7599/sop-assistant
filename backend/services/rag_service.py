import re
from difflib import SequenceMatcher


def _tokenize(text):
    """Split text into lowercase alphanumeric tokens for lightweight matching."""
    return [token for token in re.findall(r"[a-z0-9']+", (text or "").lower()) if token]


def _sentence_score(sentence, question_tokens, question_text):
    """Score a sentence by overlap, phrase matches, and similarity heuristics."""
    sentence_text = " ".join(_tokenize(sentence))
    sentence_tokens = _tokenize(sentence)
    if not sentence_tokens or not question_tokens:
        return 0.0

    score = 0.0
    if question_text and question_text in sentence_text:
        score += 3.0

    overlap = sum(min(sentence_tokens.count(term), question_tokens.count(term)) for term in set(question_tokens))
    score += overlap

    if question_tokens:
        score += overlap / len(question_tokens)
    if sentence_tokens:
        score += overlap / len(sentence_tokens)

    score += SequenceMatcher(None, question_text, sentence_text).ratio()
    return score


def run_rag(question, sop_content):
    """Return a concise answer and evidence excerpt for a given SOP question."""
    if not sop_content:
        return "I could not find any SOP guidance for that question.", ""

    question_text = re.sub(r"\s+", " ", (question or "").strip().lower())
    question_tokens = _tokenize(question_text)

    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", sop_content) if segment.strip()]
    if not sentences:
        sentences = [sop_content.strip()]

    best_sentence = sentences[0]
    best_score = -1.0

    for sentence in sentences:
        score = _sentence_score(sentence, question_tokens, question_text)
        if score > best_score:
            best_score = score
            best_sentence = sentence

    if best_score <= 0:
        source_excerpt = sop_content.strip()[:500]
        answer = (
            f"I could not find a specific SOP answer for that question. Here is the relevant guidance: {source_excerpt}"
            if source_excerpt.endswith((".", "!", "?"))
            else f"I could not find a specific SOP answer for that question. Here is the relevant guidance: {source_excerpt}."
        )
        return answer, source_excerpt

    source_excerpt = best_sentence[:500]
    answer = (
        f"According to the SOP, {source_excerpt}"
        if source_excerpt.endswith((".", "!", "?"))
        else f"According to the SOP, {source_excerpt}."
    )
    return answer, source_excerpt
