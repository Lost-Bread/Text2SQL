import os
import gradio as gr
from openai import OpenAI


# =========================
# 核心：大模型调用逻辑
# =========================
def generate_sql(num_tables, requirement, *table_structs):

    # 1. 从环境变量读取 API Key
    api_key = os.environ.get("DEEPSEEK_API_KEY")

    if not api_key:
        return "❌ 错误：未检测到 DEEPSEEK_API_KEY 环境变量。"

    # 2. 校验用户需求
    if not requirement or not requirement.strip():
        return "❌ 错误：请输入生成 SQL 的需求。"

    # 3. 过滤空白表结构
    valid_structures = [
        s.strip()
        for s in table_structs
        if s and s.strip()
    ]

    if not valid_structures:
        return "❌ 错误：请至少填写一个有效的表结构。"

    # 检查实际填写数量
    if len(valid_structures) < int(num_tables):
        return (
            f"❌ 错误：你设置了 {int(num_tables)} 个表结构，"
            f"但实际只填写了 {len(valid_structures)} 个。"
        )

    # 4. 整理所有表结构
    table_str = "\n\n".join(
        [
            f"表结构 {i + 1}:\n{s}"
            for i, s in enumerate(valid_structures)
        ]
    )

    # 5. System Prompt
    system_prompt = """
你是一个专业的 Text to SQL 专家。

你的任务是：
根据用户提供的数据库表结构和自然语言需求，
生成准确、可执行的 SQL 查询语句。

必须遵守以下规则：

1. 只能使用用户提供的表名和字段名。
2. 严禁虚构不存在的表、字段或数据库信息。
3. 如果现有表结构无法完成用户需求，不要猜测。
4. 如果信息不足，请使用 SQL 注释说明缺少什么信息。
5. 只输出 SQL 代码或 SQL 注释，不要输出额外解释。
6. SQL 应语法正确，默认使用标准 SQL / MySQL 风格。
"""

    # 6. User Prompt
    user_prompt = f"""
以下是数据库表结构：

{table_str}

用户的查询需求：

{requirement}

请根据以上信息生成 SQL。
"""

    # 7. 调用 DeepSeek
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.1,
            stream=False
        )

        result = response.choices[0].message.content

        if not result:
            return "❌ 错误：模型没有返回 SQL。"

        # 去掉模型可能生成的 Markdown ```sql
        result = result.strip()

        if result.startswith("```sql"):
            result = result[6:]

        if result.startswith("```"):
            result = result[3:]

        if result.endswith("```"):
            result = result[:-3]

        return result.strip()

    except Exception as e:
        return f"❌ API 调用失败：{str(e)}"


# =========================
# 构建 Gradio UI
# =========================
custom_css =  """
/* 整个页面统一字体 */
* {
    font-family: -apple-system, BlinkMacSystemFont,
                 "PingFang SC",
                 "Microsoft YaHei",
                 Arial,
                 sans-serif !important;
}

/* 主标题 */
h1 {
    font-family: -apple-system, BlinkMacSystemFont,
                 "PingFang SC",
                 "Microsoft YaHei",
                 Arial,
                 sans-serif !important;
    font-weight: 1400 !important;
    letter-spacing: 0 !important;
}

/* 输入框里的正常文字 */
input,
textarea {
    font-family: -apple-system, BlinkMacSystemFont,
                 "PingFang SC",
                 "Microsoft YaHei",
                 Arial,
                 sans-serif !important;
    font-style: normal !important;
}

/* 输入框里的灰色提示文字 placeholder */
input::placeholder,
textarea::placeholder {
    font-family: -apple-system, BlinkMacSystemFont,
                 "PingFang SC",
                 "Microsoft YaHei",
                 Arial,
                 sans-serif !important;
    font-style: normal !important;
    font-weight: 400 !important;
}
"""
with gr.Blocks(
        theme=gr.themes.Soft(),
        css=custom_css
) as demo:

    gr.Markdown("**MWT**的Text-to-SQL : 输入自然语言转换成SQL")

    # 1. 输入表结构数量
    num_tables = gr.Number(
        label="请输入你需要填写的表结构数量:",
        value=1,
        precision=0,
        minimum=1
    )

    # 2. 动态生成表结构输入框
    @gr.render(inputs=num_tables)
    def render_table_inputs(num):

        if num is None:
            num = 1

        num = max(1, int(num))

        table_boxes = []

        # 根据用户填写的数量生成表结构输入框
        for i in range(num):

            box = gr.Textbox(
                label=f"请输入表结构 {i + 1}:",
                lines=6,
                placeholder=(
                    "例如：\n"
                    "CREATE TABLE users (\n"
                    "    id INT,\n"
                    "    name VARCHAR(50),\n"
                    "    age INT\n"
                    ");"
                )
            )

            table_boxes.append(box)

        # 3. SQL需求输入框
        sql_requirement = gr.Textbox(
            label="请输入生成SQL的需求:",
            lines=4,
            placeholder="例如：查询所有年龄大于18岁的用户姓名，按年龄降序排列"
        )

        # 4. 生成按钮
        submit_btn = gr.Button(
            "生成 SQL",
            variant="primary"
        )

        # 5. 输出结果
        output = gr.Code(
            label="生成的 SQL 结果",
            language="sql",
            lines=10
        )

        # 6. 按钮绑定
        submit_btn.click(
            fn=generate_sql,
            inputs=[
                num_tables,
                sql_requirement,
                *table_boxes
            ],
            outputs=output
        )


if __name__ == "__main__":
    demo.launch()