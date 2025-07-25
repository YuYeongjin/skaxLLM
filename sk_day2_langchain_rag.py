# -*- coding: utf-8 -*-
"""sk_day2_langchain_rag

Automatically generated by Colab.

Original file is located at 

#Lang Chain 구조
"""

!pip install numpy==1.26.4
!pip install langchain==0.3.21
!pip install langchain-core==0.3.46
!pip install langchain-experimental==0.3.4
!pip install langchain-community==0.3.20
!pip install langchain-openai==0.3.9
!pip install langchain-chroma==0.2.2
!pip install langchain-cohere==0.4.3
# !pip install langchain-milvus==0.1.8
# !pip install langgraph==0.3.18
# !pip install langsmith==0.3.18
!pip install pymupdf==1.25.4
!pip install pypdf==4.3.1
!pip install pdfplumber==0.11.5
!pip install faiss-cpu==1.10.0
# !pip install langchain-teddynote==0.3.44

import numpy as np
print(np.__version__)

import os
my_key =
os.environ["OPENAI_API_KEY"] = my_key

# openai 에 있는 langchain llm 사용
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=1)
question = "서울의 수도는?"
res = llm.invoke(question)
print(res.content)

question = "분당 정자동의 점심 맛집 10곳 추천해줘"
res = llm.invoke(question)
print(res.content)

question = "langchain_openai을 호출한 것과 그냥 llm을 호출한 것의 정보 차이가 뭐야? 단순 prompt일떄"
res = llm.stream(question)
for chunk in res:
  print(chunk.content, end="", flush=False)

# 반복적으로 긴 문맥이 포함된 Prompt Cache 처리
very_long_prompt = """
당신은 매우 친절한 AI 어시스턴트 입니다.
당신의 임무는 주어진 질문에 대해 친절하게 답변하는 것입니다.
아래는 사용자의 질문에 답변할 때 참고할 수 있는 정보입니다.
주어진 정보를 참고하여 답변해 주세요.


<WANT_TO_CACHE_HERE>
#참고:
**Prompt Caching**
Model prompts often contain repetitive content, like systeommon instructions. OpenAI routes API requests to servers that recently processed the same prompt, making it cheaper and faster than processing a prompt from scratch. This can reduce latency by up to 80% and cost by 50% for long prompts. Prompt Caching works automatically on all your API requests (no code changes required) and has no additional fees associated with it.
m prompts and c
Prompt Caching is enabled for the following models:


gpt-4o (excludes gpt-4o-2024-05-13 and chatgpt-4o-latest)
gpt-4o-mini
o1-preview
o1-mini
This guide describes how prompt caching works in detail, so that you can optimize your prompts for lower latency and cost.


Structuring prompts
Cache hits are only possible for exact prefix matches within a prompt. To realize caching benefits, place static content like instructions and examples at the beginning of your prompt, and put variable content, such as user-specific information, at the end. This also applies to images and tools, which must be identical between requests.


How it works
Caching is enabled automatically for prompts that are 1024 tokens or longer. When you make an API request, the following steps occur:


Cache Lookup: The system checks if the initial portion (prefix) of your prompt is stored in the cache.
Cache Hit: If a matching prefix is found, the system uses the cached result. This significantly decreases latency and reduces costs.
Cache Miss: If no matching prefix is found, the system processes your full prompt. After processing, the prefix of your prompt is cached for future requests.
Cached prefixes generally remain active for 5 to 10 minutes of inactivity. However, during off-peak periods, caches may persist for up to one hour.


Requirements
Caching is available for prompts containing 1024 tokens or more, with cache hits occurring in increments of 128 tokens. Therefore, the number of cached tokens in a request will always fall within the following sequence: 1024, 1152, 1280, 1408, and so on, depending on the prompt's length.


All requests, including those with fewer than 1024 tokens, will display a cached_tokens field of the usage.prompt_tokens_details chat completions object indicating how many of the prompt tokens were a cache hit. For requests under 1024 tokens, cached_tokens will be zero.


What can be cached
Messages: The complete messages array, encompassing system, user, and assistant interactions.
Images: Images included in user messages, either as links or as base64-encoded data, as well as multiple images can be sent. Ensure the detail parameter is set identically, as it impacts image tokenization.
Tool use: Both the messages array and the list of available tools can be cached, contributing to the minimum 1024 token requirement.
Structured outputs: The structured output schema serves as a prefix to the system message and can be cached.
Best practices
Structure prompts with static or repeated content at the beginning and dynamic content at the end.
Monitor metrics such as cache hit rates, latency, and the percentage of tokens cached to optimize your prompt and caching strategy.
To increase cache hits, use longer prompts and make API requests during off-peak hours, as cache evictions are more frequent during peak times.
Prompts that haven't been used recently are automatically removed from the cache. To minimize evictions, maintain a consistent stream of requests with the same prompt prefix.
Frequently asked questions
How is data privacy maintained for caches?


Prompt caches are not shared between organizations. Only members of the same organization can access caches of identical prompts.


Does Prompt Caching affect output token generation or the final response of the API?


Prompt Caching does not influence the generation of output tokens or the final response provided by the API. Regardless of whether caching is used, the output generated will be identical. This is because only the prompt itself is cached, while the actual response is computed anew each time based on the cached prompt.


Is there a way to manually clear the cache?


Manual cache clearing is not currently available. Prompts that have not been encountered recently are automatically cleared from the cache. Typical cache evictions occur after 5-10 minutes of inactivity, though sometimes lasting up to a maximum of one hour during off-peak periods.


Will I be expected to pay extra for writing to Prompt Caching?


No. Caching happens automatically, with no explicit action needed or extra cost paid to use the caching feature.


Do cached prompts contribute to TPM rate limits?


Yes, as caching does not affect rate limits.


Is discounting for Prompt Caching available on Scale Tier and the Batch API?


Discounting for Prompt Caching is not available on the Batch API but is available on Scale Tier. With Scale Tier, any tokens that are spilled over to the shared API will also be eligible for caching.


Does Prompt Caching work on Zero Data Retention requests?


Yes, Prompt Caching is compliant with existing Zero Data Retention policies.
</WANT_TO_CACHE_HERE>


#Question:
{}


"""

