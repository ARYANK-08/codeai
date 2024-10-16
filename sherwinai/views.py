import requests
from django.shortcuts import render
import re
import google.generativeai as genai
from django.shortcuts import render, redirect
from .forms import HtmlCodeForm, CodeRequestForm
import google.generativeai as genai
from django.shortcuts import render
from .forms import CodeRequestForm
import sys
from io import StringIO
from django.shortcuts import render
from django.views import View
from .forms import CodeForm
from django.utils.safestring import mark_safe
import re
from django.shortcuts import render
from .forms import PythonCodeForm
import re
# Configure the API
genai.configure(api_key="AIzaSyCWxLcSHWh_ccrE15Gyo0t_8WhPfAXXelM")

def fetch_gemini_code(description):
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    convo = model.start_chat(history=[])
    convo.send_message(description)
    return convo.last.text


def code_runner(request):
    generated_code = None
    if request.method == 'POST':
        form = CodeRequestForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data['code_description']
            if 'generate' in request.POST:
                
                generated_code = fetch_gemini_code(f"{description} ")
                generated_code = clean_html_code(generated_code)  # Clean the code
            elif 'run' in request.POST:
                generated_code = form.cleaned_data['code_output']
                generated_code = clean_html_code(generated_code)  # Clean the code

            form = CodeRequestForm(initial={
                'code_description': description,
                'code_output': generated_code
            })
    else:
        form = CodeRequestForm()

    return render(request, 'sherwinai/code_runner.html', {
        'form': form,
        'generated_code': generated_code
    })


def clean_html_code(html_code):
    # Replace ```css with <style> tag
    html_code = re.sub(r'```css\s*([\s\S]*?)```', r'<style>\1</style>', html_code)
    
    # Replace ```js with <script> tag
    html_code = re.sub(r'```js\s*([\s\S]*?)```', r'<script>\1</script>', html_code)
    
    # Remove HTML comments
    html_code = re.sub(r'<!--.*?-->', '', html_code, flags=re.DOTALL)
    

    return html_code



def python_generate_code(request):
    generated_code = ''
    form = PythonCodeForm()
    context = 'using single quotes only'

    if request.method == 'POST':
        form = PythonCodeForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data['input_text']
            # Concatenate context with input_text
            input_text_with_context = f"{context}: {input_text}"
            generated_code = fetch_gemini_code(input_text_with_context)

            # Clean the generated code
            pattern = r"```python(.*?)```"
            match = re.search(pattern, generated_code, re.DOTALL)
            if match:
                generated_code = match.group(1).strip()
            print(generated_code)

            if 'debug-btn' in request.POST:
                debug_result = gemini_debug(generated_code)
                return render(request, 'emmuai/python-ai.html', {'form': form, 'generated_code': generated_code, 'debug_result': debug_result})
            elif 'explain-btn' in request.POST:
                explanation_result = gemini_explain(generated_code)
                return render(request, 'emmuai/python-ai.html', {'form': form, 'generated_code': generated_code, 'explanation_result': explanation_result})
            elif 'optimize-btn' in request.POST:
                optimized_code = gemini_optimize(generated_code)
                return render(request, 'emmuai/python-ai.html', {'form': form, 'generated_code': generated_code, 'optimized_code': optimized_code})


    return render(request, 'emmuai/python-ai.html', {'form': form, 'generated_code': generated_code})

def gemini_debug(code):
    response = model.generate_text(prompt=f"Debug this Python code:\n```python\n{code}\n```")
    return response.result

def gemini_explain(code):
    response = model.generate_text(prompt=f"Explain this Python code and give detailed in depth explaination line by line:\n```python\n{code}\n```")
    print(response.result)
    return response.result

def gemini_optimize(code):
    response = model.generate_text(prompt=f"Optimize this Python code for efficiency and performance:\n```python\n{code}\n```")
    return response.result

# def python_generate_code(request):
#     generated_code = ''
#     if request.method == 'POST':
#         form = PythonCodeForm(request.POST)
#         if form.is_valid():
#             input_text = form.cleaned_data['input_text']
#             # Use Gemini to fetch code based on input_text
#             generated_code = fetch_gemini_code(input_text)
#                     # Clean the generated code
#             pattern = r"```python(.*?)```"  # Regex pattern to match code block
#             match = re.search(pattern, generated_code, re.DOTALL)  # Search for code block
#             if match:
#                 generated_code = match.group(1).strip()  # Extract and clean the code
#                 print(generated_code)

#     else:
#         form = PythonCodeForm()

#     return render(request, 'emmuai/python-ai.html', {'form': form, 'generated_code': generated_code})





# OG RUNNING 
# def code_runner(request):
#     generated_code = ''  # Initialize generated_code to an empty string

#     if request.method == 'POST':
#         form = CodeRequestForm(request.POST)
#         if form.is_valid():
#             description = form.cleaned_data['code_description']
#             # Assuming fetch_gemini_code is a function that generates code based on description
#             generated_code = fetch_gemini_code(description)
#     else:
#         form = CodeRequestForm()

#     return render(request, 'sherwinai/code_runner.html', {
#         'form': form,
#         'generated_code': generated_code
#     })

















# from django.shortcuts import render

# # Create your views here.
# """
# At the command line, only need to run once to install the package via pip:

# $ pip install google-generativeai
# """

# import google.generativeai as genai

# genai.configure(api_key="YOUR_API_KEY")

# # Set up the model
# generation_config = {
#   "temperature": 0.9,
#   "top_p": 1,
#   "top_k": 1,
#   "max_output_tokens": 2048,
# }

# safety_settings = [
#   {
#     "category": "HARM_CATEGORY_HARASSMENT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_HATE_SPEECH",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
#   {
#     "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#   },
# ]

# model = genai.GenerativeModel(model_name="gemini-1.0-pro",
#                               generation_config=generation_config,
#                               safety_settings=safety_settings)

# convo = model.start_chat(history=[
# ])

# convo.send_message("YOUR_USER_INPUT")
# print(convo.last.text)




class RunCodeView(View):
    form_class = CodeForm
    template_name = 'sherwinai/execute_code.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            # Capture output
            old_stdout = sys.stdout
            redirected_output = sys.stdout = StringIO()
            try:
                exec(code)
            except Exception as e:
                output = str(e)
            else:
                sys.stdout.seek(0)
                output = redirected_output.read()
            finally:
                sys.stdout = old_stdout
            return render(request, self.template_name, {'form': form, 'output': output})
        return render(request, self.template_name, {'form': form})

# from django.shortcuts import render
# from .forms import HtmlCodeForm

# def code_runner(request):
#     html_code = ''
#     css_code = ''
#     js_code = ''
    
#     if request.method == 'POST':
#         form = HtmlCodeForm(request.POST)
#         if form.is_valid():
#             html_code = form.cleaned_data['html_code']
#             css_code = form.cleaned_data['css_code']
#             js_code = form.cleaned_data['js_code']
#     else:
#         form = HtmlCodeForm()

#     return render(request, 'sherwinai/code_runner.html', {
#         'form': form,
#         'html_code': html_code,
#         'css_code': css_code,
#         'js_code': js_code
#     })

