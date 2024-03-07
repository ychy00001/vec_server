import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class objDictTool:
    @staticmethod
    def to_dic(obj):
        dic = {}
        for fieldkey in dir(obj):
            fieldvaule = getattr(obj, fieldkey)
            if not fieldkey.startswith("__") and not callable(fieldvaule) and not fieldkey.startswith("_"):
                dic[fieldkey] = fieldvaule
        return dic

    @staticmethod
    def to_obj(obj: object, **data):
        obj.__dict__.update(data)