from langchain.callbacks import get_openai_callback
with get_openai_callback() as cb:
  res=llm.invoke(very_long_prompt.format("프롬프트 캐싱 기능을 2줄로 설명해줘"))
  print(res)
  print(f"Prompt Token: {cb.prompt_tokens}")
  c_tokens = res.response_metadata["token_usage"]["prompt_tokens_details"]["cached_tokens"]
  print(f"Cached Tokens : {c_tokens}")

"""## Prompt Template Module
### 기본형 템플릿

"""

# 기본 문장 완성 템플릿
from langchain import PromptTemplate
prompt=PromptTemplate.from_template("{contry}의 수도는?")
print(prompt.format(contry="로마")) # 프롬프트 확인

# prompt 에서 바로 LLM으로 연결되는 기능
chain1 = prompt | llm
res=chain1.invoke("로마")
print(res.content)

"""### 대화형 템플릿"""

from langchain.prompts import ChatPromptTemplate
c_prompt = ChatPromptTemplate.from_messages([
    ("system","당신은 친절한 {job}입니다."),
    ("user","{input}")
    ])
print(c_prompt.format(job="수학교사",input="'에어컨의 기능에 대한 수학적 원리'"))

chain2 = c_prompt | llm
res = chain2.invoke({"job": "수학교사",
                    "input":"'에어컨의 기능에 대한 수학적 원리'"} )
print(res.content)

"""## 아웃 파서"""

from langchain_core.output_parsers import StrOutputParser
output_parsers = StrOutputParser()
chain3 = c_prompt | llm  | output_parsers
res = chain3.invoke({"job": "수학교사",
                    "input":"'에어컨의 기능에 대한 수학적 원리'"} )
print(res)

"""## 데이터를 효과적으로 전달하는 방법

## RunnablePassthrough

RunnableLambda

사용자의 입력받은 변수를 parameter로 토스
"""

chain = prompt | llm | output_parsers
res = chain.invoke({"contry":"대만"})
print(res)

from langchain_core.runnables import RunnablePassthrough
RunnablePassthrough().invoke({"contry":"대만"})

chain_runnable = {"contry": RunnablePassthrough()} | prompt | llm | output_parsers
chain_runnable.invoke("대만")

from datetime import datetime
datetime.now().strftime("%b-%d")

def get_today(a):
  return datetime.now().strftime("%b-%d")
  get_today(None)

from langchain_core.runnables import RunnableLambda, RunnablePassthrough
prompt = PromptTemplate.from_template(
"{today}이 생일인 유명 연예인 {n}명을 나열하세요."
 )
chain = prompt | llm | output_parsers
chain.invoke({ "today": get_today,"n":3})
chain = ( {"today": RunnableLambda(get_today), "n":RunnablePassthrough()}|prompt | llm | output_parsers)
res = chain.invoke(3)
print(res)

"""## 임베딩 모델 호출

"""

texts=["좋아하는 음식은 무엇인가요?",
              "어디에 살고 계세요?",
              "오늘은 기분이 어떻세요?",
              "길이 많이 막히네요",
              "날씨가 덥습니다"]

