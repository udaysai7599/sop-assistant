import re
from difflib import SequenceMatcher


def _tokenize(text):
    return [token for token in re.findall(r"[a-z0-9']+", (text or '').lower()) if token]


def _split_sentences(text):
    chunks = [segment.strip() for segment in re.split(r'(?<=[.!?])\s+', text or '') if segment.strip()]
    if chunks:
        return chunks
    stripped = (text or '').strip()
    return [stripped] if stripped else []


def _score_chunk(chunk, question_tokens, question_text):
    chunk_tokens = _tokenize(chunk)
    if not chunk_tokens or not question_tokens:
        return 0.0

    overlap = sum(min(chunk_tokens.count(term), question_tokens.count(term)) for term in set(question_tokens))
    lexical_recall = overlap / max(len(question_tokens), 1)
    lexical_precision = overlap / max(len(chunk_tokens), 1)
    fuzzy_similarity = SequenceMatcher(None, question_text, ' '.join(chunk_tokens)).ratio()

    score = (2.2 * lexical_recall) + (1.1 * lexical_precision) + (1.0 * fuzzy_similarity)
    if question_text and question_text in chunk.lower():
        score += 0.6
    return score


def run_rag(question, sop_entries, top_k=3):
    """
    Run lightweight retrieval + answer synthesis.

    Parameters:
        question (str): user question
        sop_entries (list[dict] | str): either raw SOP content string or list of
            {'sop_id': int, 'sop_title': str, 'content': str}
        top_k (int): number of evidence chunks to return

    Returns:
        dict: {
            'answer': str,
            'sources': list[dict],
            'confidence': 'high' | 'low'
        }
    """
    if isinstance(sop_entries, str):
        sop_entries = [{"sop_id": None, "sop_title": "SOP", "content": sop_entries}]

    question_text = re.sub(r'\s+', ' ', (question or '').strip().lower())
    question_tokens = _tokenize(question_text)

    retrieval_rows = []
    for entry in sop_entries or []:
        sop_id = entry.get('sop_id')
        sop_title = entry.get('sop_title') or 'SOP'
        content = entry.get('content') or ''
        source_type = entry.get('source_type') or 'sop_text'
        document_id = entry.get('document_id')
        document_title = entry.get('document_title')
        download_url = entry.get('download_url')
        for chunk in _split_sentences(content):
            score = _score_chunk(chunk, question_tokens, question_text)
            retrieval_rows.append({
                'sop_id': sop_id,
                'sop_title': sop_title,
                'excerpt': chunk[:500],
                'score': round(score, 4),
                'source_type': source_type,
                'document_id': document_id,
                'document_title': document_title,
                'download_url': download_url
            })

    if not retrieval_rows:
        return {
            'answer': 'I could not find any SOP guidance for that question.',
            'sources': [],
            'confidence': 'low'
        }

    ranked = sorted(retrieval_rows, key=lambda row: row['score'], reverse=True)
    top_sources = [row for row in ranked[:max(top_k, 1)] if row['score'] > 0]

    if not top_sources:
        fallback = ranked[0]
        return {
            'answer': (
                'I could not find a precise SOP match for your question. '
                f"Closest available guidance from '{fallback['sop_title']}': {fallback['excerpt']}"
            ),
            'sources': [fallback],
            'confidence': 'low'
        }

    primary = top_sources[0]
    secondary = top_sources[1:]
    if secondary:
        supporting_titles = ', '.join(sorted({item['sop_title'] for item in secondary}))
        answer = (
            f"According to '{primary['sop_title']}', {primary['excerpt']} "
            f"Supporting context also appears in: {supporting_titles}."
        )
    else:
        answer = f"According to '{primary['sop_title']}', {primary['excerpt']}"

    confidence = 'high' if primary['score'] >= 1.2 else 'low'
    if confidence == 'low':
        answer = (
            'I found limited confidence context in your SOPs. '
            'Please verify with a manager if this is business-critical. ' + answer
        )

    return {
        'answer': answer,
        'sources': top_sources,
        'confidence': confidence
    }
