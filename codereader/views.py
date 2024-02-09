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
            selected_repo = (request.POST.get('selected_repo'))
            print((selected_repo))
            repo_name = selected_repo.rsplit('/', 1)[1]

            # repo_url = selected_repo['url']

            contents = fetch_contents(f"{selected_repo}/contents")
            code = visualize_structure(contents, username, repo_name)

            pdf_filename = f"{username}_{repo_name}_code_documentation.pdf"
            convert_txt_to_pdf(code, pdf_filename)

            return HttpResponse(f"PDF '{pdf_filename}' generated successfully.")
        else:
            return HttpResponse("No repositories found for the given username.")
    else:
        return render(request, 'generate_pdf.html')

def convert_txt_to_pdf(content, pdf_filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in content.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)

    pdf.output(pdf_filename)

import requests
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

import requests
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

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


