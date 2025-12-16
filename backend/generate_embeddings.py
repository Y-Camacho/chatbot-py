import os
import re
import json
from pypdf import PdfReader
import mysql.connector
from openai import OpenAI
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()


# ======================
# CONFIGURACIÓN
# ======================

PDF_FOLDER = "./docs"

# Accede a las variables de entorno
OPENAI_API_KEY = os.getenv("PERSONAL_API_KEY")

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE" )
}

EMBEDDING_MODEL = "text-embedding-3-small"

MIN_CHUNK_SIZE = 300
MAX_CHUNK_SIZE = 800

# ======================
# CLIENTES
# ======================

client = OpenAI(api_key=OPENAI_API_KEY)
db = mysql.connector.connect(**MYSQL_CONFIG)
cursor = db.cursor()

# ======================
# FUNCIONES
# ======================

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text = []
    for page in reader.pages:
        if page.extract_text():
            text.append(page.extract_text())
    return " ".join(text)


def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text, min_size=300, max_size=800):
    words = text.split(" ")
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_size:
            current_chunk += (" " if current_chunk else "") + word
        else:
            if len(current_chunk) >= min_size:
                chunks.append(current_chunk)
                current_chunk = word
            else:
                current_chunk += " " + word

    if len(current_chunk) >= min_size:
        chunks.append(current_chunk)

    return chunks


def get_embedding(text):
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def save_to_db(pdf_name, chunk, embedding):
    sql = """
        INSERT INTO embeddings (source, text, embedding)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (pdf_name, chunk, json.dumps(embedding)))
    db.commit()

# ======================
# PIPELINE PRINCIPAL
# ======================

def process_pdfs():
    for filename in os.listdir(PDF_FOLDER):
        if not filename.lower().endswith(".pdf"):
            continue

        print(f"📄 Procesando: {filename}")
        pdf_path = os.path.join(PDF_FOLDER, filename)

        raw_text = extract_text_from_pdf(pdf_path)
        cleaned_text = clean_text(raw_text)

        chunks = chunk_text(cleaned_text)

        print(f"   → {len(chunks)} chunks")

        for chunk in chunks:
            embedding = get_embedding(chunk)
            save_to_db(filename, chunk, embedding)

    cursor.close()
    db.close()


if __name__ == "__main__":
    process_pdfs()
