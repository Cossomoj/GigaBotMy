from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import uvicorn
import os
import faiss
import numpy as np

# Настройки
GIGACHAT_API_URL = "https://gigachat-api.sber.ru/v1/embeddings"
GIGACHAT_API_KEY = os.getenv("NzU0ZjA2NzctYjlmOC00M2UxLWExNWQtNmQwNTIxMjg1Yzc3OmZlMTNiZGEzLTc2MzgtNGExZS1hODY5LTA3MGRmNTU2MTgyNg==")  # Укажите API-ключ в переменной среды

# Инициализация FastAPI
app = FastAPI()

# Инициализация FAISS
embedding_dim = 768  # Размерность эмбеддингов (уточните для GigaChat)
index = faiss.IndexFlatL2(embedding_dim)  # L2-нормализация
stored_texts = []  # Храним соответствующие тексты


# Модель запроса
class TextInput(BaseModel):
    text: str


class SearchQuery(BaseModel):
    query: str
    top_k: int = 5


# Эндпоинт для генерации эмбеддингов и сохранения в FAISS
@app.post("/embed")
def get_embedding(input_data: TextInput):
    headers = {
        "Authorization": f"Bearer {GIGACHAT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"input": [input_data.text], "model": "GigaChatEmbedding"}

    response = requests.post(GIGACHAT_API_URL, headers=headers, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    embedding = np.array(response.json()["data"][0]["embedding"]).astype("float32").reshape(1, -1)
    index.add(embedding)
    stored_texts.append(input_data.text)

    return {"message": "Embedding stored", "index_size": index.ntotal}


# Эндпоинт для поиска по FAISS
@app.post("/search")
def search_embedding(query: SearchQuery):
    headers = {
        "Authorization": f"Bearer {GIGACHAT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"input": [query.query], "model": "GigaChatEmbedding"}

    response = requests.post(GIGACHAT_API_URL, headers=headers, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    query_embedding = np.array(response.json()["data"][0]["embedding"]).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_embedding, query.top_k)

    results = [{"text": stored_texts[i], "distance": float(distances[0][j])} for j, i in enumerate(indices[0]) if
               i < len(stored_texts)]

    return {"results": results}


# Запуск сервера
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)