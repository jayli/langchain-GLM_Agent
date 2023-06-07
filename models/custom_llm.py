from typing import Any, List, Dict, Mapping, Optional
import json

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.requests import TextRequestsWrapper
from langchain.llms.base import LLM

# llm = CustomLLM()
# print(llm("who are you?"))
class CustomLLM(LLM):

    logging: bool = False
    output_keys: List[str] = ["output"]

    llm_type: str = "chatglm"

    @property
    def _llm_type(self) -> str:
        return self.llm_type

    def log(self, log_str):
        if self.logging:
            print(log_str)
        else:
            return

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        self.log('----------' + self._llm_type + '----------> llm._call()')
        self.log(prompt)
        requests = TextRequestsWrapper()

        response = requests.post(f"http://js-perf.cn:7001/test/{self._llm_type}", {
            "ask": prompt
        })
        if self._llm_type == "chatglm":
            # 我部署的 chatglm
            self.log('<--------chatglm------------')
            self.log(response)
            return response
        else:
            return "不支持该类型的 llm"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"n": 10}

