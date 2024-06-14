import requests

# Replace 'your_token' with your actual GitHub personal access token
headers = {
    'Authorization': 'token your_token',
    'Accept': 'application/vnd.github.v3+json'
}

# Change 'openai' and 'gpt-3' to the target organization and repository
url = "https://api.github.com/repos/openai/gpt-3/issues"

response = requests.get(url, headers=headers)
issues = response.json()

# Extract relevant data
for issue in issues:
    print(issue['title'], issue['body'][:100])  # Print title and first 100 chars of body
import requests

url = "https://api.stackexchange.com/2.3/questions"
params = {
    'order': 'desc',
    'sort': 'activity',
    'site': 'stackoverflow',
    'tagged': 'python'
}

response = requests.get(url, params=params)
questions = response.json()

for question in questions['items']:
    print(question['title'], question['link'])


from tensorflow.keras.preprocessing.text import Tokenizer

# Assuming 'data' is a list of texts from the issues and questions
tokenizer = Tokenizer(num_words=10000)
tokenizer.fit_on_texts(data)
sequences = tokenizer.texts_to_sequences(data)


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Pad sequences to ensure uniform input size
data = pad_sequences(sequences, maxlen=200)

# Define the model
model = Sequential([
    Embedding(10000, 16, input_length=200),
    GlobalAveragePooling1D(),
    Dense(24, activation='relu'),
    Dense(1, activation='sigmoid')
])

# Compile the model 
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(data, labels, epochs=10, validation_split=0.1)
