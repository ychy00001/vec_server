# -*- coding:utf-8 -*-
import os
import logging
import sys

import uvicorn

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Any, List, Mapping, Optional, Union, Dict
from typing_extensions import Annotated

from fastapi import FastAPI, HTTPException, Body

from config.config_parse import LLMPARSER_HOST, LLMPARSER_PORT

from services_router import (query2sql_service, preset_query_service,
                            solved_query_service, plugin_call_service)

from vec_call.run import similarity_search as _vec_similarity_search, add as _vec_add, clean as _vec_clean
from vec_call.run_dim_val import similarity_search as _dim_val_similarity_search, add as _dim_val_add, \
    clean as _dim_val_clean
from vec_call.run_func import similarity_search as _func_similarity_search, add as _func_add, clean as _func_clean
from vec_call.run_poster import similarity_search as _poster_similarity_search, add as _poster_add, clean as _poster_clean, update as _poster_update, delete as _poster_delete
from vec_call.vec_item_info import VecItemInfo
from vec_call.dim_val_item_info import DimValItemInfo
from vec_call.func_item_info import FuncItemInfo
from vec_call.poster_item_info import PosterItemInfo
from util.api_response import return_msg, ret_error, ret_success


app = FastAPI()
logger = logging.getLogger("uvicorn")

@app.get("/health")
def read_health():
    return {"status": "Healthy"}

app.include_router(preset_query_service.router)
app.include_router(solved_query_service.router)
app.include_router(query2sql_service.router)
app.include_router(plugin_call_service.router)


@app.post("/vec_similarity_search")
async def vec_similarity_search(query_text_list: List[str], query_filter: Optional[Dict[str, str]] = None,
                                n_results: int = 1):
    '''
    Args:
        query_text_list: ['销售额', "年龄"]
        query_filter: {"item_type": "METRIC"}
        n_results: 1

    Returns:
        [
          {
            'key': '销售额',
            'search': [
               Document(page_content='销售价格', metadata={'item_type': 'DIMENSION', 'domain_id': 1, 'model_id': 1, 'metric_id': 2, 'dimension_id': 0})
            ]
          },
          {
            'key': '性别',
            'search': [
              Document(page_content='性别', metadata={'item_type': 'DIMENSION', 'domain_id': 1, 'model_id': 1, 'metric_id': 0, 'dimension_id': 1})
            ]
          }
        ]

    '''
    from chromadb.errors import NoIndexException
    try:
        parsed_retrieval_res_format = _vec_similarity_search(query_text_list, query_filter, n_results)
    except NoIndexException:
        return ret_error(message="索引未找到，数据库可能已被删除")
    return ret_success(parsed_retrieval_res_format)


@app.post("/vec_insert")
async def vec_insert(insert_list: List[VecItemInfo]):
    '''
    插入数据
    Args:
        [
          {'text': '销售额', 'item_type': 'DIMENSION', 'domain_id': 0, 'model_id': 0, 'metric_id': 0, 'dimension_id': 1}
        ]

    Returns: "success"
    '''
    _vec_add(insert_list)
    return ret_success()


@app.post("/vec_clean")
async def vec_clean():
    '''
    清空cw向量库
    Returns:

    '''
    _vec_clean()
    return ret_success()


@app.post("/dim_val_similarity_search")
async def dim_val_similarity_search(query_text_list: List[str], query_filter: Optional[Dict[str, str]] = None, n_results: int = 1):
    '''
    Args:
        query_text_list: ['SUV车辆', "越野"]
        query_filter: { "dim_column" : "type"}
        n_results: 1

    Returns:
        [
          {
            'key': 'SUV车辆',
            'search': [
               Document(page_content='SUV车辆', metadata={'dim_column': 'type', 'dim_value': 'SUV', 'model_id': 3, 'data_source_id': 5})
            ]
          },
          {
            'key': '越野车',
            'search': [
              Document(page_content='越野车', metadata={'dim_column': 'type', 'dim_value': '越野车', 'model_id': 3, 'data_source_id': 5})
            ]
          }
        ]

    '''
    from chromadb.errors import NoIndexException
    try:
        parsed_retrieval_res_format = _dim_val_similarity_search(query_text_list, query_filter, n_results)
    except NoIndexException:
        return ret_error(message="索引未找到，数据库可能已被删除")
    return ret_success(parsed_retrieval_res_format)


