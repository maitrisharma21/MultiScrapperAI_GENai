import os
import re
import langcodes
import streamlit as st
import google.generativeai as genai
from streamlit_extras.add_vertical_space import add_vertical_space
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from bs4 import BeautifulSoup
import requests
from PyPDF2 import PdfReader
from warnings import filterwarnings
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)

from pdfminer.high_level import extract_text
from parse import parse_with_ollama

# ========== Common Setup ==========
filterwarnings("ignore")
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Streamlit UI Setup
st.set_page_config(page_title='Multi Scrapper AI')
add_vertical_space(1)
st.markdown("<h2 style='text-align: center;'>Multi Scrapper AI</h2>", unsafe_allow_html=True)
add_vertical_space(1)

# Sidebar Options
tool_choice = st.sidebar.radio("Choose a Tool", ["YouTube Video Summarizer", "PDF/Website Parser"])

def extract_languages(video_id):

    # Fetch the List of Available Transcripts for Given Video
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Extract the Language Codes from List ---> ['en','ta']
    available_transcripts = [i.language_code for i in transcript_list]

    # Convert Language_codes to Human-Readable Language_names ---> 'en' into 'English'
    language_list = list({langcodes.Language.get(i).display_name() for i in available_transcripts})

    # Create a Dictionary Mapping Language_names to Language_codes
    language_dict = {langcodes.Language.get(i).display_name():i for i in available_transcripts}

    return language_list, language_dict



def extract_transcript(video_id, language):
    
    try:
        # Request Transcript for YouTube Video using API
        transcript_content = YouTubeTranscriptApi.get_transcript(video_id=video_id, languages=[language])
    
        # Extract Transcript Content from JSON Response and Join to Single Response
        transcript = ' '.join([i['text'] for i in transcript_content])

        return transcript
    
    
    except Exception as e:
        add_vertical_space(5)
        st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)



def generate_summary(transcript_text):

    try:
        # Configures the genai Library
        genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

        # Initializes a Gemini-Pro Generative Model
        model = genai.GenerativeModel(model_name = 'gemini-2.0-flash')  

        # Define a Prompt for AI Model
        prompt = """You are a YouTube video summarizer. You will be taking the transcript text and summarizing the entire video, 
                    providing the important points are proper sub-heading in a concise manner (within 500 words). 
                    Please provide the summary of the text given here: """
        
        response = model.generate_content(prompt + transcript_text)

        return response.text

    except Exception as e:
        add_vertical_space(5)
        st.markdown(f'<h5 style="text-position:center;color:orange;">{e}</h5>', unsafe_allow_html=True)

def get_pdf_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    except Exception as e:
        st.warning(f"PDF Error: {e}")

def get_website_text(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all('p')
        return " ".join([para.get_text() for para in paragraphs])
    except Exception as e:
        st.warning(f"Website Error: {e}")

def summarize_content(content, question):
    try:
        model = genai.GenerativeModel(model_name='gemini-2.0-flash')
        prompt = f"Answer the following based on the text:\n\n{question}\n\nContent:\n{content}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.warning(f"Summarization Error: {e}")

if tool_choice == "YouTube Video Summarizer":
    st.subheader("🎥 YouTube Video Summarizer")
    video_link = st.text_input("Enter YouTube Video URL")

    if video_link:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", video_link)
        video_id = match.group(1) if match else None

        if video_id:
            try:
                language_list, language_dict = extract_languages(video_id)
                selected_lang = st.selectbox("Select Transcript Language", language_list)
                language_code = language_dict[selected_lang]

                if st.button("Summarize Video"):
                    st.image(f'http://img.youtube.com/vi/{video_id}/0.jpg', use_container_width=True)
                    with st.spinner("Extracting Transcript..."):
                        transcript = extract_transcript(video_id, language_code)
                    with st.spinner("Generating Summary..."):
                        summary = generate_summary(transcript)
                    if summary:
                        st.markdown("### Summary")
                        st.write(summary)
                        st.download_button("Download Summary", summary, file_name="youtube_summary.txt")
            except Exception as e:
                st.warning(f"Error: {e}")
        else:
            st.error("Invalid YouTube link format.")

elif tool_choice == "PDF/Website Parser":
    st.subheader("📄 PDF / Website Scraper + AI Parser")

    # Input Mode Selection
    parser_mode = st.radio("Choose Input Type", ["PDF File", "Website URL"])
    

    content = ""
    
    if parser_mode  == "Website URL":
        url = st.text_input("Enter Website URL")
        # Step 1: Scrape the Website
        if st.button("Scrape Website"):
                st.write("Scraping the website...")
                result = scrape_website(url)
                body_content = extract_body_content(result)
                cleaned_content = clean_body_content(body_content)

                # Store the DOM content in Streamlit session state
                st.session_state.dom_content = cleaned_content


                # Display the DOM content in an expandable text box
                with st.expander("View DOM Content"):
                        st.text_area("DOM Content", cleaned_content, height=300)

                print(result )
    elif parser_mode == "PDF File":
#query = st.text_area("Enter your query/question for the content")
        uploaded_file = st.file_uploader("Upload a PDF File", type="pdf")

        if uploaded_file is not None:
            st.write("Extracting text from PDF...")
            pdf_text = extract_text(uploaded_file)

            if pdf_text.strip():
                # Save to session
                st.session_state.dom_content = pdf_text

                with st.expander("View PDF Content"):
                    st.text_area("Extracted Text", pdf_text, height=300)
            else:
                st.warning("Could not extract text from this PDF.")

    # Step 2: Ask Questions About the DOM Content
    if "dom_content" in st.session_state:
        parse_description = st.text_area("Describe what you want to parse")

        if st.button("Parse Content"):
            if parse_description:
                st.write("Parsing the content...")

                # Parse the content with Ollama
                dom_chunks = split_dom_content(st.session_state.dom_content)
                parsed_result = parse_with_ollama(dom_chunks, parse_description)
                st.write(parsed_result)

