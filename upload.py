import os
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import re
import json

# Function to convert PDF to text and append to vault.txt
def convert_pdf_to_text():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            text = ''
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                if page.extract_text():
                    text += page.extract_text() + " "
            
            # Normalize whitespace and clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split text into chunks by sentences, respecting a maximum chunk size
            sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Check if the current sentence plus the current chunk exceeds the limit
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                    current_chunk += (sentence + " ").strip()
                else:
                    # When the chunk exceeds 1000 characters, store it and start a new one
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Don't forget the last chunk!
                chunks.append(current_chunk)
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    # Write each chunk to its own line
                    vault_file.write(chunk.strip() + "\n")  # Two newlines to separate chunks
            print(f"PDF content appended to vault.txt with each chunk on a separate line.")

# Function to upload a text file and append to vault.txt
def upload_txtfile():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as txt_file:
            text = txt_file.read()
            
            # Normalize whitespace and clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split text into chunks by sentences, respecting a maximum chunk size
            sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Check if the current sentence plus the current chunk exceeds the limit
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                    current_chunk += (sentence + " ").strip()
                else:
                    # When the chunk exceeds 1000 characters, store it and start a new one
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Don't forget the last chunk!
                chunks.append(current_chunk)
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    # Write each chunk to its own line
                    vault_file.write(chunk.strip() + "\n")  # Two newlines to separate chunks
            print(f"Text file content appended to vault.txt with each chunk on a separate line.")

# Function to upload a JSON file and append to vault.txt
def upload_jsonfile():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        with open(file_path, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
            
            # Flatten the JSON data into a single string
            text = json.dumps(data, ensure_ascii=False)
            
            # Normalize whitespace and clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split text into chunks by sentences, respecting a maximum chunk size
            sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                # Check if the current sentence plus the current chunk exceeds the limit
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                    current_chunk += (sentence + " ").strip()
                else:
                    # When the chunk exceeds 1000 characters, store it and start a new one
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Don't forget the last chunk!
                chunks.append(current_chunk)
            with open("vault.txt", "a", encoding="utf-8") as vault_file:
                for chunk in chunks:
                    # Write each chunk to its own line
                    vault_file.write(chunk.strip() + "\n")  # Two newlines to separate chunks
            print(f"JSON file content appended to vault.txt with each chunk on a separate line.")
import os
import re
from tkinter import filedialog

# Function to import markdown files from a directory
def import_markdown_directory():
    dir_path = filedialog.askdirectory()
    if dir_path:
        with open("vault.txt", "a", encoding="utf-8") as vault_file:  # Open the vault file once for writing
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(".md"):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding="utf-8") as md_file:
                            lines = md_file.readlines()
                            text = f"# Document: {file}\n"  # Add the filename as a header
                            for line in lines:
                                # Stop processing if the line reads **Problems**
                                if line.strip() == "**Problems**":
                                    break
                                # Extract headings and text
                                if line.startswith("#"):
                                    # Treat headings as important context
                                    heading_level = line.count('#')
                                    text += f"\n{' ' * (heading_level - 1)}* {line.strip()}"
                                else:
                                    text += line.strip() + " "

                            # Normalize whitespace and clean up text
                            text = re.sub(r'\s+', ' ', text).strip()
                            
                            # Split text into chunks by sentences, respecting a maximum chunk size
                            sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
                            chunks = []
                            current_chunk = ""
                            for sentence in sentences:
                                # Check if the current sentence plus the current chunk exceeds the limit
                                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                                    current_chunk += (sentence + " ").strip()
                                else:
                                    # When the chunk exceeds 1000 characters, store it and start a new one
                                    chunks.append(current_chunk)
                                    current_chunk = sentence + " "
                            if current_chunk:  # Don't forget the last chunk!
                                chunks.append(current_chunk)

                            # Write the document boundary, each chunk, and the separator to vault.txt
                            vault_file.write("\n---\n")  # Document boundary
                            for chunk in chunks:
                                # Write each chunk to its own line
                                vault_file.write(chunk.strip() + "\n")
        print(f"Markdown files from directory '{dir_path}' appended to vault.txt with each chunk on a separate line.")

# Create the main window
root = tk.Tk()
root.title("Upload local data")

# Create a button to open the file dialog for PDF
pdf_button = tk.Button(root, text="Upload PDF", command=convert_pdf_to_text)
pdf_button.pack(pady=10)

# Create a button to open the file dialog for text file
txt_button = tk.Button(root, text="Upload Text File", command=upload_txtfile)
txt_button.pack(pady=10)

# Create a button to open the file dialog for JSON file
json_button = tk.Button(root, text="Upload JSON File", command=upload_jsonfile)
json_button.pack(pady=10)

# Create a button to open the directory dialog for Markdown files
md_dir_button = tk.Button(root, text="Upload Markdown Directory", command=import_markdown_directory)
md_dir_button.pack(pady=10)

# Run the main event loop
root.mainloop()
