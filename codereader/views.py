from django.shortcuts import render
from django.http import HttpResponse
import os
import requests
from fpdf import FPDF

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

def select_repository(repositories):
    """
    Allows the user to select a repository from the list of repositories.
    
    Args:
    - repositories (list): A list of dictionaries containing repository details.
    
    Returns:
    - selected_repo (dict): The selected repository.
    """
    print("Select a repository:")
    for idx, repo in enumerate(repositories, 1):
        print(f"{idx}: {repo['name']}")
    repo_idx = int(input("Enter the repository number: ")) - 1
    return repositories[repo_idx]

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
            if filename.endswith(('.py', '.dart')):
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
            selected_repo = select_repository(repositories)
            repo_name = selected_repo['name']
            repo_url = selected_repo['url']

            contents = fetch_contents(f"{repo_url}/contents")
            code = visualize_structure(contents, username, repo_name)
            
            pdf_filename = f"{username}_{repo_name}_code_documentation.pdf"
            convert_txt_to_pdf(code, pdf_filename)
            
            return HttpResponse(f"PDF '{pdf_filename}' generated successfully.")
        else:
            return HttpResponse("No repositories found for the given username.")
    else:
        return render(request, 'generate_pdf.html')

from fpdf import FPDF


def convert_txt_to_pdf(content, pdf_filename):
    # Create PDF object with specified parameters
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Write content to PDF
    for line in content.split('\n'):
        # Encode the line as UTF-8 to support a wider range of characters
        line_utf8 = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(200, 10, txt=line_utf8, ln=True)

    # Output PDF to file
    pdf.output(pdf_filename)


