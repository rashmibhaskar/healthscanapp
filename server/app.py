# from flask import Flask, request

# app = Flask(__name__)

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return 'No file part', 400
    
#     file = request.files['file']
#     # Process or save the file here
#     file.save('uploaded_file.txt')
    
#     return 'File uploaded successfully'

# if __name__ == '__main__':
#     app.run()
from flask import Flask, request
from flask_cors import CORS
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
import tempfile

app = Flask(__name__)
CORS(app)

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

client = OpenAI()

sample_prompt = """You are a medical practictioner and an expert in analzying medical related images working for a very reputed hospital. You will be provided with images and you need to identify the anomalies, any disease or health issues. You need to generate the result in detailed manner. Write all the findings, next steps, recommendation, etc. You only need to respond if the image is related to a human body and health issues. You must have to answer but also write a disclaimer saying that "Consult with a Doctor before making any decisions".

Remember, if certain aspects are not clear from the image, it's okay to state 'Unable to determine based on the provided image.'

Now analyze the image and answer the above questions in the same structured manner defined above."""

# sample_prompt = """You are a skin expert. You analyse the skin tone"""

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_gpt4_model_for_analysis(filename: str, sample_prompt=sample_prompt):
    # print(filename)
    base64_image = encode_image(filename)
    # print(base64_image)
    
    messages = [
        {
            "role": "user",
            "content":[
                {
                    "type": "text", "text": sample_prompt
                    },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                        }
                    }
                ]
            }
        ]

    response = client.chat.completions.create(
        model = "gpt-4-vision-preview",
        messages = messages,
        max_tokens = 1500
        )

    print(response.choices[0].message.content)
    return response.choices[0].message.content

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    result = call_gpt4_model_for_analysis(filename)
    
    return result
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return 'No file part', 400
    
#     file = request.files['file']
#     # Process or save the file here
#     print(file)
#     # result = call_gpt4_model_for_analysis(file)
#     file.save()
    
#     return 'File uploaded successfully'