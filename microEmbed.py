from fastapi import FastAPI, HTTPException import faiss import numpy as np import requests import os

Настройка FastAPI

app = FastAPI()

Токен GigaChat API

GIGACHAT_TOKEN = "ВАШ_ТОКЕН" INDEX_FILE = "faiss_index.bin" D = 1024  # Размерность эмбеддинга

Загрузка FAISS индекса

if os.path.exists(INDEX_FILE): index = faiss.read_index(INDEX_FILE) else: index = faiss.IndexFlatL2(D)

Функция получения эмбеддингов

def get_gigachat_embedding(text): url = "https://gigachat-api.sberbank.ru/v1/embeddings" headers = {"Authorization": f"Bearer {GIGACHAT_TOKEN}", "Content-Type": "application/json"} data = {"input": [text], "model": "Embeddings"} response = requests.post(url, headers=headers, json=data) if response.status_code == 200: return np.array(response.json()["data"][0]["embedding"], dtype=np.float32) else: raise HTTPException(status_code=500, detail="Ошибка GigaChat API")

@app.post("/search/") async def search_text(query: str, k: int = 3): query_vector = get_gigachat_embedding(query).reshape(1, -1) distances, indices = index.search(query_vector, k) return {"indices": indices.tolist(), "distances": distances.tolist()}

