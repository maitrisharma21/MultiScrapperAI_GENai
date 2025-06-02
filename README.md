# 🧠 Multiscrapper AI
Multiscrapper AI is an intelligent content extraction and question-answering system that leverages advanced language models and web scraping techniques to help users interact with information from multiple content sources—PDFs, web pages, and YouTube videos—using natural language queries.

# 🚀 Features
Multi-source Input Support:

-> PDF Documents: Upload any PDF, and the system extracts and processes its content. Ask questions and get answers based on the PDF using Ollama 3.

-> Web URLs: Input any webpage URL. The scraper uses Bright Data proxies to bypass CAPTCHAs and IP blocks, parses the webpage content using BeautifulSoup, and uses Ollama 3 to provide insightful answers.

-> YouTube Videos: Provide a YouTube video URL. The system fetches the transcript, processes the content, and uses Gemini 4.0 Flash to answer questions based on the video content.

Integrated with Generative AI Models:

-> Ollama 3 for document and webpage Q&A.

-> Gemini 4.0 Flash for video content analysis and summarization.

Seamless Parsing & Proxy Handling:

-> Robust handling of CAPTCHA and geo-restrictions via Bright Data proxy network.

-> Clean and efficient parsing of raw HTML content using BeautifulSoup.

# 🧰 Tech Stack
Python-based backend

Bright Data proxy integration

BeautifulSoup for HTML parsing

PDF parsing (PyMuPDF / PDFMiner / similar)

YouTube transcript extraction (YouTube Transcript API / custom fetcher)

Ollama 3 integration for NLP tasks

Gemini 4.0 Flash for video Q&A

# 🧠 Use Cases
Research assistants

Content summarization

Data-driven insights from unstructured content

Automated video/document analysis

# 📌 How It Works
Input your source: PDF file, webpage URL, or YouTube video URL.

Multiscrapper AI extracts and preprocesses the content.

Depending on the source type:

For PDFs/webpages: Ollama 3 processes and answers queries.

For videos: Gemini 4.0 Flash analyzes the transcript and responds.

Ask your questions and receive accurate, context-based answers.
