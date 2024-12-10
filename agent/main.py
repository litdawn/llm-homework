import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

os.environ["OPENAI_API_KEY"] = "None"
os.environ["OPENAI_API_BASE"] = ""

# 初始化大模型
llm_chat = ChatOpenAI(model="Qwen2.5-14B")

# 假设的课程数据，实际应用中可替换为真实数据来源或数据库操作
courses_all = [
    {"name": "高等数学", "type":"必修","info": "数学"},
    {"name": "大学英语", "type":"选修","info": "英语"},
    {"name": "羽毛球A", "type":"选修","info": "羽毛球初级课程"},
    {"name": "羽毛球B", "type":"选修","info": "羽毛球高级课程"},
    {"name": "游泳", "type":"选修","info": "游泳初级课程"},
    {"name": "计算机基础","type":"必修", "info": "计算机"},
    {"name": "音乐欣赏", "type":"选修","info": "学习音乐"}
]
courses = [c["name"] for c in courses_all]

selected_course = []


def query_courses(type, query_text):
    ans = []
    if query_text == "0":
        for i in courses_all:
            if i['type'] == type:
                ans.append(f"{i['name']}({i['type']}):{i['info']}\n")
        return f"{type}课包括:\n{''.join(ans)}"

    elif query_text in courses:
        for i in courses_all:
            if i["name"] == query_text and i['type'] == type:
                ans.append(f"{i['name']}({i['type']}):{i['info']}\n")
        return f"{type}课包括:\n{''.join(ans)}"

    else:
        possible_courses = query(query_text)
        for i in courses_all:
            if i["name"] in possible_courses and i['type'] == type:
                ans.append(f"{i['name']}({i['type']}) : {i['info']}\n")
        if len(ans) > 0:
            return f"未找到精确匹配课程'{query_text}'，你是否想找的是:\n{''.join(ans)}"
        else:
            return "未找到相关课程"


def query(course_name):
    messages = [
        SystemMessage(
            content=f"请从下列选项中找出与描述最像的若干个课程，你的回应消息只包含课程名称。选项```{str(courses)}```"),
        HumanMessage(content=f"描述：{course_name}"),
    ]

    response = llm_chat.invoke(messages)
    response = response.content
    # 尝试从响应中提取可能的课程建议
    possible_courses = []
    for course in courses:
        if course in response:
            possible_courses.append(course)
    return possible_courses


def select_course(course_name):
    if course_name in courses:
        selected_course.append(course_name)
        return f"已选择{course_name}"

    possible_course = query(course_name)

    if possible_course:
        return f"未找到精确匹配课程'{course_name}'，可能你想选的是：{', '.join(possible_course)}"
    return f"选课失败：未找到课程'{course_name}'"


def delete_course(course_name):
    if course_name in courses:
        if course_name in selected_course:
            selected_course.remove(course_name)
            return f"已删除{course_name}"
        else:
            return f"您未选择{course_name}，无法删除"
    possible_courses = query(course_name)
    if possible_courses:
        return f"未找到精确匹配课程'{course_name}'，可能你想删的是：{', '.join(possible_courses)}"
    return f"删除失败：未找到课程'{course_name}'"


def main():
    print("欢迎使用选课系统！")
    while True:
        print("\n请选择操作：")
        print("1. 查询课程")
        print("2. 选择课程")
        print("3. 删除课程")
        print("4. 已选择的课程")
        print("0. 退出")

        choice = input("请输入选项数字：")

        if choice == "1":
            type = input("请输入查询内容：请输入'必修'，或'选修'")
            query_text = input("额外的要求？没有要求请输入0")
            result = query_courses(type, query_text)
            print("查询结果：")
            print(f"{result}")
        elif choice == "2":
            course_name = input("请输入要选择的课程名称：")
            result = select_course(course_name)
            print(result)
        elif choice == "3":
            course_name = input("请输入要删除的课程名称：")
            result = delete_course(course_name)
            print(result)
        elif choice == "4":
            result = str(selected_course)
            print(f"您目前选择的课程是{result}")
        elif choice == "0":
            print("感谢使用选课系统，再见！")
            break
        else:
            print("无效的选项，请重新输入。")


if __name__ == "__main__":
    main()