# text-embedding-3-large
# text-embedding-ada-002

from openai import OpenAI

client = OpenAI()
res  = client.embeddings.create(input=texts, model="text-embedding-3-large")
len(res.data[0].embedding)

import numpy as np
vecs = np.array([ elt.embedding for elt in res.data ])
vecs.shape

q = "오늘 서울 날씨?"
res  = client.embeddings.create(input=[q], model="text-embedding-3-large")
q_vec = np.array(res.data[0].embedding)
q_vec.shpae

# 행렬의 거리 연산
np.sqrt( ((vecs-q_vec)**2).sum(1))

result = np.sqrt( ((vecs-q_vec)**2).sum(1)).argsort()
print(result)

for idx in result:
  print(texts[idx])

"""# RAG : 전 과정

## 1. 문서 로드 => text document 형태로 추출

## 2. 문서 분할(Split Chunk 분할)

## 3. Embedding => 벡터 DB에 저장

## 4. 리트리버 설정 (검색)

## 5. Context와 사용자 Query 생성자에게 전달 (Prompting)

## 6. LLM 응답받기
"""

#1. 문서 로드 => text, document로 추출
with open("/content/akazukin_all.txt") as f:
  text = f.read()

#2. Chunk 분할 -> chunk_size를 상황에 맞게 지정해야함
from langchain.text_splitter import CharacterTextSplitter
text_splitter = CharacterTextSplitter(separator="\n\n",chunk_size=300, chunk_overlap=20)
docs = text_splitter.split_text(text)
len(docs)

for doc in docs:
  print(doc[:30])

# 3. 임베딩=> 벡터보관소에 저장 (db)
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
embeddings=OpenAIEmbeddings(model="text-embedding-3-large")
db=FAISS.from_texts(docs, embeddings)

#4. 리트리버 설정 => 컨텍스트 기반 검색 (시멘틱)
my_retriever= db.as_retriever()
my_retriever.invoke("미코의 적인 악당 이름은?")

#5. Context와 사용자 Query 생성자에게 전달 (Prompting)

# RAG 문서 프롬프트
system = """당신은 질문-답변(Question-Answering)을 수행하는 친절한 AI 어시스턴트입니다.
당신의 임무는 주어진 문맥(context) 에서 주어진 질문(question) 에 답하는 것입니다.
검색된 다음 문맥(context) 을 사용하여 질문(question) 에 답하세요.
만약, 주어진 문맥(context) 에서 답을 찾을 수 없다면,
`주어진 정보에서 질문에 대한 정보를 찾을 수 없습니다` 라고 답하세요.
기술적인 용어나 이름은 번역하지 않고 그대로 사용해 주세요.
답변은 한글로 답변해 주세요.
#Question:{question}
#Context:{context}
#Answer:"""

prompt = PromptTemplate.from_template(system)
llm=ChatOpenAI(model="gpt-4.1-nano", temperature=0)
chain = {"question":RunnablePassthrough(),"context":my_retriever}|prompt | llm | output_parsers

chain.invoke("미코의 적인 악당 이름은?")

"""## 문서 로더 (PDF)"""

from langchain_community.document_loaders import PyMuPDFLoader
loader=PyMuPDFLoader("/content/sample.pdf")
docs=loader.load()
print(len(docs))
docs[0]

"""## splitter => RecursiveCharacterTextSplitter"""

from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=20, length_function=len)
texts= splitter.split_documents(docs)
print(len(texts))

# db 구성
# 리트리버
# chain 구성
# 질문 : 속도 제한을 어기면 어떤 처벌을 받아?

# DB 구성

from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
embeddings=OpenAIEmbeddings(model="text-embedding-3-large")
db=FAISS.from_documents(texts, embeddings)

# 리트리버
yjyoo_retriever = db.as_retriever()
#yjyoo_retriever.invoke("속도 제한을 어기면 어떤 처벌을 받아?")

# chain 구성
prompt = PromptTemplate.from_template(system)
llm=ChatOpenAI(model="gpt-4.1-nano", temperature=0)
chain = {"question":RunnablePassthrough(),"context":yjyoo_retriever} | prompt | llm | output_parsers

# Query
chain.invoke("속도 제한을 어기면 어떤 처벌을 받아?")

"""## DB

### Chroma 버전 관리에 유의 (충돌이 잦음)
"""

from langchain_community.document_loaders import TextLoader

loader1 = TextLoader("/content/finance-keywords.txt")
loader2 = TextLoader("/content/nlp-keywords.txt")

splitter = RecursiveCharacterTextSplitter(chunk_size=450, chunk_overlap=50, length_function=len)