@app.post("/dim_val_insert")
async def dim_val_insert(insert_list: List[DimValItemInfo]):
    '''
    插入数据
    Args:
        [
          {
            "text": "SUV车辆",
            "dim_column": "type",
            "dim_value": "SUV",
            "model_id": 3,
            "data_source_id" 5
          }
        ]
    Returns: "success"
    '''
    _dim_val_add(insert_list)
    return ret_success()


@app.post("/dim_val_clean")
async def dim_val_clean():
    '''
    清空dim_val向量库
    Returns:

    '''
    _dim_val_clean()
    return ret_success()


@app.post("/func_similarity_search")
async def dim_val_similarity_search(query_text_list: List[str], n_results: int = 1):
    '''
    Args:
        query_text_list: ['总数', "最大值"]
        n_results: 1

    Returns:
        [
          {
            'key': '数量',
            'search': [
               Document(page_content='求数量', metadata={'func_name': 'COUNT', 'func_format': 'COUNT(%s)', 'func_content': '', 'arg_count': 1})
            ]
          },
          {
            'key': '最大值',
            'search': [
              Document(page_content='求最大值', metadata={'func_name': 'MAX', 'func_format': 'MAX(%s)', 'func_content': '', 'arg_count': 1})
            ]
          }
        ]

    '''
    from chromadb.errors import NoIndexException
    try:
        parsed_retrieval_res_format = _func_similarity_search(query_text_list, n_results)
    except NoIndexException:
        return ret_error(message="索引未找到，数据库可能已被删除")
    return ret_success(parsed_retrieval_res_format)


@app.post("/func_insert")
async def dim_val_insert(insert_list: List[FuncItemInfo]):
    '''
    插入数据
    Args:
        [
              {
                "text": "求平均值",
                "func_name": "AVG",
                "func_format": "AVG(%s)",
                "arg_count": 1,
                "func_content": ""
              }
        ]

    Returns: "success"
    '''
    _func_add(insert_list)
    return ret_success()


@app.post("/func_clean")
async def dim_val_clean():
    '''
    清空cw向量库
    Returns:

    '''
    _func_clean()
    return ret_success()

@app.post("/poster_similarity_search")
async def poster_similarity_search(query_text_list: List[str], n_results: Annotated[int, Body()], query_filter: Optional[Dict[str, str]] = None):
    logger.info(f"poster_similarity_search, n_result: {n_results}")
    '''
    Args:
        query_text_list: ['小年', "生日"]
        query_filter: {"biz_name": "节日"}
        n_results: 1

    Returns:
        [
          {
            'key': '小年',
            'search': [
               Document(page_content='1', metadata={'biz_name': '节日', 'keyword': '小年...', 'template_id': 1})
            ]
          },
          {
            'key': '生日',
            'search': [
              Document(page_content='2', metadata={'biz_name': '节日', 'keyword': '春节...', 'template_id': 2})
            ]
          }
        ]

    '''
    from chromadb.errors import NoIndexException
    try:
        logger.info(f"poster_similarity_search, n_result: {n_results}")
        if n_results == None:
            n_results = 1
        parsed_retrieval_res_format = _poster_similarity_search(query_text_list, query_filter, n_results)
    except NoIndexException:
        return ret_error(message="索引未找到，数据库可能已被删除")
    return ret_success(parsed_retrieval_res_format)


@app.post("/poster_insert")
async def poster_insert(insert_list: List[PosterItemInfo]):
    '''
    插入数据
    Args:
        [
          {'biz_name': '节日', 'keyword': '新年', 'template_id': 1}
        ]
    Returns: "success"
    '''
    _poster_add(insert_list)
    return ret_success()


@app.post("/poster_clean")
async def poster_clean():
    '''
    清空poster向量库
    Returns:

    '''
    _poster_clean()
    return ret_success()

@app.post("/poster_update")
async def poster_insert(posterItem: PosterItemInfo):
    '''
    更新向量库条目
    Args:
        {
          'biz_name': '节日', 
          'keyword': '新年', 
          'template_id': 1,
          'is_ai': true,
          'is_segmentation': false,
        }
    Returns: "success"
    '''
    _poster_update(posterItem)
    return ret_success()


@app.post("/poster_delete")
async def poster_clean(posterItem: PosterItemInfo):
    '''
    删除poster向量库条目
    Returns:
    '''
    _poster_delete(posterItem)
    return ret_success()

if __name__ == "__main__":
    uvicorn.run(app, host=LLMPARSER_HOST, port=LLMPARSER_PORT)
