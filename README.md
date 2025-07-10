Этот проект представляет собой Retrieval-Augmented Generation (RAG) помощника, обученного на технической документации для насосов DY. Он позволяет выполнять точечные запросы к PDF-документу через REST API или веб-интерфейс.

## Зависимости

* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/)

## Структура проекта

```
.
├── app.py                 # Streamlit UI
├── api.py                 # FastAPI REST API
├── rag_pipeline.py        # Основной пайплайн RAG
├── requirements.txt
├── Dockerfile.api
├── Dockerfile.ui
├── docker-compose.yml
├── Руководство по насосам шламовым 4 DY -AHF.pdf
└── README.md
```

## Запуск в Docker

### 1. Нужно собрать и запустить контейнеры

```bash
docker-compose up --build
```

### 2. Открыть в браузере

* **Streamlit UI:** [http://localhost:8501](http://localhost:8501)
* **API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

## REST API

### Endpoint: `POST /ask`

**URL:** `http://localhost:8000/ask`
**Content-Type:** `application/json`

### Пример запроса

```bash
curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"query": "Какой объём смазки (л) требуется для подшипниковой рамы DY?"}'
```

### Пример ответа

```json
{
  "answer": "Для подшипниковой рамы DY требуется 3,5 литра смазки. Объём зависит от конкретной конфигурации и должен соответствовать инструкции производителя."
}
```

## Переменные окружения

На данный момент переменные окружения не требуются.

## Дополнительное

* Поддерживаются модели Ollama, включая `llama3`. Нужно убедиться, что модель доступна в среде.
* Для ускорения загрузки можно сохранить Chroma VectorStore на диск (`persist_directory`).
* PDF должен быть в корне проекта или примонтирован внутрь контейнера.
