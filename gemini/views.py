# views.py

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import urllib.parse

load_dotenv()
genai.configure(api_key=(os.getenv("GOOGLE_API_KEY")))

# try:
#     genai.configure(api_key=(os.getenv("GOOGLE_API_KEY_A")))
# except:
#     genai.configure(api_key=(os.getenv("GOOGLE_API_KEY_S")))

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    print(text)
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local(os.path.join(settings.BASE_DIR, "faiss_index"))
    return vector_store

def get_conversational_chain():
    prompt_template = """
    Answer the question thoroughly based on the provided code PDF input. As a code documenter, your task is to meticulously explain the code in detail each code line, including code snippets line by line , within a 2000-word limit. Additionally, provide frequently asked or related questions based on the user's query and suggest keywords for finding matching answers. Include relevant links to articles and YouTube videos related to the topic heading to enhance understanding. Ensure all pertinent details are covered. If the answer isn't explicitly stated in the provided context, utilize the information to craft an accurate response, incorporating your knowledge as necessary.

    Context:
    {context} (Provide the PDF containing the code for analysis)

    Question:
    {question}

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local(os.path.join(settings.BASE_DIR, "faiss_index"), embeddings)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    response_text = response["output_text"]
    if response_text == "":
        response_text = "It seems that the answer is out of context. Here is a general response: ..."
    return response_text

def search_related_content(query):
    search_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={search_query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = soup.find_all('div', class_='BNeawe UPmit AP7Wnd')
    related_content = []
    for i, result in enumerate(search_results):
        if i >= 3:
            break
        related_content.append(result.text)
    return related_content

def scrape_youtube_videos(query):
    search_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={search_query}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    video_results = soup.find_all('a', class_='yt-simple-endpoint style-scope ytd-video-renderer')
    related_videos = []
    for i, video in enumerate(video_results):
        if i >= 3:
            break
        video_title = video.get('title')
        video_link = f"https://www.youtube.com{video.get('href')}"
        related_videos.append((video_title, video_link))
    return related_videos

def display_related_content(related_content):
    return related_content

def gemini(request):
    if request.method == 'POST':
        # Handle PDF upload
        pdf_docs = request.FILES.getlist('pdf_files')
        raw_text = get_pdf_text(pdf_docs)
        text_chunks = get_text_chunks(raw_text)
        get_vector_store(text_chunks)

        # Handle user question
        user_question = request.POST.get('user_question')
        response_text = user_input(user_question)

        # Search related content
        related_content = search_related_content(user_question)
        youtube_content = scrape_youtube_videos(user_question)

        # Display related content
        related_content = display_related_content(related_content)

        # Return response
        return render(request, 'gemini.html', {'response_text': response_text, 'related_content': related_content})
    else:
        return render(request, 'gemini.html')

# Add appropriate URL mapping in urls.py
