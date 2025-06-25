#set GROQ API 
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


#step2: Convert Image to required format
import base64 #encoding using base64

def encode_image(image_path):
  if image_path is None:
    return None
  image_file = open(image_path,"rb")
  return base64.b64encode(image_file.read()).decode('utf-8')

#step3: Multimodal LLm setup

from groq import Groq

query="Is there something wrong with my face?"
#model = "meta-llama/llama-4-maverick-17b-128e-instruct"
model="meta-llama/llama-4-scout-17b-16e-instruct"
#model = "meta-llama/llama-4-scout-17b-16e-instruct"
#model="llama-3.2-90b-vision-preview" #Deprecated

def analyze_image_with_query(query, model, encoded_image=None):
    client = Groq()
    messages = [{"role": "user", "content": []}]
    
    # Add text query
    messages[0]["content"].append({"type": "text", "text": query})
    
    # Add image if provided
    if encoded_image:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}
        })
    
    response = client.chat.completions.create(
        messages=messages,
        model=model
    )
    return response.choices[0].message.content


# print(analyze_image_with_query(query, model, encode_image("acne.jpg")))