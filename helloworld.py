from langchain.prompts import PromptTemplate
from models.custom_llm import CustomLLM

llm = CustomLLM()

prompt = PromptTemplate(
    input_variables=["product"],
    template="请给一个制造{product}的公司起一个好听的名字",
)

from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
print(chain.run("彩虹色的袜子"))
