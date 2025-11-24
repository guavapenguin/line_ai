from google import genai
import os

client = genai.Client(api_key="AIzaSyBLJRCA2VAaFagZol91BbhtPelZf7wCyIc")
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents="Explain how AI works in a few words",
)

print(response.text)
