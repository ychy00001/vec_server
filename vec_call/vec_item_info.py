from embed_type_enum import EmbedTypeEnum
import sys
import os
import json
from langchain.schema import Document
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from util.common import objDictTool


class VecItemInfo(BaseModel):
    domain_id = 0
    model_id = 0
    metric_id = 0
    dimension_id = 0
    item_type = ""
    text = ""
    biz_name = ""
    db_type = "varchar"

    def __init__(self, text="", domain_id=0, model_id=0, metric_id=0, dimension_id=0,
                 biz_name="", db_type="", item_type=None):
        if dimension_id > 0:
            item_type = EmbedTypeEnum.DIMENSION.name
        elif metric_id > 0:
            item_type = EmbedTypeEnum.METRIC.name
        else:
            item_type = EmbedTypeEnum.UNKNOWN.name
        super().__init__(text=text, domain_id=domain_id, model_id=model_id, metric_id=metric_id,
                         dimension_id=dimension_id, item_type=item_type, biz_name=biz_name, db_type=db_type)

    def keys(self):
        '''
        当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法
        '''
        return ('text', 'item_type', 'domain_id', "model_id", "metric_id", "dimension_id", "biz_name", "db_type")

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

    def reload_item_type(self):
        if self.dimension_id > 0:
            self.item_type = EmbedTypeEnum.DIMENSION.name
        elif self.metric_id > 0:
            self.item_type = EmbedTypeEnum.METRIC.name
        else:
            self.item_type = EmbedTypeEnum.UNKNOWN.name

    def get_id(self):
        return "%s_%s_%s_%s_%s" % (self.domain_id, self.model_id, self.metric_id, self.dimension_id, self.text)

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

    print("%s_%s" % ("aaa","bbb"))
    # a = VecItemInfo("销售额", dimension_id=1)
    # r = dict(a)
    # print(r)
    # c = VecItemInfo()
    # objDictTool.to_obj(c, **r)
    # print(c.item_type)
    # print(c.get_meta_dict())
