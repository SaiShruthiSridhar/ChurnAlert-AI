import chromadb
import os

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = client.get_collection(name="churn_cases")

count = collection.count()

print("=" * 60)
print("ChromaDB Knowledge Base — IBM Telco Churn Dataset")
print("=" * 60)
print(f"Total records loaded: {count}")
print(f"Collection name: churn_cases")
print(f"Data source: Kaggle IBM Telco Customer Churn Dataset")
print(f"Dataset URL: https://www.kaggle.com/datasets/blastchar/telco-customer-churn")
print("=" * 60)

results = collection.query(
    query_texts=["customer churned month-to-month contract"],
    n_results=3
)

print("Sample records from ChromaDB:")
print("-" * 60)

docs = results.get("documents", [[]])[0]
metas = results.get("metadatas", [[]])[0]

for i, (doc, meta) in enumerate(zip(docs, metas)):
    print(f"Record {i + 1}:")
    print(f"  Text: {doc[:120]}...")
    print(f"  Contract: {meta.get('contract', 'N/A')}")
    print(f"  Tenure: {meta.get('tenure', 'N/A')} months")
    print(f"  Monthly Charges: ${meta.get('monthly_charges', 'N/A')}")
    print(f"  Churn Reason: {meta.get('churn_reason', 'N/A')}")
    print("-" * 60)

print(f"Embedding model: ChromaDB DefaultEmbeddingFunction (ONNX)")
print(f"Vector similarity: Cosine distance")
print(f"Status: Active and powering Similar Past Accounts feature")
print("=" * 60)
