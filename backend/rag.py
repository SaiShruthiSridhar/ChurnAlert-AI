import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import os

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

_client = None
_collection = None

def _warmup_onnx_model():
    """
    Force the ONNX model to download at startup, not on first user request.
    This prevents the 79MB download from blocking the /similar endpoint.
    On Render free tier, the download path is hardcoded to ~/.cache/chroma
    and cannot be changed via env var — so we trigger it early instead.
    """
    try:
        from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2
        ef = ONNXMiniLM_L6_V2()
        ef._download_model_if_not_exists()
        print("[RAG] ONNX model warm-up complete.")
    except Exception as e:
        print(f"[RAG] ONNX warm-up failed (non-fatal): {e}")

# Warm up at import time so Render downloads the model during startup
_warmup_onnx_model()

def get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    try:
        ef = DefaultEmbeddingFunction()
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_collection(
            name="churn_cases",
            embedding_function=ef
        )
        print(f"[RAG] ChromaDB collection loaded. Total cases: {_collection.count()}")
        return _collection
    except Exception as e:
        print(f"[RAG] ChromaDB not available: {e}. Falling back to keyword matcher.")
        return None

FALLBACK_CASES = [
    {
        "id": "fallback_1",
        "text": "Customer churned after 3 months. Month-to-month contract. Low feature adoption. High monthly charges.",
        "action": "Assign onboarding specialist. Offer discounted annual contract.",
        "outcome": "Similar intervention succeeded in 60% of early-tenure cases."
    },
    {
        "id": "fallback_2",
        "text": "Customer churned due to unresolved support tickets and negative sentiment. Fiber optic service.",
        "action": "Escalate to senior support. Schedule dedicated review call.",
        "outcome": "Resolution-focused outreach reduced churn by 40% in similar cases."
    },
    {
        "id": "fallback_3",
        "text": "Customer churned after renewal date passed. Two year contract expired. No re-engagement.",
        "action": "Send renewal offer 60 days before expiry. Offer loyalty discount.",
        "outcome": "Early renewal outreach retained 70% of expiring contracts."
    }
]

def retrieve_similar_cases(risk_reasons: list, n_results: int = 3) -> list:
    if not risk_reasons:
        return FALLBACK_CASES[:2]

    priority_keywords = [
        'month-to-month', 'adoption', 'inactiv', 'login', 'tenure',
        'ticket', 'negative', 'renewal', 'session', 'churn'
    ]
    scored = []
    for reason in risk_reasons:
        score = sum(1 for kw in priority_keywords if kw.lower() in reason.lower())
        scored.append((score, reason))
    scored.sort(reverse=True)
    top_reasons = [r for _, r in scored[:3]] if scored else risk_reasons[:3]
    query_text = " ".join(top_reasons)
    print(f"[RAG] Query text: {query_text[:100]}")

    collection = get_collection()

    if collection is not None:
        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=min(n_results, collection.count())
            )
            cases = []
            if results and results.get("documents") and results["documents"][0]:
                docs = results["documents"][0]
                metas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]
                for i, doc in enumerate(docs):
                    meta = metas[i] if i < len(metas) else {}
                    distance = distances[i] if i < len(distances) else 1.0
                    similarity = round(max(0.0, min(1.0, 1.0 / (1.0 + distance))), 3)
                    cases.append({
                        "id": f"chroma_{i}",
                        "text": doc,
                        "contract": meta.get("contract", "Unknown"),
                        "tenure": meta.get("tenure", "Unknown"),
                        "monthly_charges": meta.get("monthly_charges", "Unknown"),
                        "churn_reason": meta.get("churn_reason", "Not specified"),
                        "similarity_score": similarity,
                        "source": "IBM Telco Churn Dataset"
                    })
            print(f"[RAG] Retrieved {len(cases)} similar cases from ChromaDB.")
            return cases if cases else FALLBACK_CASES[:2]
        except Exception as e:
            print(f"[RAG] ChromaDB query failed: {e}. Using fallback.")
            return FALLBACK_CASES[:2]
    else:
        query_lower = query_text.lower()
        matched = []
        for case in FALLBACK_CASES:
            keywords = ["usage", "adoption", "inactivity", "ticket", "negative",
                       "sentiment", "friction", "month", "contract", "renewal",
                       "tenure", "early"]
            if any(k in query_lower for k in keywords):
                matched.append(case)
        return matched[:2] if matched else FALLBACK_CASES[:2]

def add_outcome_to_rag(account_id: str, risk_reasons: list, outcome: str, csm_action: str):
    collection = get_collection()
    if collection is None:
        print("[RAG] Cannot add outcome — ChromaDB not available.")
        return False
    try:
        text = (
            f"Account {account_id} intervention outcome: {outcome}. "
            f"Risk signals: {' '.join(risk_reasons)}. "
            f"CSM action taken: {csm_action}."
        )
        collection.add(
            documents=[text],
            metadatas=[{
                "account_id": account_id,
                "outcome": outcome,
                "churn_value": "0" if outcome == "renewed" else "1",
                "source": "intervention_outcome"
            }],
            ids=[f"outcome_{account_id}_{len(risk_reasons)}"]
        )
        print(f"[RAG] Outcome for {account_id} added to ChromaDB.")
        return True
    except Exception as e:
        print(f"[RAG] Failed to add outcome: {e}")
        return False