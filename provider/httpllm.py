from typing import Any, Dict, List, Optional
from pydantic import Extra, Field, root_validator
import requests
import warnings
from abc import ABC
import json


class HttpGenInference(ABC):
    max_new_tokens: int = 512
    top_k: Optional[int] = 50
    top_p: Optional[float] = 0.95
    typical_p: Optional[float] = 0.95
    do_sample: Optional[bool] = False
    truncate: Optional[int] = 800
    temperature: float = 0.1
    repetition_penalty: Optional[float] = 1.03
    stop_sequences: List[str] = Field(default_factory=list)
    seed: Optional[int] = None
    inference_server_url: str = ""
    timeout: int = 120
    client: Any
    is_stream: bool = False

    def __init__(self, inference_server_url="http://10.178.13.110:15501/chat",
                 max_new_tokens=600,
                 top_k=50,
                 top_p=0.95,
                 temperature=0.1,
                 do_sample=False,
                 repetition_penalty=1.03,
                 stop_sequences=["</s>", "User"]):
        self.inference_server_url = inference_server_url
        self.max_new_tokens = max_new_tokens
        self.top_k = top_k
        self.top_p = top_p
        self.temperature = temperature
        self.do_sample = do_sample
        self.repetition_penalty = repetition_penalty
        self.stop_sequences = stop_sequences

    def __call__(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> str:
        data = {
            "allowTruncation": False,
            "messages": [
                {
                    "role": "system",
                    "content": ""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "parameters": {
                "do_sample": self.do_sample,
                "max_new_tokens": self.max_new_tokens,
                "repetition_penalty": self.repetition_penalty,
                "stop": self.stop_sequences,
                "temperature": self.temperature,
                "top_k": self.top_k,
                "top_p": self.top_p
            },
            "assistantPrefix": "",
            "userPrefix": ""
        }
        # 设置请求头部
        headers = {'Content-Type': 'application/json'}
        print("request data:", data)
        response = requests.post(self.inference_server_url, json=data, headers=headers)

        if response.status_code == 200:
            json_response = response.json()
            return json_response.get('generated_text')
        else:
            print("请求失败:", response.content)
        return ""
