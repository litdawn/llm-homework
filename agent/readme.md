### 使用说明

1. 依赖库
```shell
pip install -U langchain_openai
pip install -U langchain_core
```
2. 运行main.py

### 实现功能

以如下课程列表为例
```python
courses_all = [
    {"name": "高等数学", "info": "数学"},
    {"name": "大学英语", "info": "英语"},
    {"name": "羽毛球A", "info": "羽毛球初级课程"},
    {"name": "羽毛球B", "info": "羽毛球高级课程"},
    {"name": "游泳", "info": "游泳初级课程"},
    {"name": "计算机基础", "info": "计算机"},
    {"name": "音乐欣赏", "info": "学习音乐"}
]
```
#### 1 基础功能
1. 查询必修选修
![img_3.png](img%2Fimg_3.png)
2. 选课

![img.png](img%2Fimg.png)
3. 删除
   1. 成功删除
   
   ![img_1.png](img%2Fimg_1.png)
   2. 不成功删除 
   
   ![img_2.png](img%2Fimg_2.png)

#### 2 进阶功能
1. 选择增强（以选课为例）

![img_4.png](img%2Fimg_4.png)
2. 查询增强

![img_5.png](img%2Fimg_5.png)