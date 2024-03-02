from transformers import AutoTokenizer

tokenizer=AutoTokenizer.from_pretrained("OrdalieTech/Solon-embeddings-large-0.1")

def tokenize(text):
    return tokenizer.encode(text)