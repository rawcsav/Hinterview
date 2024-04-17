import os
import re
import warnings
from concurrent.futures import as_completed
from concurrent.futures import ThreadPoolExecutor
from typing import List, Any
import numpy as np
import openai
from openai import OpenAI, AsyncOpenAI
from pypdf import PdfReader
import tiktoken
from colorama import Fore, Style
from tqdm import tqdm
from config import configure_gpt_settings, get_config, get_file_type

configure_gpt_settings()

EMBEDDING_MODEL = "text-embedding-3-small"
GPT_MODEL = get_config('gpt_model')
TEMPERATURE = get_config('temperature')
TOP_P = get_config('top_p')
MAX_TOKENS = get_config('max_tokens')
SYSTEM_PROMPT = get_config('system_prompt')

MAX_LENGTH = 200
TOP_N = 3

tokenizer = tiktoken.get_encoding("cl100k_base")
warnings.filterwarnings('ignore')
client = OpenAI(api_key=get_config('openai_api_key'))

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def transcribe(audio_filepath) -> str:
    try:
        transcript = client.audio.transcriptions.create(
            file=open(audio_filepath, "rb"),
            model="whisper-1",
            prompt="This is an audio recording of a professional, personable, and fluid conversation.",
        )
        return transcript.text
    except openai.OpenAIError as api_err:
        print(Style.BRIGHT + Fore.RED + "API Error:", api_err)
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + "Error:", e)
    return ""


def remove_non_ascii(text: str) -> str:
    return ''.join(i for i in text if ord(i) < 128)

def transcribe_and_clean(mp3_filepath) -> str:
    transcription = transcribe(mp3_filepath)
    if transcription:
        cleaned_transcription = remove_non_ascii(transcription)
        return cleaned_transcription
    else:
        return "Transcription failed. Please try again."

def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def preprocess_text(text):
    text = re.sub(r'\n', ' ', text)

    text = re.sub(r'\s+', ' ', text)

    return text


def split_text(text, document_title, file_type):
    text = preprocess_text(text)

    tokens = tokenizer.encode(text)

    sections = []

    def decode_tokens(token_ids):
        return tokenizer.decode(token_ids).strip()

    processed_tokens = []
    current_section = {"title": f"{document_title} - {file_type.capitalize()}", "loc": "", "text": "", "tokens": 0}

    for token_id in tokens:
        processed_tokens.append(token_id)
        current_section["tokens"] += 1

        if len(processed_tokens) == 10:
            current_section["loc"] = decode_tokens(processed_tokens)

        if current_section["tokens"] >= MAX_LENGTH:
            current_section["text"] = decode_tokens(processed_tokens)
            sections.append(current_section)

            current_section = {"title": f"{document_title} - {file_type.capitalize()}", "loc": "", "text": "", "tokens": 0}
            processed_tokens = []

    if processed_tokens:
        current_section["text"] = decode_tokens(processed_tokens)
        sections.append(current_section)

    return sections


def get_embeddings(document: str):
    response = client.embeddings.create(
        input=document,  # Adjusted to take a single document
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def embed_corpus(corpus: List[str], num_workers=8):
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_doc = {executor.submit(get_embeddings, doc): doc for doc in corpus}

        embeddings = []
        # Initialize tqdm progress bar
        with tqdm(total=len(corpus), desc="Generating Embeddings") as pbar:
            for future in as_completed(future_to_doc):
                embeddings.append(
                    future.result())  # Collect embeddings as they are completed
                pbar.update(1)  # Update progress bar per completed task

    return embeddings



def embed_documents(folder_path):
    try:
        sections = []
        for filename in os.listdir(folder_path):
            file_type = get_file_type(filename)
            if file_type != "none" and (filename.endswith(".txt") or filename.endswith(".pdf")):
                if filename.endswith(".txt"):
                    with open(os.path.join(folder_path, filename), 'r') as f:
                        original = f.read()
                elif filename.endswith(".pdf"):
                    file_path = os.path.join(folder_path, filename)
                    original = extract_text_from_pdf(file_path)
                original_title = os.path.splitext(filename)[0]
                sections.extend(split_text(original, original_title, file_type))

        titles = [section['title'] for section in sections]
        locs = [section['loc'] for section in sections]
        texts = [section['text'] for section in sections]
        embeddings = embed_corpus(texts)

        return titles, locs, texts, embeddings
    except PermissionError:
        print(Fore.RED + "Permission denied. Please check the folder path and ensure you have read access.")
        return [], [], [], []
    except Exception as e:
        print(Fore.RED + f"An error occurred: {str(e)}")
        return [], [], [], []
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def strings_ranked_by_relatedness(query: str, titles, locs, embeddings, relatedness_fn=cosine_similarity, top_n: int = TOP_N):
    query_embedding_response = client.embeddings.create(
        input=query,
        model=EMBEDDING_MODEL
    )
    query_embedding = np.array(query_embedding_response.data[0].embedding)

    relatedness_scores = np.array([relatedness_fn(query_embedding, embedding) for embedding in embeddings])
    top_indices = np.argsort(relatedness_scores)[::-1][:top_n]

    return [(titles[i], locs[i]) for i in top_indices]

def query_message(query: str, titles, locs, texts, embeddings) -> tuple[str, str, list[tuple[Any, Any]]]:
    introduction = ('Use the textual excerpts to provide detailed, bullet point answers for the subsequent question. '
                    'If the answer cannot be found in the provided text, do your best to provide the most rational and  '
                    'comprehensive response. The response should be able to be seamlessly used to quickly answer the question.'
                    'Be as succinct as possible.')
    question = query

    message = introduction
    full_message = introduction

    docs_used = []

    relevant_sections = strings_ranked_by_relatedness(query, titles, locs, embeddings)
    docs_used.extend(relevant_sections[:5])

    for title, loc in docs_used:
        doc_info = f'\n\nTitle: {title}'
        section_text = texts[locs.index(loc)]
        next_article = doc_info + f'\nTextual excerpt section:\n"""\n{section_text}\n"""'
        message += doc_info
        full_message += next_article

    full_message += question
    return message, full_message, docs_used

async def ask(transcription, titles, locs, texts, embeddings, interruption_event) -> str:
    async_client = AsyncOpenAI(
        api_key=get_config('openai_api_key'),
    )
    if interruption_event.is_set():
        return

    print(Fore.CYAN + "\n──────────────────────────────────────────────────────────────────────────")
    print(Style.BRIGHT + Fore.BLUE + "Question:" + "\n" + Style.NORMAL + Fore.RESET + f"{transcription}")
    print(Style.BRIGHT + Fore.MAGENTA + "\n" + "AI Response:")
    max_tokens = MAX_TOKENS
    temperature = TEMPERATURE
    top_p = TOP_P
    model = GPT_MODEL
    message, full_message, docs_used = query_message(transcription, titles, locs, texts,
                                                     embeddings)
    max_tokens = max_tokens - num_tokens(transcription + full_message, model=model)
    messages = [
        {"role": "system",
         "content": SYSTEM_PROMPT},
        {"role": "user", "content": full_message},
    ]

    response_content = ""
    response = await async_client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stream=True
    )

    try:
        async for chunk in response:
            if interruption_event.is_set():
                return
            content = chunk.choices[0].delta.content
            if content is not None:
                print(content, end='')
                response_content += content

    except RuntimeError as e:
        if 'asynchronous generator is already running' in str(e):
            print("Generator was interrupted.")
        else:
            raise

    print(Fore.CYAN + "\n──────────────────────────────────────────────────────────────────────────")
    print(Fore.LIGHTGREEN_EX + "\nPress and hold the hotkey again to record another segment.")