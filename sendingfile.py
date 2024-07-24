import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Define the file path and other parameters
file_path = '/Users/sakchotekhemmarach/Documents/GitHub/Roadmap_planner_api/respondformat.json'
api_key = os.getenv("API_KEY")
prompt = 'How to Build a Desktop AI Assistant with a custom voice from character ARONA from Blue Archive'
depth = 3
retry = 2
target_node = 'Audio Engineering'

# Open the file in binary mode
with open(file_path, 'rb') as file:
    # Prepare the files and data to be sent in the request
    files = {'upload_file': file}
    # Query parameters are sent in the URL
    params = {
        'openai_api_key': api_key,
        'prompt': prompt,
        'depth': depth,
        'retry': retry,
        'target_node': target_node
    }

    # Send the POST request
    response = requests.post('http://127.0.0.1:8000/uploadfiles/', files=files, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        print("Request was successful.")
        print(response.json())
    else:
        print("Request failed.")
        print(response.text)
