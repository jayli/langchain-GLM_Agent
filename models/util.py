from typing import Any, List, Dict, Mapping, Optional
import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from models.chinese_text_splitter import ChineseTextSplitter
from langchain.vectorstores import FAISS
from models.custom_llm import CustomLLM
import datetime
import torch
from tqdm import tqdm
from models.config import *
from langchain import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain

conversation_template = """你是一个正在跟某个人类对话的机器人.

{chat_history}
人类: {human_input}
机器人:"""

def load_txt_file(filepath):
    loader = TextLoader(filepath, encoding="utf8")
    textsplitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE,
                                         chunk_overlap=CHUNK_OVERLAP,
                                         length_function=len)
    docs = loader.load_and_split(text_splitter=textsplitter)
    return docs

def torch_gc():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    elif torch.backends.mps.is_available():
        try:
            from torch.mps import empty_cache
            empty_cache()
        except Exception as e:
            print(e)
            print("如果您使用的是 macOS 建议将 pytorch 版本升级至 2.0.0 或更高版本，以支持及时清理 torch 产生的内存占用。")

def load_file(filepath):
    if filepath.lower().endswith(".md"):
        loader = UnstructuredFileLoader(filepath, mode="elements")
        docs = loader.load()
    elif filepath.lower().endswith(".pdf"):
        loader = UnstructuredFileLoader(filepath)
        textsplitter = ChineseTextSplitter(pdf=True)
        docs = loader.load_and_split(textsplitter)
    else:
        docs = load_txt_file(filepath)
    return docs

def get_related_content(related_docs):
    related_content = []
    for doc in related_docs:
        related_content.append(doc.page_content)
    return "\n".join(related_content)

def get_docs_with_score(docs_with_score):
    docs = []
    for doc, score in docs_with_score:
        doc.metadata["score"] = score
        docs.append(doc)
    return docs

# filepath 可以是目录，也可以是文件
def init_knowledge_vector_store(filepath: str or List[str],
                                vs_path: str or os.PathLike = None,
                                embeddings: object = None):
    loaded_files = []
    failed_files = []
    # 单个文件
    if isinstance(filepath, str):
        if not os.path.exists(filepath):
            print(f"{filepath} 路径不存在")
            return None
        elif os.path.isfile(filepath):
            file = os.path.split(filepath)[-1]
            try:
                docs = load_file(filepath)
                print(f"{file} 已成功加载")
                loaded_files.append(filepath)
            except Exception as e:
                print(e)
                print(f"{file} 未能成功加载")
                return None
        elif os.path.isdir(filepath):
            docs = []
            for file in tqdm(os.listdir(filepath), desc="加载文件"):
                fullfilepath = os.path.join(filepath, file)

                try:
                    docs += load_file(fullfilepath)
                    loaded_files.append(fullfilepath)
                except Exception as e:
                    failed_files.append(file)

            if len(failed_files) > 0:
                print("以下文件未能成功加载：")
                for file in failed_files:
                    print(file,end="\n")
    #  文件列表
    else:
        docs = []
        for file in filepath:
            try:
                docs += load_file(file)
                print(f"{file} 已成功加载")
                loaded_files.append(file)
            except Exception as e:
                print(e)
                print(f"{file} 未能成功加载")

    if len(docs) > 0:
        print("文件加载完毕，正在生成向量库")
        if vs_path and os.path.isdir(vs_path):
            vector_store = FAISS.load_local(vs_path, embeddings)
            vector_store.add_documents(docs)
            torch_gc()
        else:
            if not vs_path:
                vs_path = os.path.join(vs_path,
                                       f"""FAISS_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}""")
            vector_store = FAISS.from_documents(docs, embeddings)
            torch_gc()

        vector_store.save_local(vs_path)
        print("向量生成成功")
        return vs_path, loaded_files
    else:
        print("文件均未成功加载，请检查依赖包或替换为其他文件再次上传。")
        return None, loaded_files



class LocalDocQA:
    filepath: str
    vs_path: str
    load_files: List[str] = []
    top_k: int
    embedding: object
    llm: object
    conversation_with_summary: object
    init: bool = True

    def __init__(self, filepath: str, vs_path: str, embeddings: object,
                       init: bool = True):
        if init:
            vs_path, loaded_files = init_knowledge_vector_store(filepath=LOCAL_CONTENT,
                                                                vs_path=VS_PATH,
                                                                embeddings=embeddings)
        else:
            vs_path = VS_PATH
            loaded_files = []


        self.load_files = loaded_files
        self.vs_path = vs_path
        self.filepath = filepath
        self.embeddings = embeddings
        self.top_k = VECTOR_SEARCH_TOP_K
        self.llm = CustomLLM()
        self.conversation_with_summary = ConversationChain(llm=self.llm,
                                                       memory=ConversationSummaryBufferMemory(llm=self.llm,
                                                                                              max_token_limit=40),
                                                       verbose=True)

    def query_knowledge(self, query: str):
        vector_store = FAISS.load_local(self.vs_path, self.embeddings)
        vector_store.chunk_size = CHUNK_SIZE
        related_docs_with_score = vector_store.similarity_search_with_score(query, k = self.top_k)
        related_docs = get_docs_with_score(related_docs_with_score)
        related_content = get_related_content(related_docs)
        return related_content

    def get_knowledge_based_answer(self, query: str):
        related_content = self.query_knowledge(query)
        prompt = PromptTemplate(
            input_variables=["context","question"],
            template=PROMPT_TEMPLATE,
        )
        pmt = prompt.format(context=related_content,
                            question=query)

        # answer=self.conversation_with_summary.predict(input=pmt)
        answer = self.llm(pmt)
        return answer
