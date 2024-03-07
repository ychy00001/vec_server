# -*- coding:utf-8 -*-

import os
import sys
import json
from importlib import reload
from typing import Any, List, Mapping, Optional, Union, Dict

import util.chromadb_instance as chroma_instance

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vec_call.func_item_info import FuncItemInfo

'''
操作符向量库用于存储mysql的相关函数的文字解析
'''


def add(item_list: List[FuncItemInfo]):
    insert_list = []
    meta_list = []
    id_list = []
    for item in item_list:
        # 服务端传来的数据没有类型，所以需要填充类型信息
        insert_list.append(item.text)
        meta_list.append(item.get_meta_dict())
        id_list.append(item.get_id())
    # 根据原始数据填充变成向量库需要的数据
    chroma_instance.cw_func_db.add_texts(insert_list, meta_list, id_list)
    chroma_instance.cw_func_db.persist()


def similarity_search(item_list: List[str], n_results: int = 1):
    search_result = []
    item_filter = None

    db_size = chroma_instance.cw_func_db._collection.count()
    fetch_k = db_size if db_size < 10 else 10
    n_results = n_results if n_results < db_size else db_size

    for item in item_list:
        # item_result = chroma_instance.cw_func_db.similarity_search(item, n_results, item_filter)
        item_result = chroma_instance.cw_func_db.max_marginal_relevance_search(item, k=n_results, fetch_k=fetch_k,
                                                                               lambda_mult=0.9, filter=item_filter)
        search_result.append({"origin_name": item, "search": item_result})

    return search_result


def update(origin_item: FuncItemInfo, update_item: FuncItemInfo):
    if origin_item.get_id() != update_item.get_id():
        raise Exception('id值不同，无法更改: origin_id:{} update_id:{}'.format(origin_item.get_id(), update_item.get_id()))
    chroma_instance.cw_func_db.update_document(origin_item.get_id(), update_item.to_document())


def delete(del_item: FuncItemInfo):
    chroma_instance.cw_func_db._collection.delete(del_item.get_id())


def clean():
    '''
    清空当前向量库，从数据库中删除了collection对象，重新添加数据会报异常，所以此处直接简单处理，重新new一个客户端出来
    TODO 其实可以重写langchain.chroma对象，补充可以重新创建一个collection的方法
    Returns:
    '''
    chroma_instance.cw_func_db.delete_collection()
    chroma_instance.cw_func_db = None
    chroma_instance.cw_func_db = chroma_instance.reload_func_db()


if __name__ == "__main__":
    test_list = []
    a1 = FuncItemInfo("求平均值", func_name="AVG", func_format="AVG(%s)", func_content="", arg_count=1)
    a2 = FuncItemInfo("求最大值", func_name="MAX", func_format="MAX(%s)", func_content="", arg_count=1)
    a3 = FuncItemInfo("求最小值", func_name="MIN", func_format="MIN(%s)", func_content="", arg_count=1)
    a4 = FuncItemInfo("求累加和", func_name="SUM", func_format="SUM(%s)", func_content="", arg_count=1)
    a5 = FuncItemInfo("求数量", func_name="COUNT", func_format="COUNT(%s)", func_content="", arg_count=1)
    test_list.append(a1)
    test_list.append(a2)
    test_list.append(a3)
    test_list.append(a4)
    test_list.append(a5)
    add(test_list)
    print(json.dumps(test_list, default=lambda o: o.__dict__, ensure_ascii=False))
    result = similarity_search(["最大", "求和"], n_results=1)
    print(result)
    clean()
    add(test_list)
    result = similarity_search(["计算数量"], n_results=1)
    print(result)
    clean()
