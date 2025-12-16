import os
import json
from openai import OpenAI
import mysql.connector
import numpy as np
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("PERSONAL_API_KEY")

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE" )
}

client = OpenAI(api_key=OPENAI_API_KEY)
db = mysql.connector.connect(**MYSQL_CONFIG)
cursor = db.cursor()

def embed_question(question: str) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )
    return np.array(response.data[0].embedding)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_embeddings_from_db():
    """
    Debe devolver una lista de dicts:
    [
      {
        "id": 1,
        "text": "...",
        "embedding": np.array([...]),
        "source": "..."
      },
      ...
    ]
    """

    sql_query = "SELECT id, text, embedding, source FROM embeddings"
    cursor.execute(sql_query)

    rows = cursor.fetchall()

    cursor.close()
    db.close()

    data = []
    for r in rows:
        data.append({
            "id": r[0],
            "text": r[1],
            "embedding": np.array(json.loads(r[2]), dtype=np.float32),
            "source": r[3]
        })
    return data

def retrieve_top_k(question_embedding, documents, k=5):
    scored = []

    for doc in documents:
        score = cosine_similarity(question_embedding, doc["embedding"])
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:k]]

def build_context(docs):
    context = ""
    for i, doc in enumerate(docs, 1):
        context += f"[Documento {i} | Fuente: {doc['source']}]\n"
        context += doc["text"] + "\n\n"
    return context

def answer_question(question, context):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Responde usando únicamente la información del contexto."
            },
            {
                "role": "user",
                "content": f"""
Contexto:
{context}

Pregunta:
{question}
"""
            }
        ],
        temperature=0.2
    )
    return response.choices[0].message.content

def rag_pipeline(question):
    question_embedding = embed_question(question)
    documents = load_embeddings_from_db()
    top_docs = retrieve_top_k(question_embedding, documents, k=5)
    context = build_context(top_docs)
    answer = answer_question(question, context)
    return answer

question = "¿Cuando se fundo nvidia?"
respuesta = rag_pipeline(question)
print(respuesta)
