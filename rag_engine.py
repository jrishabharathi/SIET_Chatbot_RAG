import faiss
import numpy as np
from groq import Groq
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

#load pdfs
def load_pdf (pdf_path):
  reader = PdfReader(str(pdf_path))
  mypages = [ i.extract_text() or ""  for i in reader.pages]
  full_text = "\n".join(mypages).strip()
  if not full_text:
    raise ValueError("No readabel Text Found")
  return full_text
#chunking
def create_chunks(full_text, chunksize = 500, overlap = 100):
  chunks = []
  start = 0
  while start<len(full_text):
    end = start + chunksize
    chunk = full_text[start:end]
    if chunk.strip():
      chunks.append(chunk)
    start = end - overlap
  return chunks
#enbedding:
def build_vectors (chunks, model_name = "all-MiniLM-L6-v2"):
  if not chunks:
    raise ValueError("Cannot apply embedding without chunks")
  embed_model = SentenceTransformer(model_name)
  embed_vectors = embed_model.encode(chunks, convert_to_numpy = True )
  faiss.normalize_L2(embed_venctors)
  index = faiss.IndexFlatIP(embed_vectors.shape[1])
  index.add(embed_vectors)
  return index, embed_model
#call loadpdf, chunk, embedding
def load_base (pdf_path= "01_College_Information.pdf"):
  full_text = load_pdf(pdf_path)
  chunks = create_chunks(full_text)
  index, embed_model = build_vector(chunks)
  return index, embed_model, chunks

#retrive
def retrieve_content (question, embed_model, chunks, index, num_chunks=3)
  if not question.strip():
    raise ValueError("Question canniot be blank")
  if num_chunks < 1:
    raise ValueError("Request atleanst one or more chunks")
  query_embed = embed_model.encode([question], convert_to_numpy=True)
  faiss.normalize_L2(query_embed)
  sim_scores, vec_indices = index.search(query_embed, min(num_chunks, len(chunks)))
  background = ""
  for i in vec_indices[0]:
    if i != -1:
      background += chunks[i] + "\n\n"
  return background


#ask:
def ask_rag (question, embed_modul, chunks, index, api_key, num_chunks=3, model_name = "openai/gpt-oss-120b"):
  key = api_key
  if not key:
    raise ValueError("API key Missing")
  background = retrieve_content(question, embed_model, chunks, index, num_chunks=3):
  prompt = """ you are an professional ai assistant.
  answer userr question using only document backgrojfn below .
  do nint inbvet or assume facts.
  if information not AVIAPNBG GRC, Simply say "Information misssinfg 
  documengt backgroundn :""" + background + "user question " + question + "Answer:"
  client = Groq(api_key = key)
  response = client.chat.completions.create(
    model = model_name,
    messages = [ { "role" : "user",
                   "content" : prompt}],
                   temprature = 0.3,
  )
  return response.choices[0].message.content
