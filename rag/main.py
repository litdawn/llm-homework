from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Milvus
import os
import re

# 设置大模型API信息
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ["OPENAI_API_KEY"] = "None"
os.environ["OPENAI_API_BASE"] = ""

# 初始化大模型
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(model_name="Qwen2.5-14B")

# from langchain.llms import OpenAI, OpenAIChat
# llm = OpenAIChat(model_name="Qwen2.5-14B")

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L12-v2")
# 初始化向量数据库
db = Milvus(
    embedding_function=embedding,
    collection_name="arXiv",
    connection_args={
        "host": "",
        "port": "",
    }
)

template = """注意，你回答中的实际内容要以```，```包裹，且在全文中只能出现一次，其中不要有解释性文字。"""


def llm_query(question, request=""):
    messages = [
        SystemMessage(content=f"{template}，{request}"),
        HumanMessage(content=question),
    ]
    answer = llm.invoke(messages).content
    # print("answer,", answer)

    # 使用正则表达式提取```answer```内的实际回答内容
    match = re.search(r"```(.*?)```", answer, re.DOTALL)
    return match.group(1).strip() if match else "未找到有效答案"


def generate_preliminary_answer(query):
    return llm_query(f"请给我一个英语的、使用CoT的、能够生成下列问题答案的prompt：{query}")


def optimize_query(query):
    return llm_query(f"{query}，使用英语回答")


def generate_multi_document_answer(query, documents):
    """根据多个相关论文摘要生成综合回答，返回带来源引用的回答"""
    combined_content = "\n\n".join([f"摘要{idx + 1}：{doc}" for idx, doc in enumerate(documents)])
    return llm_query(
        f"""根据以下多个论文摘要生成对问题的简洁回答：
        问题：{query}
        
        多个摘要内容：
        
        {combined_content} 
        """,
        "仅用中文回答问题并用编号引用来源，假设这些摘要与问题均不相关，请在```，```中回答不相关。")


def answer_question(query):
    max_attempts = 5
    attempts = 0

    # Step 1: 找合适的prompt
    optimized_prompt = generate_preliminary_answer(query)
    # print("初步回答:", optimized_prompt)

    while attempts < max_attempts:
        print(f"\n第 {attempts + 1} 轮查询中...")

        # Step 2: 根据上一步的prompt生成一段英文的解释，用于在milvus中查询
        optimized_query = optimize_query(optimized_prompt)
        # # optimized_query = preliminary_answer
        # print(f"优化后的查询: {optimized_query}")

        # Step 3: 在数据库中执行相似度检索

        results = db.similarity_search(f"{optimized_query}", top_k=10)
        # print(f"找到 {len(results)} 条结果。")

        if not results:
            print("未找到任何相关论文。")
            query = f"重新表述：{query}"
            attempts += 1
            continue

        # Step 4: 检查相关性并提取前3篇相关文档 被删掉
        # relevant_results = [(doc, doc.metadata['score']) for doc in results if 'score' in doc.metadata]
        relevant_results = results
        # Step 5: 由用户决定找到的论文是否符合结果。
        if relevant_results:
            print("\n\n".join([f"摘要{idx + 1}：{doc.page_content}" for idx, doc in enumerate(relevant_results)]))
            is_satisfied = input("以上几篇文章是否符合需要？(y/n)")
            if is_satisfied == 'y':
                # 使用多个相关文档生成综合回答
                answer = generate_multi_document_answer(query, relevant_results)
                if "不相关" in answer:
                    new_query = True
                else:
                    new_query = False
                    sources = []
                    # 格式化输出来源信息
                    for idx, doc in enumerate(relevant_results):
                        doc = doc.metadata
                        source_info = {
                            "title": doc['title'],
                            "authors": doc['authors'],
                            "source_url": f"https://arxiv.org/abs/{doc['access_id']}",
                        }
                        sources.append(source_info)

                    return {
                        "answer": answer,
                        "sources": sources
                    }
            else:
                new_query = True
            if new_query:
                good_number = input("请输入最相关的论文序号，系统将以此为基础进行二次查询，没有请输入0")
                bad_number = input("请输入最不符合要求的论文序号，系统将以此为基础进行二次查询。")
                if good_number != "0":
                    optimized_prompt = (f"{optimized_query},for example, a good answer is like:`{relevant_results[int(good_number) - 1]}`"
                                        f"，a bad answer is like:`{relevant_results[int(bad_number) - 1]}`")
                else:
                    optimized_prompt = (
                        f"{optimized_query},for example"
                        f"，a bad answer is like:`{relevant_results[int(bad_number) - 1]}`")
            attempts += 1
        else:
            print("未找到合适答案，将重新查询")
            attempts += 1

    return {"error": "抱歉，未能找到相关答案，请尝试更换查询内容。"}


if __name__ == "__main__":
    print("问答系统已经初始化完毕。")
    while (True):
        user_query = input("请输入你的问题,输入q终止程序\n")
        if user_query == "q":
            break
        response = answer_question(user_query)
        if "answer" in response and response["answer"] != "未找到合适答案，请调整问题":
            print("\n答案：", response["answer"])
            if "sources" in response:
                print("\n引用文献：")
                for idx, source in enumerate(response["sources"], 1):
                    print(f"[{idx}] 论文标题：{source['title']}")
                    print(f"作者：{source['authors']}")
                    print(f"详情页：{source['source_url']}")
            if "error" in response:
                print(response["error"])
        else:
            print("未找到合适的答案，请重新提问")
