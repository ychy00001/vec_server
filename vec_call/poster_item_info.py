from embed_type_enum import EmbedTypeEnum
import sys
import os
import json
from langchain.schema import Document
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.common import objDictTool

class PosterItemInfo(BaseModel):
    biz_name = ""
    keyword = ""
    template_id = ""
    is_ai = False
    is_segmentation = False

    def __init__(self, biz_name="", keyword="", template_id="", is_ai = False, is_segmentation = False):
        super().__init__(biz_name=biz_name, keyword=keyword, template_id=template_id, is_ai = is_ai, is_segmentation, is_segmentation)

    def keys(self):
        '''
        当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法
        '''
        return ('biz_name', 'keyword', 'template_id', 'is_ai', 'is_segmentation')

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
        return "%s" % (self.template_id)

    def get_meta_dict(self):
        dic_item = dict(self)
        return dic_item

    def to_document(self):
        '''
        转为LangChain Document对象
        Returns: langchain.schema.Document
        '''
        doc = Document()
        doc.page_content = self.template_id
        doc.metadata = self.get_meta_dict()
        return doc


if __name__ == '__main__':
    a = PosterItemInfo(biz_name="节日", keyword="春节、新年、喜庆", template_id="1")
    r = dict(a)
    print(r)
    c = PosterItemInfo()
    objDictTool.to_obj(c, **r)
    print(c.dim_value)
    print(c.get_meta_dict())
