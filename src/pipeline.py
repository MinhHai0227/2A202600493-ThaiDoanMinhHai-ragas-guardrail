"""Production RAG pipeline: chunking + search + rerank + generation + eval."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OPENAI_API_KEY, OPENAI_CHAT_MODEL, RERANK_TOP_K
from src.m1_chunking import chunk_hierarchical, load_documents
from src.m2_search import HybridSearch
from src.m3_rerank import CrossEncoderReranker
from src.m4_eval import evaluate_ragas, failure_analysis, load_test_set, save_report
from src.m5_enrichment import enrich_chunks

_openai_client = None


def _get_openai_client():
    """Lazy-load OpenAI client so retrieval can still run without API access."""
    global _openai_client
    if _openai_client is None and OPENAI_API_KEY:
        from openai import OpenAI

        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def generate_answer(query: str, contexts: list[str]) -> str:
    """Generate an answer grounded only in the retrieved contexts."""
    if not contexts:
        return "Khong tim thay thong tin."

    client = _get_openai_client()
    if client is None:
        return contexts[0]

    context_str = "\n\n".join(
        f"[Context {idx + 1}]\n{context}" for idx, context in enumerate(contexts)
    )

    try:
        response = client.chat.completions.create(
            model=OPENAI_CHAT_MODEL,
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ban la tro ly RAG. Hay tra loi CHI dua tren context duoc cung cap. "
                        "Neu context khong du de tra loi, hay noi ro 'Khong tim thay thong tin trong tai lieu duoc cung cap.'. "
                        "Khong tu bo sung kien thuc ben ngoai."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context_str}\n\nCau hoi: {query}",
                },
            ],
        )
        answer = response.choices[0].message.content
        return answer.strip() if answer else contexts[0]
    except Exception as exc:
        print(f"  [warn] OpenAI generation failed, using top context fallback: {exc}")
        return contexts[0]


def build_pipeline():
    """Build production RAG pipeline."""
    print("=" * 60)
    print("PRODUCTION RAG PIPELINE")
    print("=" * 60)

    print("\n[1/4] Chunking documents...")
    docs = load_documents()
    all_chunks = []
    for doc in docs:
        _, children = chunk_hierarchical(doc["text"], metadata=doc["metadata"])
        for child in children:
            all_chunks.append(
                {
                    "text": child.text,
                    "metadata": {**child.metadata, "parent_id": child.parent_id},
                }
            )
    print(f"  {len(all_chunks)} chunks from {len(docs)} documents")

    print("\n[2/4] Enriching chunks (M5)...")
    print("  [skip] Enrichment disabled for faster indexing")

    print("\n[3/4] Indexing (BM25 + Dense)...")
    search = HybridSearch()
    search.index(all_chunks)

    print("\n[4/4] Loading reranker...")
    reranker = CrossEncoderReranker()

    return search, reranker


def run_query(
    query: str, search: HybridSearch, reranker: CrossEncoderReranker
) -> tuple[str, list[str]]:
    """Run a single query through retrieval, reranking, and generation."""
    results = search.search(query)
    docs = [{"text": item.text, "score": item.score, "metadata": item.metadata} for item in results]
    reranked = reranker.rerank(query, docs, top_k=RERANK_TOP_K)
    contexts = [item.text for item in reranked] if reranked else [item.text for item in results[:3]]
    answer = generate_answer(query, contexts)
    return answer, contexts


def evaluate_pipeline(search: HybridSearch, reranker: CrossEncoderReranker):
    """Run evaluation on the test set."""
    print("\n[Eval] Running queries...")
    test_set = load_test_set()
    questions, answers, all_contexts, ground_truths = [], [], [], []

    for idx, item in enumerate(test_set):
        answer, contexts = run_query(item["question"], search, reranker)
        questions.append(item["question"])
        answers.append(answer)
        all_contexts.append(contexts)
        ground_truths.append(item["ground_truth"])
        print(f"  [{idx + 1}/{len(test_set)}] {item['question'][:50]}...")

    print("\n[Eval] Running RAGAS...")
    results = evaluate_ragas(questions, answers, all_contexts, ground_truths)

    print("\n" + "=" * 60)
    print("PRODUCTION RAG SCORES")
    print("=" * 60)
    for metric in [
        "faithfulness",
        "answer_relevancy",
        "context_precision",
        "context_recall",
    ]:
        score = results.get(metric, 0)
        status = "OK" if score >= 0.75 else "LOW"
        print(f"  {status:<3} {metric}: {score:.4f}")

    failures = failure_analysis(results.get("per_question", []))
    save_report(results, failures)
    return results


if __name__ == "__main__":
    start = time.time()
    search_engine, reranker_model = build_pipeline()
    evaluate_pipeline(search_engine, reranker_model)
    print(f"\nTotal: {time.time() - start:.1f}s")
