from django.shortcuts import render
from django.http import HttpResponse
import os
import requests
from fpdf import FPDF
import requests
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

def fetch_repositories(username):
    """
    Fetches repositories for the given GitHub username.
    
    Args:
    - username (str): The GitHub username.
    
    Returns:
    - repositories (list): A list of dictionaries containing repository details.
    """
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code} occurred while fetching repositories.")
        return []

# def select_repository(repositories):
#     """
#     Allows the user to select a repository from the list of repositories.

#     Args:
#     - repositories (list): A list of dictionaries containing repository details.

#     Returns:
#     - selected_repo (dict): The selected repository.
#     """
#     print("Select a repository:")
#     for idx, repo in enumerate(repositories, 1):
#         print(f"{idx}: {repo['name']}")
#     repo_idx = int(input("Enter the repository number: ")) - 1
#     return repositories[repo_idx]

def fetch_contents(url):
    """
    Fetches the contents (files and directories) from the provided URL.
    
    Args:
    - url (str): The URL to fetch contents from.
    
    Returns:
    - contents (list): A list of dictionaries containing file/folder details.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code} occurred while fetching contents.")
        return []

def visualize_structure(contents, username, repo_name):
    """
    Visualizes the folder structure recursively and documents code for files.
    
    Args:
    - contents (list): A list of dictionaries containing file/folder details.
    - username (str): The GitHub username.
    - repo_name (str): The repository name.
    """
    result = ""
    for item in contents:
        if item['type'] == 'dir':
            result += f"Folder: {item['name']}\n"
            subdir_contents = fetch_contents(item['url'])
            result += visualize_structure(subdir_contents, username, repo_name)
        else:
            filename = item['name']
            if filename.endswith(('.py', '.dart', '.html')):
                raw_url = item['download_url']
                code = fetch_code(raw_url)
                result += f"File: {filename}\n"
                result += f"Documented code for {filename}:\n{code}\n\n"
    return result

def fetch_code(raw_url):
    """
    Fetches and documents code for the specified file.
    
    Args:
    - raw_url (str): The raw URL of the file.
    
    Returns:
    - code (str): The documented code.
    """
    response = requests.get(raw_url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error {response.status_code} occurred while fetching code.")
        return None

def generate_pdf(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        repositories = fetch_repositories(username)

        if repositories:
            selected_repo = request.POST.get('selected_repo')
            repo_name = selected_repo.split('/')[-1]  # Extract the repository name from the URL

            contents = fetch_contents(selected_repo)
            code = visualize_structure(contents, username, repo_name)

            # Construct the PDF filename
            pdf_filename = f"{username}_{repo_name}_code_documentation.pdf"

            # Call the function to convert content to PDF
            convert_txt_to_pdf(code, pdf_filename)

            return HttpResponse(f"PDF '{pdf_filename}' generated successfully.")
        else:
            return HttpResponse("No repositories found for the given username.")
    else:
        return render(request, 'profile-page.html')


# def convert_txt_to_pdf(content, pdf_filename):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)

#     for line in content.split('\n'):
#         pdf.cell(200, 10, txt=line, ln=True)

#     pdf.output(pdf_filename)
    
def convert_txt_to_pdf(content, pdf_filename):
    # Create an instance of FPDF
    pdf = FPDF()
    
    # Add a page to the PDF
    pdf.add_page()
    
    # Set font for the PDF
    pdf.set_font("Arial", size=12)

    # Set the desired cell width and line height
    cell_width = 190
    line_height = 8

    is_python_code_block = False  # Flag to track whether the current block is a Python code block

    # Iterate through each line in the content
    for line in content.split('\n'):
        # Check if the line is the start of a Python code block
        if line.strip().startswith('```python'):
            pdf.set_fill_color(200, 220, 255)  # Set a background color for the code block
            is_python_code_block = True
            pdf.multi_cell(cell_width, line_height, txt='', fill=True)  # Add an empty line for separation
        # Check if the line is the end of a Python code block
        elif is_python_code_block and line.strip().endswith('```'):
            line += '\n'  # Ensure the closing ``` is on its own line
            pdf.multi_cell(cell_width, line_height, txt=line, fill=True)
            is_python_code_block = False
        # Check if the line is within a Python code block
        elif is_python_code_block:
            pdf.multi_cell(cell_width, line_height, txt=line, fill=True)
        # Handle non-code lines
        else:
            pdf.multi_cell(cell_width, line_height, txt=line)

    # Output the PDF to the specified filename
    pdf.output(pdf_filename)



def get_github_user_data(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve user data from GitHub API. Status code: {response.status_code}")
        return None

def get_github_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve repository data from GitHub API. Status code: {response.status_code}")
        return None

def get_repo_details(repo):
    languages_url = repo.get("languages_url")
    commits_url = f"{repo.get('url')}/commits"
    languages_response = requests.get(languages_url)
    commits_response = requests.get(commits_url)
    if languages_response.status_code == 200 and commits_response.status_code == 200:
        languages_data = languages_response.json()
        commits_data = commits_response.json()
        return {
            'languages': languages_data,
            'commits_count': min(len(commits_data), 10),
            'repo_name': repo.get("name")  # Include repo_name here
        }
    else:
        return None

def profile_metrics_calculation(username):
    user_data = get_github_user_data(username)
    repos_data = get_github_repos(username)
    
    if user_data is None or repos_data is None:
        return None
    
    language_counts = defaultdict(int)
    commits_info = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_repo_details, repo) for repo in repos_data]
        for future in futures:
            result = future.result()
            if result:
                languages_data = result['languages']
                for language in languages_data:
                    language_counts[language] += 1
                commits_info.append({
                    'repo_name': result['repo_name'],  # Access repo_name from result
                    'commits_count': result['commits_count']
                })

    top_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)

    return {
        'username': username,
        'avatar_url': user_data.get("avatar_url"),
        'name': user_data.get("name"),
        'total_repos': user_data.get("public_repos"),
        'followers': user_data.get("followers"),
        'following': user_data.get("following"),
        'top_languages': top_languages,
        'commits_info': commits_info
    }


def profile_analysis(request):
    data = None
    if request.method == "POST":
        username = request.POST.get('username')
        data = profile_metrics_calculation(username)
        if data is None:
            error = 'Failed to retrieve user data.'
            return render(request, 'profile.html', {'error': error})
    return render(request, 'profile.html', {'data': data})




# def profile_analyzer(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         github_avatar = "https://avatars.githubusercontent.com/u/120780784?v=4"
#         user_profile_link = f"https://github.com/{username}"
#         user_bio = ""
#         user_location = ""
#         user_top_languages = ""
#         total_repos = ""
#         total_commits_repowise = ""
#         total_followers = ""
#         total_subscribers = ""
#         #graph 
#         commits_overtime = ""

#         content = {
#             '' : ,

#         }
#         return render(request, 'profile_analyzer.html',content)


def index(request):
    return render(request, 'index.html')

def user_signin(request):
    return render(request, 'register-page.html')


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
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()
genai.configure(api_key=(os.getenv("GOOGLE_API_KEY")))

# def get_pdf_text(pdf_docs):
#     text = ""
#     for pdf in pdf_docs:
#         pdf_reader = PdfReader(pdf)
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#     print(text)
#     return text

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
Explain the provided code snippet by breaking it down line by line. Provide a detailed explanation for each portion, function, or line of code. Aim to make the explanation accessible for a beginner or intermediate-level programmer, ensuring a step-by-step understanding. The total word count for the explanation should not exceed 2000 words.

---

**Code Explanation:**

ADD only the necessary points you see fit in the provided code and give the code snippet while explaining each part

1. **Line 1: Import Statements**
   Explain any libraries or modules imported in the first line. Clarify their role in the code and how they contribute to its functionality.

2. **Line 2-5: Variable Declarations**
   Break down the variables declared in these lines. Explain their purposes, data types, and any initial values assigned. Help the reader understand the significance of each variable.

3. **Line 6-10: User Input Handling**
   If the code involves user input, explain how it is handled in these lines. Detail the prompt or expected input and describe any validation or processing steps.

4. **Line 11-15: Control Flow - Part 1**
   Start explaining any conditional statements or control flow structures in this section. Clarify the conditions and describe how the code branches based on them.

5. **Line 16-20: Function Calls - Part 1**
   If there are function calls, break down each function's role in these lines. Describe the parameters passed, the function's purpose, and any return values. Provide examples if applicable.

6. **Line 21-25: Looping Structures**
   If the code includes loops, explain their purpose and how they iterate through data. Clarify any exit conditions and describe the actions performed in each iteration.

7. **Line 26-30: Data Manipulation**
   Discuss any operations related to data manipulation in this section. Explain the logic behind these operations and how they contribute to the overall functionality.

8. **Line 31-35: Control Flow - Part 2**
   Continue explaining additional conditional statements or control flow structures in this portion. Provide clear explanations for each condition and the corresponding code execution.

9. **Line 36-40: Function Calls - Part 2**
   If there are more function calls, continue breaking down their roles in this section. Explain any interdependencies between functions and how they contribute to the overall code logic.

10. **Line 41-45: Output Generation**
    Describe how the code generates output in these lines. Clarify the intended output format and any display mechanisms used.

11. **Line 46-50: Error Handling**
    If the code includes error handling mechanisms, explain how errors are identified and addressed. Describe any try-except blocks and the expected behavior in case of errors.

---

**Conclusion:**

Summarize the key points from your explanation. Reinforce the overall purpose of the code and highlight important concepts that a beginner or intermediate programmer should grasp.

---

Note: Keep the explanations concise and provide examples where necessary to enhance understanding.

    Context:
    {context} (Provide the code for analysis)

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



def gemini(filename, code):
    response_text1=""
    if code :
        # Handle PDF upload
        # pdf_docs = request.FILES.getlist('pdf_files')
        # raw_text = get_pdf_text(pdf_docs)

        text_chunks = get_text_chunks(code)
        get_vector_store(text_chunks)

        # Handle user question
        # user_question = request.POST.get('user_question')
        user_question = f'Explain {filename} in detail step by step in detail along with the necessary code snippets code snippets'
        response_text1 += f"File: {filename}\n"
        response_text = user_input(user_question)
        response_text1 += f"Documented code for {filename}:\n{response_text}\n\n"

        return(response_text1)
        


        # Search related content
        # related_content = search_related_content(user_question)
        # youtube_content = scrape_youtube_videos(user_question)

        # # Display related content
        # related_content = display_related_content(related_content)

        # Return response
    #     return render('gemini.html', {'response_text': response_text})
    # else:
    #     return render('gemini.html')
    

def generate_pdf1(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        repositories = fetch_repositories(username)
        if repositories:
            selected_repo = (request.POST.get('selected_repo'))
            print((selected_repo))
            repo_name = selected_repo.rsplit('/', 1)[1]

            contents = fetch_contents(f"{selected_repo}/contents")
            code = documentation(contents, username, repo_name)
            code1 = visualize_structure(contents, username, repo_name)

            # Construct the PDF filename
            pdf_filename = f"{username}_{repo_name}_code.pdf"

            # Call the function to convert content to PDF
            convert_txt_to_pdf(code1, pdf_filename)


            pdf_filename = f"{username}_{repo_name}_code_documentation.pdf"
            convert_txt_to_pdf(code, pdf_filename)

            content = {
                'code' : code.splitlines(),
            }
            return render(request, 'test.html',content)
            # return HttpResponse(f"PDF '{pdf_filename}' generated successfully.")
        else:
            return HttpResponse("No repositories found for the given username.")
    else:
        return render(request, 'generate_pdf.html')



def documentation(contents, username, repo_name):
    result = ""
    with ThreadPoolExecutor() as executor:
        futures = []
        for item in contents:
            if item['type'] == 'dir':
                result += f"Folder: {item['name']}\n"
                subdir_contents = fetch_contents(item['url'])
                futures.append(executor.submit(documentation, subdir_contents, username, repo_name))

            else:
                filename = item['name']
                if filename.endswith(('.py', '.dart')):
                    raw_url = item['download_url']
                    code = fetch_code(raw_url)
                    futures.append(executor.submit(gemini, filename, code))

        for future in as_completed(futures):
            try:
                result1 = future.result()
                if result1 is not None:
                    result += result1
            except Exception as e:
                # Handle exceptions gracefully
                result += f"Error processing: {e}\n" 
    return result