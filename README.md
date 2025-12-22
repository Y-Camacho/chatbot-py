# CHATBOT - PY


## 1. Objetivo del proyecto
El objetivo de este proyecto es desarrollar un chatbot inteligente capaz de responder preguntas de los usuarios únicamente a partir de un contexto documental previamente indexado, utilizando técnicas de embeddings semánticos y Recuperación Aumentada por Generación (RAG).
El sistema permite:

- Consultar documentación interna de una empresa.

- Evitar respuestas inventadas (hallucinations).

- Basar todas las respuestas en información real y trazable.


## 2.  Descripción general del sistema
El chatbot se basa en un flujo RAG (Retrieval-Augmented Generation) que combina:

- Indexación de documentos (PDFs, textos, FAQs).

- Generación de embeddings para representar semánticamente el contenido.

- Búsqueda por similitud ante una pregunta del usuario.

- Generación de una respuesta usando únicamente el contexto recuperado.

**El sistema está dividido en backend, base de datos y frontend web.**

## 3. Guía de instalación
### Requisitos

- Lenguaje: Python.

- Base de datos mysql (o cualquier otra).

- NodeJs.

### Pasos generales

- Clonar el repositorio  
```bash
git clone https://github.com/Y-Camacho/chatbot-py.git
```

- Instalar dependencias  
```bash
# Python - Desde la carpeta ‘backend’
# Primero hay que crear un entorno virtual, y luego ejecutar el siguiende conmando dentro:
python -m venv nombre_del_entorno

.\nombre_del_entorno\Scripts\Activate

pip install -r requirements.txt

# Vue / Node - Desde la carpeta ‘frontend’
npm install
```

- Base de datos.  
El repositorio cuenta con un esquema sql para crear la base de datos e insertar una carga 
inicial de embeddings. Se pueden eliminar los INSERTS si lo que se desea es ejecutar el escript 
propio de crear y persistir los chunks creados a partir de un contenido determinado.

- Ejecutar script de generación de embeddings  
Para ejecutar este script primero se debe estar dentro del venv de python. Luego solo debe de 
ejecutarlo. Asegúrese que tiene los documentos que quiere indexar dentro del directorio **docs/**

- Configurar variables de entorno (API keys)

- Iniciar el servidor backend
```bash
# .\backend\api\
uvicorn api:app --reload
```


- Acceder al frontend
```bash
# .\frontend\
npm run dev
```