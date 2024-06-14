# forms.py

from django import forms

class CodeForm(forms.Form):
    code = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 10}), label='Python Code')

from django import forms
from django import forms

class HtmlCodeForm(forms.Form):
    html_code = forms.CharField(label='HTML Code', widget=forms.Textarea)
    css_code = forms.CharField(label='CSS Code', required=False, widget=forms.Textarea)
    js_code = forms.CharField(label='JavaScript Code', required=False, widget=forms.Textarea)

from django import forms

# from django import forms

# class CodeRequestForm(forms.Form):
#     code_description = forms.CharField(
#         widget=forms.Textarea(attrs={'placeholder': 'Describe the HTML/CSS/JS you need, e.g., "a responsive login form"'}),
#         label='Code Description'
#     )
#     code_output = forms.CharField(
#         widget=forms.Textarea(attrs={'readonly': True, 'rows': 10, 'cols': 50}),
#         required=False,
#         label='Generated Code'
#     )

class CodeRequestForm(forms.Form):
    code_description = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Describe the HTML/CSS/JS you need, e.g., "a responsive login form"'}),
        label='Code Description'
    )
    code_output = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 50}),  # Removed readonly=True
        required=False,
        label='Generated Code'
    )

from django import forms

class PythonCodeForm(forms.Form):
    input_text = forms.CharField(label='Enter your text', max_length=100, widget=forms.Textarea(attrs={'cols': 80, 'rows': 4}))
