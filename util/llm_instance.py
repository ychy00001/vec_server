# -*- coding:utf-8 -*-
from langchain import llms

from provider.huggingface import HuggingFaceTextGenInference
from provider.httpllm import HttpGenInference
from langchain.llms import AzureOpenAI
from run_config import MODEL_NAME, OPENAI_API_KEY, TEMPERATURE,ENV_CONFIG
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config_parse import LLM_PROVIDER_NAME, llm_config_dict


def get_llm_provider(llm_provider_name: str, llm_config_dict: dict):
    if llm_provider_name in llms.type_to_cls_dict:
        llm_provider = llms.type_to_cls_dict[llm_provider_name]
        llm = llm_provider(**llm_config_dict)
        return llm
    else:
        raise Exception("llm_provider_name is not supported: {}".format(llm_provider_name))


# llm = get_llm_provider(LLM_PROVIDER_NAME, llm_config_dict)


# llm = OpenAI(openai_api_key=OPENAI_API_KEY, model_name=MODEL_NAME,
#              temperature=TEMPERATURE)

# llm = AzureOpenAI(
#         openai_api_key=ENV_CONFIG['OPENAI_API_KEY'],
#         openai_api_base=ENV_CONFIG['OPENAI_API_BASE'],
#         openai_api_type=ENV_CONFIG['OPENAI_API_TYPE'],
#         openai_api_version=ENV_CONFIG['OPENAI_API_VERSION'],
#         deployment_name=ENV_CONFIG['AZURE_DEPLOYMENT_NAME'],
#         temperature=ENV_CONFIG['OPENAI_API_TEMPERATURE'],
#         stop=json.loads(ENV_CONFIG['OPENAI_API_STOP'])
#     )


# llm = HuggingFaceTextGenInference(
#         inference_server_url="http://10.178.13.110:15501/chat",
#         max_new_tokens=600,
#         top_k=50,
#         top_p=0.95,
#         temperature=0.1,
#         do_sample=False,
# #         truncate=800,
#         repetition_penalty=1.03,
#         stop_sequences=["\n\nTable", "\n\n问题", "</s>", "User"]
#     )


llm = HttpGenInference(
        inference_server_url="http://10.178.13.110:15501/chat",
        max_new_tokens=600,
        top_k=50,
        top_p=0.95,
        temperature=0.1,
        do_sample=False,
#         truncate=800,
        repetition_penalty=1.03,
        stop_sequences=["</s>", "User"]
    )
