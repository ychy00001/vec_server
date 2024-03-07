# -*- coding:utf-8 -*-

import os
import sys
import json
from importlib import reload
from typing import Any, List, Mapping, Optional, Union, Dict
import logging
import util.chromadb_instance as chroma_instance

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vec_call.embed_type_enum import EmbedTypeEnum
from vec_call.vec_item_info import VecItemInfo


def add_metric(dim_list: List[VecItemInfo]):
    add(dim_list, EmbedTypeEnum.METRIC)


def add_dim(dim_list: List[VecItemInfo]):
    add(dim_list, EmbedTypeEnum.DIMENSION)


def add(item_list: List[VecItemInfo], item_type: EmbedTypeEnum = None):
    insert_list = []
    meta_list = []
    id_list = []
    for item in item_list:
        # 服务端传来的数据没有类型，所以需要填充类型信息
        if item_type is None:
            item.reload_item_type()
        else:
            item.item_type = item_type.name
        insert_list.append(item.text)
        meta_list.append(item.get_meta_dict())
        id_list.append(item.get_id())
    # 根据原始数据填充变成向量库需要的数据
    chroma_instance.cw_vec_db.add_texts(insert_list, meta_list, id_list)
    chroma_instance.cw_vec_db.persist()


def similarity_search_dim(dim_list: List[str], n_results: int = 1):
    similarity_search(dim_list, EmbedTypeEnum.DIMENSION, n_results)


def similarity_search_metric(metric_list: List[str], n_results: int = 1):
    similarity_search(metric_list, EmbedTypeEnum.METRIC, n_results)


def similarity_search(item_list: List[str], item_filter: Optional[Dict[str, str]] = None, n_results: int = 1):
    search_result = []
    db_size = chroma_instance.cw_vec_db._collection.count()
    fetch_k = db_size if db_size < 10 else 10
    n_results = n_results if n_results < db_size else db_size
    for item in item_list:
        # item_result = chroma_instance.cw_vec_db.similarity_search(item, n_results, item_filter)
        item_result = chroma_instance.cw_vec_db.max_marginal_relevance_search(item, k=n_results, fetch_k=fetch_k,
                                                                              lambda_mult=0.9,
                                                                              filter=item_filter)
        search_result.append({"origin_name": item, "search": item_result})

    return search_result


def update(origin_item: VecItemInfo, update_item: VecItemInfo):
    origin_item.reload_item_type()
    update_item.reload_item_type()
    if origin_item.get_id() != update_item.get_id():
        raise Exception('id值不同，无法更改: origin_id:{} update_id:{}'.format(origin_item.get_id(), update_item.get_id()))
    chroma_instance.cw_vec_db.update_document(origin_item.get_id(), update_item.to_document())


def delete(del_item: VecItemInfo):
    chroma_instance.cw_vec_db._collection.delete(del_item.get_id())


def clean():
    '''
    清空当前向量库，从数据库中删除了collection对象，重新添加数据会报异常，所以此处直接简单处理，重新new一个客户端出来
    TODO 其实可以重写langchain.chroma对象，补充可以重新创建一个collection的方法
    Returns:
    '''
    chroma_instance.cw_vec_db.delete_collection()
    chroma_instance.cw_vec_db = None
    chroma_instance.cw_vec_db = chroma_instance.reload_vec_db()


if __name__ == "__main__":
    text_list = ['彩虹汽车', '性别', "年龄", "销售价格", "购买时间", "访问历史记录"]
    test_list = []
    a1 = VecItemInfo("彩虹汽车", 1, 1, 1, 0, "rainbow_car")
    a2 = VecItemInfo("性别", 1, 1, 0, 1, "sex")
    a3 = VecItemInfo("年龄", 1, 1, 0, 2, "age")
    a4 = VecItemInfo("销售价格", 1, 1, 2, 0, "buy_price")
    a5 = VecItemInfo("购买时间", 1, 1, 0, 3, "buy_time")
    a6 = VecItemInfo("访问历史记录", 1, 1, 3, 0, "visit_history")
    test_list.append(a1)
    test_list.append(a2)
    test_list.append(a3)
    test_list.append(a4)
    test_list.append(a5)
    test_list.append(a6)
    add(test_list)
    print(json.dumps(test_list, default=lambda o: o.__dict__, ensure_ascii=False))
    result = similarity_search(["销售额", "性别"], n_results=1)
    print(result)
    clean()
    add(test_list)
    print(a2.get_meta_dict())
    result = similarity_search(["年龄"], {'item_type': 'DIMENSION'}, n_results=1)
    print(result)
    clean()
