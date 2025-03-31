import re
import httpx
import os
import json
import base64
from fastapi import UploadFile  # type: ignore

BASE_URL = "https://aiproxy.sanand.workers.dev/openai/v1"


def GA3_1(question: str):
    match = re.search(r"meaningless text:\s*(.*?)\s*Write a",
                      question, re.DOTALL)

    if not match:
        return "Error: No match found in the input string."

    meaningless_text = match.group(1).strip()

    python_code = f"""
import httpx
model = "gpt-4o-mini"
messages = [
    {{"role": "system", "content": "LLM Analyze the sentiment of the text. Make sure you mention GOOD, BAD, or NEUTRAL as the categories."}}, 
    {{"role": "user", "content": "{meaningless_text}"}}
]
data = {{"model": model,"messages": messages}}
headers = {{"Content-Type": "application/json","Authorization": "Bearer dummy_api_key"}}
response = httpx.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
print(response.json())"""
    return python_code

# question="""
# DataSentinel Inc. is a tech company specializing in building advanced natural language processing (NLP) solutions. Their latest project involves integrating an AI-powered sentiment analysis module into an internal monitoring dashboard. The goal is to automatically classify large volumes of unstructured feedback and text data from various sources as either GOOD, BAD, or NEUTRAL. As part of the quality assurance process, the development team needs to test the integration with a series of sample inputs—even ones that may not represent coherent text—to ensure that the system routes and processes the data correctly.

# Before rolling out the live system, the team creates a test harness using Python. The harness employs the httpx library to send POST requests to OpenAI's API. For this proof-of-concept, the team uses the dummy model gpt-4o-mini along with a dummy API key in the Authorization header to simulate real API calls.

# One of the test cases involves sending a sample piece of meaningless text:

# d4A aWl1FbqmD9 j SEIWdsMNo Jw e8cRbq  v  WCu WQL K
# Write a Python program that uses httpx to send a POST request to OpenAI's API to analyze the sentiment of this (meaningless) text into GOOD, BAD or NEUTRAL. Specifically:

# Make sure you pass an Authorization header with dummy API key.
# Use gpt-4o-mini as the model.
# The first message must be a system message asking the LLM to analyze the sentiment of the text. Make sure you mention GOOD, BAD, or NEUTRAL as the categories.
# The second message must be exactly the text contained above.
# This test is crucial for DataSentinel Inc. as it validates both the API integration and the correctness of message formatting in a controlled environment. Once verified, the same mechanism will be used to process genuine customer feedback, ensuring that the sentiment analysis module reliably categorizes data as GOOD, BAD, or NEUTRAL. This reliability is essential for maintaining high operational standards and swift response times in real-world applications.

# Note: This uses a dummy httpx library, not the real one. You can only use:

# response = httpx.get(url, **kwargs)
# response = httpx.post(url, json=None, **kwargs)
# response.raise_for_status()
# response.json()
# Code
# """
# print(GA3_1(question))


def GA3_2(question: str):
    match = re.search(
        r"List only the valid English words from these:(.*?)\s*\.\.\. how many input tokens does it use up?",
        question, re.DOTALL
    )
    if not match:
        return "Error: No valid input found."
    user_message = "List only the valid English words from these: " + \
        match.group(1).strip()
    # Make a real request to get the accurate token count
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": user_message}]
    }
    API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjIwMDQ1OTVAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.7B5ZZjxXdte_XTR9x7UGkOzvekGIJjSNcJ6Zrb2NVbk"
    # API_KEY = os.getenv("AIPROXY_TOKEN")  # Set this variable in your system
    # print(API_KEY)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    response = httpx.post(BASE_URL + "/chat/completions",
                          json=data, headers=headers, timeout=60)

    return response.json().get("usage", {}).get("prompt_tokens")


# question="""
# Specifically, when you make a request to OpenAI's GPT-4o-Mini with just this user message:

