import torch
import ollama
import os
import argparse
import json
import numpy as np
from openai import OpenAI

# ANSI escape codes for colors
PINK = '\033[95m'
CYAN = '\033[96m'
YELLOW = '\033[93m'
NEON_GREEN = '\033[92m'
RESET_COLOR = '\033[0m'

# open file and return contents as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Function to split documents into overlapping chunks
def chunk_document(document, chunk_size=512, overlap=50):
    words = document.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# Get relevant context from the vault based on user prompt
def get_relevant_context(rewritten_input, vault_embeddings, vault_content, similarity_threshold=0.7, max_results=10):
    if vault_embeddings.nelement() == 0:
        return []
    
    # Encode the rewritten input
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    input_tensor = torch.tensor(input_embedding).unsqueeze(0)
    
    # Calculate cosine similarity
    cos_scores = torch.cosine_similarity(input_tensor, vault_embeddings)
    
    # Apply a similarity threshold
    above_threshold_indices = torch.where(cos_scores > similarity_threshold)[0]
    if len(above_threshold_indices) == 0:
        return []
    
    # Get indices of top results
    top_indices = torch.topk(cos_scores[above_threshold_indices], k=min(max_results, len(above_threshold_indices)))[1]
    relevant_context = [vault_content[above_threshold_indices[idx]].strip() for idx in top_indices]
    
    return relevant_context

def rewrite_query(user_input_json, conversation_history, ollama_model):
    user_input = json.loads(user_input_json)["Query"]
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-2:]])
    prompt = f"""Rewrite the following query by incorporating relevant context from the conversation history.
    The rewritten query should:
    
    - Preserve the core intent and meaning of the original query
    - Expand and clarify the query to make it more specific and informative for retrieving relevant context
    - Avoid introducing new topics or queries that deviate from the original query
    - DONT EVER ANSWER the Original query, but instead focus on rephrasing and expanding it into a new query
    
    Return ONLY the rewritten query text, without any additional formatting or explanations.
    
    Conversation History:
    {context}
    
    Original query: [{user_input}]
    
    Rewritten query: 
    """
    response = client.chat.completions.create(
        model=ollama_model,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
        n=1,
        temperature=0.1,
    )
    # Extract the rewritten query from the model's response
    rewritten_query = response.choices[0].message.content.strip()
    return json.dumps({"Rewritten Query": rewritten_query})

def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
    conversation_history.append({"role": "user", "content": user_input})
    
    # First query does not need to be re-written
    if len(conversation_history) > 1:
        query_json = {"Query": user_input}
        rewritten_query_json = rewrite_query(json.dumps(query_json), conversation_history, ollama_model)
        rewritten_query_data = json.loads(rewritten_query_json)
        rewritten_query = rewritten_query_data["Rewritten Query"]
        print(PINK + "Original Query: " + user_input + RESET_COLOR)
        print(PINK + "Rewritten Query: " + rewritten_query + RESET_COLOR)
    else:
        rewritten_query = user_input

    # Feed rewritten query to get_relevant_context. The rewritten query is passed to the get_relevant_context 
    # function which retrieves relevant context from the vector database.    
    relevant_context = get_relevant_context(rewritten_query, vault_embeddings, vault_content)    
    if relevant_context:
        context_str = "\n".join(relevant_context)
        print("Context Pulled from Documents: \n\n" + CYAN + context_str + RESET_COLOR)
    else:
        print(CYAN + "No relevant context found." + RESET_COLOR)
    
    user_input_with_context = user_input + ("\n\nRelevant Context:\n" + context_str if relevant_context else "")
    conversation_history[-1]["content"] = user_input_with_context
    
    messages = [{"role": "system", "content": system_message}, *conversation_history]
    
    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages,
        max_tokens=2000,
    )
    
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
    
    return response.choices[0].message.content

# Parse command-line arguments
print(NEON_GREEN + "Parsing command-line arguments..." + RESET_COLOR)
parser = argparse.ArgumentParser(description="Ollama Chat")
parser.add_argument("--model", default="llama3.1", help="Ollama model to use (default: llama3.1)")
parser.add_argument("--similarity_threshold", type=float, default=0.7, help="Cosine similarity threshold for context retrieval (default: 0.7)")
args = parser.parse_args()

# Configureation for the Ollama API client
print(NEON_GREEN + "Initializing Ollama API client..." + RESET_COLOR)
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='llama3'
)

# Load the vault content
print(NEON_GREEN + "Loading vault content..." + RESET_COLOR)
vault_content = []
if os.path.exists("vault.txt"):
    with open("vault.txt", "r", encoding='utf-8') as vault_file:
        for line in vault_file:
            chunks = chunk_document(line)
            vault_content.extend(chunks)

# Generate embeddings for the vault content using Ollama
print(NEON_GREEN + "Generating embeddings for the vault content..." + RESET_COLOR)
vault_embeddings = []
for content in vault_content:
    response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
    vault_embeddings.append(response["embedding"])

print("Converting embeddings to tensor...")
vault_embeddings_tensor = torch.tensor(vault_embeddings)
print("Embeddings for each line in the vault:")
print(vault_embeddings_tensor)

print("Starting conversation loop...")
conversation_history = []
system_message = "You are a helpful assistant that is an expert at extracting the most useful information from a given text. Also bring in extra relevant information to the user query from outside the given context."

while True:
    user_input = input(YELLOW + "Ask a query about your documents (or type 'quit' to exit): " + RESET_COLOR)
    if user_input.lower() == 'quit':
        break
    
    response = ollama_chat(user_input, system_message, vault_embeddings_tensor, vault_content, args.model, conversation_history)
    print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)