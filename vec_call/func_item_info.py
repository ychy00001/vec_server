from embed_type_enum import EmbedTypeEnum
import sys
import os
import json
from langchain.schema import Document
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.common import objDictTool


class FuncItemInfo(BaseModel):
    text = ""
    func_name = ""
    func_format = ""
    func_content = ""
    arg_count = 1



    def __init__(self, text="", func_name="", func_format="", func_content="", arg_count=1):
        super().__init__(text=text, func_name=func_name, func_format=func_format, func_content=func_content,
                         arg_count=arg_count)

    def keys(self):
        '''
        当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法
        '''
        return ('text', 'func_name', 'func_format', "func_content", "arg_count")

    def __getitem__(self, item):
        '''
        内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值
        '''
        return getattr(self, item)

    def toJSON(self):
        '''
        供json.dumps使用
        Returns:

        '''
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def get_id(self):
        return "%s_%s" % (self.func_name, self.text)

    def get_meta_dict(self):
        dic_item = dict(self)
        del dic_item['text']
        return dic_item

    def to_document(self):
        '''
        转为LangChain Document对象
        Returns: langchain.schema.Document
        '''
        doc = Document()
        doc.page_content = self.text
        doc.metadata = self.get_meta_dict()
        return doc


if __name__ == '__main__':
    a = FuncItemInfo("求平均值", func_name="AVG", func_format="AVG(%s)", func_content="", arg_count=1)
    r = dict(a)
    print(r)
    c = FuncItemInfo()
    objDictTool.to_obj(c, **r)
    print(c.func_name)
    print(c.get_meta_dict())