# List only the valid English words from these: 4CyRh5aMGr, YfH9DFZeI, rmNyoh6u, k, 6IdO, OC
# ... how many input tokens does it use up?
# """
# print(GA3_2(question))

def GA3_3(question: str):
    match = re.search(
        r"Uses structured outputs to respond with an object addresses which is an array of objects with required fields: "
        r"(\w+)\s*\(\s*(\w+)\s*\)\s*"
        r"(\w+)\s*\(\s*(\w+)\s*\)\s*"
        r"(\w+)\s*\(\s*(\w+)\s*\)",
        question
    )

    if match:
        field1, type1, field2, type2, field3, type3 = match.groups()
    else:
        print("No match found")
        return None  # Return None if no match is found

    # Ensure the type values are correctly formatted in JSON
    type1 = type1.lower()
    type2 = type2.lower()
    type3 = type3.lower()

    json_data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Respond in JSON"},
            {"role": "user", "content": "Generate 10 random addresses in the US"}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "addresses",
                "schema": {
                    "type": "object",
                    "description": "An address object to insert into the database",
                    "properties": {
                        "addresses": {
                            "type": "array",
                            "description": "A list of random addresses",
                            "items": {
                                "type": "object",
                                "properties": {
                                    field1: {"type": type1, "description": f"The {field1} of the address."},
                                    field2: {"type": type2, "description": f"The {field2} of the address."},
                                    field3: {
                                        "type": type3, "description": f"The {field3} of the address."}
                                },
                                "additionalProperties": False,
                                "required": [field1, field2, field3]
                            }
                        }
                    }
                }
            }
        }
    }

    return json_data  # Return parsed JSON object


# question="""
# As part of the integration process, you need to write the body of the request to an OpenAI chat completion call that:

# Uses model gpt-4o-mini
# Has a system message: Respond in JSON
# Has a user message: Generate 10 random addresses in the US
# Uses structured outputs to respond with an object addresses which is an array of objects with required fields: zip (number) city (string) longitude (number) .
# Sets additionalProperties to false to prevent additional properties.
# Note that you don't need to run the request or use an API key; your task is simply to write the correct JSON body.

# What is the JSON body we should send to https://api.openai.com/v1/chat/completions for this? (No need to run it or to use an API key. Just write the body of the request below.)
# """
# print(GA3_3(question))

async def GA3_4(question: str, file: UploadFile):
    if not file or not file.filename:
        return {"error": "No file uploaded"}

    binary_data = await file.read()
    if not binary_data:
        return {"error": "Uploaded file is empty"}

    image_b64 = base64.b64encode(binary_data).decode()

    json_data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract text from this image."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                    }
                ]
            }
        ]
    }

    return json_data


def GA3_5(question: str):
    matches = re.findall(
        r"Dear user, please verify your transaction code (\d+) sent to ([\w.%+-]+@[\w.-]+\.\w+)", question)

    if matches:
        extracted_messages = [
            f"Dear user, please verify your transaction code {code} sent to {email}" for code, email in matches]
        print(extracted_messages)  # Debugging line

        result = {
            "model": "text-embedding-3-small",
            "input": extracted_messages
        }
        return result 
    else:
        return {"error": "Invalid format"}


def GA3_6(question: str):
    python_code = """
import numpy as np
def most_similar(embeddings):
    phrases = list(embeddings.keys())
    embedding_values = np.array(list(embeddings.values()))
    similarity_matrix = np.dot(embedding_values, embedding_values.T)
    norms = np.linalg.norm(embedding_values, axis=1)
    similarity_matrix = similarity_matrix / np.outer(norms, norms)
    np.fill_diagonal(similarity_matrix, -1)
    max_indices = np.unravel_index(np.argmax(similarity_matrix, axis=None), similarity_matrix.shape)
    phrase1,phrase2 = phrases[max_indices[0]],phrases[max_indices[1]]
    return (phrase1, phrase2)
    """
    print(python_code)
    return python_code
