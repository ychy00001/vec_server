# -*- coding:utf-8 -*-

import os
import sys
import json
from importlib import reload
from typing import Any, List, Mapping, Optional, Union, Dict
import util.chromadb_instance as chroma_instance
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vec_call.poster_item_info import PosterItemInfo

logger = logging.getLogger("uvicorn")


def add(item_list: List[PosterItemInfo]):
    insert_list = []
    meta_list = []
    id_list = []
    for item in item_list:
        insert_list.append(item.keyword)
        logger.info(f"add meta:{item.get_meta_dict()}")
        meta_list.append(item.get_meta_dict())
        id_list.append(item.get_id())
    # 根据原始数据填充变成向量库需要的数据
    logger.info(f"meta-list:{meta_list}")
    chroma_instance.cw_poster_db.add_texts(insert_list, meta_list, id_list)
    chroma_instance.cw_poster_db.persist()


def similarity_search(item_list: List[str], item_filter: Optional[Dict[str, object]] = None, n_results: int = 1):
    search_result = []
    db_size = chroma_instance.cw_poster_db._collection.count()
    fetch_k = db_size if db_size < 10 else 10
    logger.info(f"poster_db_size:{db_size}")
    n_results = n_results if n_results < db_size else db_size
    logger.info(f"poster_n_results: {n_results}", )
    metaList = []
    for key in item_filter:
        metaList.append({
            key: item_filter[key]
        })
    if len(metaList) > 1:
        whereMeta = {
            "$and": metaList
        }
    else:
        whereMeta = item_filter

    logger.info(f"where meta: {whereMeta}")
    for item in item_list:
        # item_result = chroma_instance.cw_poster_db.similarity_search(item, n_results, item_filter)
        item_result = chroma_instance.cw_poster_db.similarity_search_with_score(item, n_results, whereMeta)
        # item_result = chroma_instance.cw_poster_db.max_marginal_relevance_search(item, k=n_results, fetch_k=fetch_k,
                                                                                #  lambda_mult=0.9,
                                                                                #  filter=whereMeta)
        search_result.append({"origin_keyword": item, "search": item_result})

    return search_result


def update(update_item: PosterItemInfo):
    if origin_item and origin_item.get_id() > 0:
        chroma_instance.cw_poster_db.update_document(update_item.get_id(), update_item.to_document())
    else:
        raise Exception('id值异常，无法更改: update_id:{}'.format(update_item.get_id()))


def delete(del_item: PosterItemInfo):
    chroma_instance.cw_poster_db._collection.delete(del_item.get_id())


def clean():
    '''
    清空当前向量库，从数据库中删除了collection对象，重新添加数据会报异常，所以此处直接简单处理，重新new一个客户端出来
    TODO 其实可以重写langchain.chroma对象，补充可以重新创建一个collection的方法
    Returns:
    '''
    chroma_instance.cw_poster_db.delete_collection()
    chroma_instance.cw_poster_db = None
    chroma_instance.cw_poster_db = chroma_instance.reload_poster_db()


if __name__ == "__main__":
    test_list = []
    a1 = PosterItemInfo("节日", "新年、春节、喜庆", 1)
    a2 = PosterItemInfo("节日", "除夕、春节、蜡烛、春联", 2)
    a3 = PosterItemInfo("节日", "中国红、春节、灯笼、小年", 3)
    a4 = PosterItemInfo("节日", "福字、春节、毛笔、人物", 4)
    a5 = PosterItemInfo("节日", "生日、感恩、蛋糕", 5)
    a6 = PosterItemInfo("人文", "奋斗、自行车、飞跃", 6)
    test_list.append(a1)
    test_list.append(a2)
    test_list.append(a3)
    test_list.append(a4)
    test_list.append(a5)
    test_list.append(a6)
    add(test_list)
    print(json.dumps(test_list, default=lambda o: o.__dict__, ensure_ascii=False))
    result = similarity_search(["春节"], n_results=1)
    print(result)
    clean()
    add(test_list)
    print(a2.get_meta_dict())
    result = similarity_search(["节"], {'biz_name': '节日'}, n_results=1)
    print(result)
    clean()
