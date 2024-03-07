from fastapi import status
from fastapi.responses import JSONResponse, Response
from typing import Union
import json


def return_msg(*, code=200, data: Union[list, dict, str], message="Success") -> Response:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': code,
            'message': message,
            'data': json.loads(json.dumps(data, ensure_ascii=False, default=lambda o: o.__dict__)),
        }
    )


def ret_success(data: Union[list, dict, str] = None) -> Response:
    return return_msg(data=data)


def ret_error(*, code=400, data: Union[list, dict, str] = None, message="Error") -> Response:
    return return_msg(code=code, data=data, message=message)
