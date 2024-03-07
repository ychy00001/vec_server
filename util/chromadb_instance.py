# -*- coding:utf-8 -*-
from typing import Any, List, Mapping, Optional, Union

import chromadb
from chromadb.api import Collection
from chromadb.config import Settings
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma

from run_config import CHROMA_DB_PERSIST_PATH, ENV_CONFIG
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.logging_utils import logger

from config.config_parse import CHROMA_DB_PERSIST_PATH

client = chromadb.Client(
    Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=CHROMA_DB_PERSIST_PATH,  # Optional, defaults to .chromadb/ in the current directory
    )
)


def empty_chroma_collection_2(collection: Collection):
    collection_name = collection.name
    client = collection._client
    metadata = collection.metadata
    embedding_function = collection._embedding_function

    client.delete_collection(collection_name)

    new_collection = client.get_or_create_collection(name=collection_name,
                                                     metadata=metadata,
                                                     embedding_function=embedding_function)

    size_of_new_collection = new_collection.count()

    logger.info(f'Collection {collection_name} emptied. Size of new collection: {size_of_new_collection}')

    return new_collection


def empty_chroma_collection(collection:Collection) -> None:
    collection.delete()


def add_chroma_collection(collection:Collection,
                            queries:List[str],
                            query_ids:List[str],
                            metadatas:List[Mapping[str, str]]=None
                            ) -> None:

    collection.add(documents=queries,
                    ids=query_ids,
                    metadatas=metadatas)


def update_chroma_collection(collection:Collection,
                                queries:List[str],
                                query_ids:List[str],
                                metadatas:List[Mapping[str, str]]=None
                                ) -> None:

    collection.update(documents=queries,
                        ids=query_ids,
                        metadatas=metadatas)


def query_chroma_collection(collection:Collection, query_texts:List[str],
                            filter_condition:Mapping[str,str]=None, n_results:int=10):
    outer_opt = '$and'
    inner_opt = '$eq'

    if filter_condition is not None:
        if len(filter_condition)==1:
            outer_filter = filter_condition
        else:
            inner_filter = [{_k: {inner_opt:_v}} for _k, _v in filter_condition.items()]
            outer_filter = {outer_opt: inner_filter}
    else:
        outer_filter = None

    print('outer_filter: ', outer_filter)
    res = collection.query(query_texts=query_texts, n_results=n_results, where=outer_filter)
    return res


def parse_retrieval_chroma_collection_query(res:List[Mapping[str, Any]]):
    parsed_res = [[] for _ in range(0, len(res['ids']))]

    retrieval_ids = res['ids']
    retrieval_distances = res['distances']
    retrieval_sentences = res['documents']
    retrieval_metadatas = res['metadatas']

    for query_idx in range(0, len(retrieval_ids)):
        id_ls = retrieval_ids[query_idx]
        distance_ls = retrieval_distances[query_idx]
        sentence_ls = retrieval_sentences[query_idx]
        metadata_ls = retrieval_metadatas[query_idx]

        for idx in range(0, len(id_ls)):
            id = id_ls[idx]
            distance = distance_ls[idx]
            sentence = sentence_ls[idx]
            metadata = metadata_ls[idx]

            parsed_res[query_idx].append({
                'id': id,
                'distance': distance,
                'query': sentence,
                'metadata': metadata
            })

    return parsed_res

def chroma_collection_query_retrieval_format(query_list:List[str], retrieval_list:List[Mapping[str, Any]]):
    res = []
    for query_idx in range(0, len(query_list)):
        query = query_list[query_idx]
        retrieval = retrieval_list[query_idx]

        res.append({
            'query': query,
            'retrieval': retrieval
        })

    return res


def delete_chroma_collection_by_ids(collection:Collection, query_ids:List[str]) -> None:
    collection.delete(ids=query_ids)

def get_chroma_collection_by_ids(collection:Collection, query_ids:List[str]):
    res = collection.get(ids=query_ids)

    return res

def get_chroma_collection_size(collection:Collection) -> int:
    return collection.count()


##################cw_chroma配置，上面的代码为supersonic的对象##########################
def reload_vec_db():
    return Chroma(collection_name="cw_vec", persist_directory=CHROMA_DB_PERSIST_PATH + "_cw",
                    embedding_function=embedding_function)

def reload_func_db():
    return Chroma(collection_name="cw_func", persist_directory=CHROMA_DB_PERSIST_PATH + "_cw",
                    embedding_function=embedding_function)

def reload_dim_val_db():
    return Chroma(collection_name="cw_dim_val", persist_directory=CHROMA_DB_PERSIST_PATH + "_cw",
                    embedding_function=embedding_function)

def reload_poster_db():
    return Chroma(collection_name="cw_poster", persist_directory=CHROMA_DB_PERSIST_PATH + "_cw",
                    embedding_function=embedding_function)


embedding_function = SentenceTransformerEmbeddings(model_name=ENV_CONFIG['HF_TEXT2VEC_MODEL_NAME'])

# 维度指标数据库
cw_vec_db = reload_vec_db()
# 运算符数据库
cw_func_db = reload_func_db()
# 维度值数据库
cw_dim_val_db = reload_dim_val_db()
# 海报数据库
cw_poster_db = reload_poster_db()
# db.add_texts(['彩虹汽车', '性别', "年龄", "销售价格", "购买时间", "访问历史记录"],
#              [{"meta": "1_1"}, {"meta": "1_2_3"}, {"meta": "1_2_1"}, {"meta": "1_1_3"}, {"meta": "1_2_2"},
#               {"meta": "2_1_1"}])
