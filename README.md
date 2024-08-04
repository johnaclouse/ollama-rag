# Ollama based Retrieval-Augmented Generation

A project local retrieval-augmented gerenation solution leveraging Ollama and local reference content.

### Setup
1. git clone https://github.com/AllAboutAI-YT/easy-local-rag.git
2. cd dir
3. pip install -r requirements.txt
4. Install Ollama (https://ollama.com/download)
5. ollama pull llama3 (etc)
6. ollama pull mxbai-embed-large
7. run upload.py (pdf, .txt, JSON)
8. run localrag.py (with query re-write)
9. run localrag_no_rewrite.py (no query re-write)

### Email RAG Setup
1. git clone https://github.com/AllAboutAI-YT/easy-local-rag.git
2. cd dir
3. pip install -r requirements.txt
4. Install Ollama (https://ollama.com/download)
5. ollama pull llama3 (etc)
6. ollama pull mxbai-embed-large
7. set YOUR email logins in .env (for gmail create app password (video))
9. python collect_emails.py to download your emails
10. python emailrag2.py to talk to your emails

### Latest Updates
   
### Reference

### RAG

### Ollama

## Citation

This project is based on code from https://github.com/AllAboutAI-YT/easy-local-rag. Thank you to Kris at AllAboutAI-YT for sharing this work.
