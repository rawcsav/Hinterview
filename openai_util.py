import concurrent.futures
import os
import re
import time
import warnings
from typing import Dict, Tuple, List

import openai
import pandas as pd
import tiktoken
from colorama import Fore, Style
from scipy import spatial
from tqdm import tqdm

from config import get_config

EMBEDDING_MODEL = "text-embedding-ada-002"
GPT_MODEL = "gpt-4"
MAX_LENGTH = 300
TOP_N = 3

tokenizer = tiktoken.get_encoding("cl100k_base")
warnings.filterwarnings('ignore')


def num_tokens(text: str, model: str = GPT_MODEL) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def preprocess_text(text):
    text = re.sub(r'\n', ' ', text)

    text = re.sub(r'\s+', ' ', text)

    return text


def split_text(text, document_title):
    text = preprocess_text(text)

    tokens = tokenizer.encode(text)

    sections = []

    def decode_tokens(token_ids):
        return tokenizer.decode(token_ids).strip()

    processed_tokens = []
    current_section = {"title": document_title, "loc": "", "text": "", "tokens": 0}

    for token_id in tokens:
        processed_tokens.append(token_id)
        current_section["tokens"] += 1

        if len(processed_tokens) == 10:
            current_section["loc"] = decode_tokens(processed_tokens)

        if current_section["tokens"] >= MAX_LENGTH:
            current_section["text"] = decode_tokens(processed_tokens)
            sections.append(current_section)

            current_section = {"title": document_title, "loc": "", "text": "", "tokens": 0}
            processed_tokens = []

    if processed_tokens:
        current_section["text"] = decode_tokens(processed_tokens)
        sections.append(current_section)

    return sections


def get_embedding(text: str, model: str = EMBEDDING_MODEL, retry_limit=3, retry_delay=5) -> list[float]:
    for i in range(retry_limit):
        try:
            time.sleep(0.1)  # Wait for a tiny interval of time between each call
            result = openai.Embedding.create(
                model=model,
                input=text
            )
            return result["data"][0]["embedding"]
        except openai.error.RateLimitError:
            time.sleep(5)
        except openai.error.OpenAIError as e:
            print(f"Error: {e}")
            return None
        print(f"Retrying... (attempt {i + 1})")
        time.sleep(retry_delay)
    return None


def compute_doc_embeddings(df: pd.DataFrame, batch_size=3, num_workers=6) -> Dict[Tuple[str, str], List[float]]:
    embeddings = {}

    def process_batch(batches: pd.DataFrame) -> Dict[Tuple[str, str], List[float]]:
        batch_embeddings = {}
        texts = [r.text for idx, r in batches.iterrows()]
        for j, text in enumerate(texts):
            embedding = get_embedding(text)
            if embedding is None:
                print("Failed to compute embedding for document with index:", batches.index[j])
            else:
                batch_embeddings[batches.index[j]] = embedding
        return batch_embeddings

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            futures.append(executor.submit(process_batch, batch))

        # Add desc parameter to tqdm to display custom text
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc='Creating Document '
                                                                                              'Embeddings'):
            embeddings.update(future.result())

    return embeddings


def embed_documents(folder_path):
    dfs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), 'r') as f:
                original = f.read()
                original_title = os.path.splitext(filename)[0]
                sections = split_text(original, original_title)
                df = pd.DataFrame(sections)
                dfs.append(df)

    # Concatenate all dataframes in dfs
    combined_df = pd.concat(dfs, ignore_index=True)

    # Compute embeddings for the combined dataframe
    combined_df['embeddings'] = compute_doc_embeddings(combined_df)

    return combined_df


def strings_ranked_by_relatedness(query: str, df: pd.DataFrame,
                                  relatedness_fn=lambda x, y: 1 - spatial.distance.cosine(x, y),
                                  top_n: int = TOP_N) -> pd.DataFrame:
    query_embedding_response = openai.Embedding.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    query_embedding = query_embedding_response["data"][0]["embedding"]

    df['relatedness'] = df['embeddings'].apply(lambda x: relatedness_fn(query_embedding, x))
    sorted_df = df.sort_values(by='relatedness', ascending=False).head(top_n)
    return sorted_df


def query_message(query: str, df: pd.DataFrame) -> str:
    resume_title = get_config('resume_title')
    job_desc_title = get_config('job_desc_title')

    introduction = ('Use the below textual excerpts to answer the subsequent interview question. If the answer cannot '
                    'be found in the provided text, do your best to provide the most rational and comprehensive '
                    'answer. Answer as if you are the interviewee.')
    question = query

    message = introduction
    full_message = introduction

    docs_used = []

    if get_config("special_option"):
        # Get the most relevant section from the resume
        resume_section = strings_ranked_by_relatedness(query, df[df['title'] == resume_title]).iloc[0]
        docs_used.append((resume_section["title"], resume_section["loc"]))

        # Get the most relevant section from the job description
        job_desc_section = strings_ranked_by_relatedness(query, df[df['title'] == job_desc_title]).iloc[0]
        docs_used.append((job_desc_section["title"], job_desc_section["loc"]))

        # For the third section, sort the dataframe by relevance excluding already used docs and pick the top section
        third_section_df = df[~df['loc'].isin([resume_section["loc"], job_desc_section["loc"]])]
        third_section = strings_ranked_by_relatedness(query, third_section_df).iloc[0]
        docs_used.append((third_section["title"], third_section["loc"]))
    else:
        # If the special option isn't enabled, just pick the top 3 most relevant sections
        docs_used.extend(
            [(row["title"], row["loc"]) for _, row in strings_ranked_by_relatedness(query, df).head(3).iterrows()])

    for title, loc in docs_used:
        doc_info = f'\n\nTitle: {title}'
        section_text = df[(df['title'] == title) & (df['loc'] == loc)]['text'].iloc[0]
        next_article = doc_info + f'\nTextual excerpt section:\n"""\n{section_text}\n"""'
        message += doc_info
        full_message += next_article

    full_message += question
    return message, full_message, docs_used


async def ask(transcription, df, model: str = GPT_MODEL) -> str:
    print(Fore.CYAN + "\n──────────────────────────────────────────────────────────────────────────")
    print(Style.BRIGHT + Fore.BLUE + "Question:" + "\n" + Style.NORMAL + Fore.RESET + f"{transcription}")
    print(Style.BRIGHT + Fore.MAGENTA + "\n" + "AI Response:")
    max_tokens = 1500
    max_tokens - num_tokens(transcription, model=model)

    message, full_message, docs_used = query_message(transcription, df)

    max_tokens = max_tokens - num_tokens(transcription + full_message, model=model)
    messages = [
        {"role": "system",
         "content": "You are a knowledgeable job interview assistant that uses information from provided textual "
                    "excerpts to answer interview questions."},
        {"role": "user", "content": full_message},
    ]
    response_content = ""
    async for chunk in await openai.ChatCompletion.acreate(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=.7,
            stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content", "")
        if content is not None:
            print(content, end='')
        response_content += content

    print(Fore.CYAN + "\n──────────────────────────────────────────────────────────────────────────")
    print(Fore.LIGHTGREEN_EX + "\nPress and hold the Option key again to record another segment of your interview.")
