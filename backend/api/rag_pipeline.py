# =========================
# Imports y configuración
# =========================

import os
import json
import numpy as np
import mysql.connector
from openai import OpenAI
from dotenv import load_dotenv

# Carga variables de entorno desde .env
load_dotenv()

# =========================
# Variables de entorno
# =========================

OPENAI_API_KEY = os.getenv("PERSONAL_API_KEY")

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}

# Cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# Utilidades de base de datos
# =========================

def get_db_connection():
    """
    Crea y devuelve una nueva conexión a MySQL.
    Se usa conexión por función para evitar estados compartidos.
    """
    return mysql.connector.connect(**MYSQL_CONFIG)


def save_question_and_answer(question: str, answer: str) -> int:
    """
    Guarda la pregunta y la respuesta generada en la tabla `questions`.

    Args:
        question (str): Pregunta del usuario
        answer (str): Respuesta generada por el modelo

    Returns:
        int: ID de la pregunta insertada (question_id)
    """
    db = get_db_connection()
    cursor = db.cursor()

    sql = """
        INSERT INTO questions (quiestion, answer)
        VALUES (%s, %s)
    """
    cursor.execute(sql, (question, answer))
    db.commit()

    question_id = cursor.lastrowid

    cursor.close()
    db.close()

    return question_id


def save_question_embeddings(question_id: int, docs: list):
    """
    Guarda la relación entre una pregunta y los embeddings utilizados
    para generar su respuesta.

    Args:
        question_id (int): ID de la pregunta
        docs (list): Lista de documentos (embeddings) usados en el contexto
    """
    db = get_db_connection()
    cursor = db.cursor()

    sql = """
        INSERT INTO question_embeddings (embedding_id, question_id)
        VALUES (%s, %s)
    """

    values = []
    for doc in docs:
        values.append((doc["id"], question_id))

    cursor.executemany(sql, values)
    db.commit()

    cursor.close()
    db.close()

# =========================
# Embeddings y similitud
# =========================

def embed_question(question: str) -> np.ndarray:
    """
    Genera el embedding vectorial de una pregunta usando OpenAI.

    Args:
        question (str): Texto de la pregunta

    Returns:
        np.ndarray: Vector embedding de la pregunta
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )
    return np.array(response.data[0].embedding)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calcula la similitud coseno entre dos vectores.

    Args:
        a (np.ndarray): Vector A
        b (np.ndarray): Vector B

    Returns:
        float: Similitud coseno
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def load_embeddings_from_db():
    """
    Carga todos los embeddings almacenados en la tabla `embeddings`.

    Returns:
        list: Lista de diccionarios con id, texto, embedding y fuente
    """
    db = get_db_connection()
    cursor = db.cursor()

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
    """
    Recupera los K documentos más similares a la pregunta.

    Args:
        question_embedding (np.ndarray): Embedding de la pregunta
        documents (list): Lista de documentos con embeddings
        k (int): Número de documentos a recuperar

    Returns:
        list: Top-K documentos más relevantes
    """
    scored = []

    for doc in documents:
        score = cosine_similarity(question_embedding, doc["embedding"])
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:k]]

# =========================
# Construcción del prompt
# =========================

def build_context(docs):
    """
    Construye el contexto textual a partir de los documentos recuperados.

    Args:
        docs (list): Documentos relevantes

    Returns:
        str: Contexto formateado para el prompt
    """
    context = ""
    for i, doc in enumerate(docs, 1):
        context += f"[Documento {i} | Fuente: {doc['source']}]\n"
        context += doc["text"] + "\n\n"
    return context


def answer_question(question, context):
    """
    Genera la respuesta usando el modelo de chat,
    restringiendo la respuesta únicamente al contexto.

    Args:
        question (str): Pregunta del usuario
        context (str): Contexto recuperado

    Returns:
        str: Respuesta generada
    """
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

# =========================
# Pipeline RAG (exportable)
# =========================

def rag_pipeline(question: str) -> str:
    """
    Pipeline completo RAG:
    1. Embedding de la pregunta
    2. Recuperación de documentos relevantes
    3. Construcción del contexto
    4. Generación de respuesta
    5. Persistencia en base de datos

    Args:
        question (str): Pregunta del usuario

    Returns:
        str: Respuesta final
    """

    # 1. Embedding de la pregunta
    question_embedding = embed_question(question)

    # 2. Cargar documentos
    documents = load_embeddings_from_db()

    # 3. Recuperar top-k
    top_docs = retrieve_top_k(question_embedding, documents, k=5)

    # 4. Construir contexto
    context = build_context(top_docs)

    # 5. Generar respuesta
    answer = answer_question(question, context)

    # 6. Guardar pregunta y respuesta
    question_id = save_question_and_answer(question, answer)

    # 7. Guardar relación pregunta ↔ embeddings
    save_question_embeddings(question_id, top_docs)

    return answer

# Export explícito (útil para endpoints)
__all__ = ["rag_pipeline"]

# =========================
# Ejecución directa (opcional)
# =========================

# if __name__ == "__main__":
#     question = "¿Cuanto cuesta una rtx 4090?"
#     respuesta = rag_pipeline(question)
#     print(respuesta)