doc1=loader1.load_and_split(splitter)
doc2=loader2.load_and_split(splitter)

print(len(doc1), len(doc2))

print(doc1[0])

# db 인메모리로 사용
from langchain_chroma import Chroma
embedding = OpenAIEmbeddings(model="text-embedding-3-large")
db = Chroma.from_documents(doc1, embedding,collection_name="finance")

# 정보 조회
db.get()

# local 생성
db_local = Chroma.from_documents(doc1, embedding, persist_directory="./db", collection_name="finance_db")
db_local.get()

# 설치된 자료의 파일 조회
loaded_db = Chroma(persist_directory="/content/db", embedding_function=embedding,collection_name="finance_db")
loaded_db.get()

# db에서 자체적인 유사도 검색 기능 활용
db.similarity_search("블루칩 주식이 뭐야?",k=2, filter={"source":"/content/finance-keywords.txt"})

# db에 문서 추가
db.add_documents(doc2)
print(len(db.get()["ids"]))

db.similarity_search("Word2vec이 뭐야?", k=3, filter={"source":"/content/nlp-keywords.txt"})

# 문서 삭제
db.delete(ids=['875e304e-bd7e-4ce2-bb94-9c9556acde40'])

"""## 리트리버 구성

"""

# retriever 설정
#similarity, mmr, similarity_score_threshold
# mmr : 다양한 정보의 검색

my_retriever = db.as_retriever(search_type = "mmr", search_kwargs={"k":3 , "fetch_k":6})
my_retriever.invoke("word2vec이 뭐야?")

# 실습
# 1.pdf Load
# 2. recursive로 split
# 3. chroma db => retriever mmr 10 개중 5개
# 4. chain 구성
# 5. q= " 한국형 스마트팜 구성요소 중 2세대 기본 구성요소는?"

#1
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PDFPlumberLoader
pdf_loader = PDFPlumberLoader("/content/차세대 한국형 스마트팜 개발.pdf")
#2
pdf_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30,length_function=len)
pdf_docs = pdf_loader.load_and_split(pdf_splitter)
#3
from langchain_chroma import Chroma
embeddings=OpenAIEmbeddings(model="text-embedding-3-large")
pdf_db = Chroma.from_documents(pdf_docs, embeddings, persist_directory="./pdf_db", collection_name="pdf_db")

pdf_retriever=pdf_db.as_retriever(search_type="mmr", search_kwargs={"k":5, "fetch_k":10})
# pdf_retriever.invoke("한국형 스마트팜 구성요소 중 2세대 기본 구성요소는?")
#4
chain =  {"question":RunnablePassthrough(), "context":pdf_retriever} | prompt | llm | output_parsers
#5
chain.invoke("한국형 스마트팜 구성요소 중 2세대 기본 구성요소는?")

"""### FAISS DB"""

from langchain_community.document_loaders import TextLoader

loader1 = TextLoader("/content/finance-keywords.txt")
loader2 = TextLoader("/content/nlp-keywords.txt")

splitter = RecursiveCharacterTextSplitter(chunk_size=450, chunk_overlap=50, length_function=len)

doc1=loader1.load_and_split(splitter)
doc2=loader2.load_and_split(splitter)

print(len(doc1), len(doc2))

fbd1= FAISS.from_documents(doc1,OpenAIEmbeddings())
fbd2= FAISS.from_documents(doc2,OpenAIEmbeddings())

fbd1.index_to_docstore_id

#개별 Data를 merge
fbd1.merge_from(fbd2)
print(len(fbd1.index_to_docstore_id))

# 로컬에 저장
fbd1.save_local("/content/faiss_db", index_name="faiss_db")

# 불러오기
loaded_fbd = FAISS.load_local("/content/faiss_db", OpenAIEmbeddings(), index_name="faiss_db" , allow_dangerous_deserialization=True)
len(loaded_fbd.index_to_docstore_id)

# Chain 형성 chain type
#stuff :retriever가 찾은 모든 것을 보내줌
#map_reduce : LLM을 독립적으로 여러번 호출하여 정리
#refine : 문서의 답변을 순차적으로 LLM호출하여 정리
#map_rerank : 문서의 답변의 rank를 매겨 최종 순위 대로 정리

# from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain

r_chain = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, retriever=pdf_retriever, chain_type="stuff")
r_chain.invoke("한국형 스마트팜 구성요소 중 2세대 기본 구성요소는?")

"""## 여러가지 문서 Load"""

!pip install docx2txt
!pip install python-pptx
!pip install unstructured openpyxl

from langchain_community.document_loaders import CSVLoader

CSVLoader("/content/booksv_02.csv")
