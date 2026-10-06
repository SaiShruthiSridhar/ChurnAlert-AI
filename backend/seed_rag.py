import pandas as pd
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import os

XLSX_PATH = os.path.join(os.path.dirname(__file__), "Telco_customer_churn.xlsx")
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

def seed_chroma():
    print("[RAG Seeder] Loading Telco_customer_churn.xlsx...")
    df = pd.read_excel(XLSX_PATH)
    print(f"[RAG Seeder] Total records loaded: {len(df)}")

    churned = df[df["Churn Value"] == 1].copy()
    print(f"[RAG Seeder] Churned records to embed: {len(churned)}")

    churned = churned.infer_objects(copy=False).fillna("Unknown")

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection("churn_cases")
        print("[RAG Seeder] Existing churn_cases collection deleted.")
    except Exception:
        pass

    # Use ChromaDB's built-in ONNX embedding function — no sentence-transformers needed
    ef = DefaultEmbeddingFunction()

    collection = client.get_or_create_collection(
        name="churn_cases",
        embedding_function=ef
    )

    documents = []
    metadatas = []
    ids = []

    for idx, row in churned.iterrows():
        tenure = row.get("Tenure Months", "Unknown")
        contract = row.get("Contract", "Unknown")
        monthly = row.get("Monthly Charges", "Unknown")
        total = row.get("Total Charges", "Unknown")
        internet = row.get("Internet Service", "Unknown")
        payment = row.get("Payment Method", "Unknown")
        senior = row.get("Senior Citizen", "Unknown")
        partner = row.get("Partner", "Unknown")
        dependents = row.get("Dependents", "Unknown")
        churn_reason = row.get("Churn Reason", "Not specified")

        text = (
            f"Customer churned after {tenure} months. "
            f"Contract type: {contract}. "
            f"Monthly charges: ${monthly}. "
            f"Total charges: ${total}. "
            f"Internet service: {internet}. "
            f"Payment method: {payment}. "
            f"Senior citizen: {senior}. "
            f"Has partner: {partner}. "
            f"Has dependents: {dependents}. "
            f"Churn reason: {churn_reason}."
        )

        documents.append(text)
        metadatas.append({
            "tenure": str(tenure),
            "contract": str(contract),
            "monthly_charges": str(monthly),
            "internet_service": str(internet),
            "payment_method": str(payment),
            "churn_reason": str(churn_reason),
            "churn_value": "1"
        })
        ids.append(f"churn_{idx}")

    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        collection.add(
            documents=batch_docs,
            metadatas=batch_meta,
            ids=batch_ids
        )
        print(f"[RAG Seeder] Embedded batch {i//batch_size + 1} ({len(batch_docs)} records)")

    final_count = collection.count()
    print(f"[RAG Seeder] Done. Total records in ChromaDB: {final_count}")

if __name__ == "__main__":
    seed_chroma()
