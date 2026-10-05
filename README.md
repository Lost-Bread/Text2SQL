# Text2SQL

一个基于大语言模型和 Gradio 的 Text-to-SQL 工具。

用户输入数据库表结构和自然语言查询需求，程序通过大模型自动生成对应的 SQL 查询语句。

## Features

- 自然语言转 SQL
- 支持多个数据库表结构
- 动态生成表结构输入框
- 使用 Prompt Engineering 约束 SQL 输出
- API Key 通过环境变量读取
- Gradio Web UI

## Tech Stack

- Python
- Gradio
- OpenAI-compatible API
- DeepSeek API
- Prompt Engineering

## Run

安装依赖：

```bash
pip install -r requirements.txt