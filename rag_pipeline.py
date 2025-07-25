# -*- coding: utf-8 -*-

from typing import List

from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_ollama import OllamaLLM
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate


def load_documents(pdf_path: str) -> List:
    """
    Загружает документы из PDF-файла с помощью PyMuPDFLoader.

    :param pdf_path: Путь к PDF-файлу
    :return: Список загруженных документов
    """
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    print(f"Загружено страниц: {len(documents)}")
    print("Пример содержимого:\n", documents[0].page_content[:500])
    return documents


def split_documents(documents: List) -> List:
    """
    Разделяет документы на части заданного размера.

    :param documents: Список документов
    :return: Список фрагментов текста
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return text_splitter.split_documents(documents)


def create_rag_chain(documents: List) -> callable:
    """
    Создаёт цепочку RAG (retrieval-augmented generation).

    :param documents: Список документов
    :return: Функция для выполнения запросов
    """
    embeddings = SentenceTransformerEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory="db"
    )
    retriever = vectorstore.as_retriever()

    llm = OllamaLLM(model="llama3", temperature=0.7, num_ctx=4096)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Ты — технический помощник. Отвечай на вопрос **развёрнуто**, "
            "в виде одного или двух абзацев. Используй контекст. "
            "Указывай единицы измерения и поясняй смысл, если это уместно. "
            "Если информации нет — честно скажи 'Не знаю'."
        ),
        ("human", "Вопрос: {input}\n\nКонтекст:\n{context}")
    ])

    stuff_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, stuff_chain)


def ask(rag_chain: callable, query: str) -> None:
    """
    Выполняет запрос к цепочке RAG и выводит результат.

    :param rag_chain: Функция цепочки RAG
    :param query: Строка запроса
    """
    response = rag_chain.invoke({"input": query})
    print("Ответ:\n", response["answer"])


def main() -> None:
    """
    Основная функция запуска процесса загрузки, обработки документов и запросов.
    """
    pdf_path = "Руководство по насосам шламовым 4 DY -AHF.pdf"
    documents = load_documents(pdf_path)
    chunks = split_documents(documents)
    rag_chain = create_rag_chain(chunks)

    print("--- ВОПРОСЫ ---")
    questions = [
        "Какой объём смазки (л) требуется для подшипниковой рамы DY?",
        "Укажите кинематическую вязкость масла при 40°C для подшипников.",
        "Заводская смазка для камеры центробежного уплотнения?",
        "Номер телефона сервисной линии в Финляндии?",
        "Ширина ремня (мм) для шкивов 170-224 мм, профиль SPB?",
        "Класс NLGI для смазки камеры уплотнения?",
        "Индекс вязкости DIN‑ISO 2909 для масла?",
        "Какие три требования техники безопасности при подъёме насоса CV?"
    ]

    for question in questions:
        ask(rag_chain, question)


if __name__ == "__main__":
    main()
