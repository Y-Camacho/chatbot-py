from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import os
from fastapi.middleware.cors import CORSMiddleware

from rag_pipeline import rag_pipeline

# =========================
# Configuración
# =========================

app = FastAPI(
    title="RAG Chat API",
    description="API para realizar preguntas usando RAG y consultar el histórico",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}

# =========================
# Modelos Pydantic
# =========================

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    question: str
    answer: str
    context: str


class QuestionHistory(BaseModel):
    id: int
    question: str
    answer: str

# =========================
# Utilidad DB
# =========================

def get_db_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

# =========================
# Endpoints
# =========================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Endpoint para hacer preguntas al sistema RAG.
    """
    try:
        response = rag_pipeline(request.question)
        return {"question": response["question"], "context": response["context"], "answer": response["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/questions", response_model=list[QuestionHistory])
def get_questions():
    """
    Devuelve el histórico de preguntas y respuestas.
    """
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, quiestion AS question, answer
            FROM questions
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()

        cursor.close()
        db.close()

        return rows

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/questions/{question_id}")
def delete_question(question_id: int):
    """
    Elimina una pregunta y sus relaciones con embeddings.
    """
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # 1. Eliminar relaciones (clave foránea)
        cursor.execute(
            "DELETE FROM question_embeddings WHERE question_id = %s",
            (question_id,)
        )

        # 2. Eliminar la pregunta
        cursor.execute(
            "DELETE FROM questions WHERE id = %s",
            (question_id,)
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pregunta no encontrada")

        db.commit()
        cursor.close()
        db.close()

        return {"message": f"Pregunta {question_id} eliminada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/questions")
def delete_all_questions():
    """
    Elimina TODAS las preguntas (uso administrativo).
    """
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM question_embeddings")
    cursor.execute("DELETE FROM questions")

    db.commit()
    cursor.close()
    db.close()

    return {"message": "Todas las preguntas eliminadas"}
