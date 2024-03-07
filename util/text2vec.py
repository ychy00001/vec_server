# -*- coding:utf-8 -*-
from typing import List

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from langchain.embeddings import HuggingFaceEmbeddings

from run_config import ENV_CONFIG

hg_embedding = HuggingFaceEmbeddings(model_name=ENV_CONFIG['HF_TEXT2VEC_MODEL_NAME'])


class Text2VecEmbeddingFunction(EmbeddingFunction):
    def __call__(self, texts: Documents) -> Embeddings:

        embeddings = hg_embedding.embed_documents(texts)

        return embeddings


def get_embeddings(documents: List[str]) -> List[List[float]]:
    embeddings = hg_embedding.embed_documents(documents)

    return embeddings
