import os
import yaml
import datetime
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# ==========================================
# 1. 增强版环境配置加载
# ==========================================
# 获取当前脚本所在的绝对路径，确保一定能找到 .env 文件
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
load_dotenv(env_path)

# 获取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

# 【调试打印】
print("-" * 30)
if api_key:
    print(f"✅ 成功读取到 API Key: {api_key[:8]}******{api_key[-4:]}")
else:
    print("❌ 错误：未读取到 DEEPSEEK_API_KEY，请检查 .env 文件！")
print("-" * 30)

os.makedirs('scripts', exist_ok=True)

# ==========================================
# 2. 配置 DeepSeek 客户端
# ==========================================
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

app = Flask(__name__)

# ==========================================
# 3. 核心 Prompt 设定（全中文标签版本）
# ==========================================
SYSTEM_PROMPT = """你是一位专业的金牌编剧。你的任务是将用户输入的小说文本转换为结构化的剧本（YAML格式）。
必须严格遵守以下规则：
1. 输出格式必须是纯 YAML 代码，严禁包含任何 Markdown 符号（如 ```yaml ）。
2. 【全中文标签要求】YAML 的所有字段名（Key）必须使用中文，不得出现 metadata, characters, scenes 等英文单词。
   请严格遵循以下中文 Schema 结构：
   - 剧本信息: (包含 标题, 类型, 作者, 梗概)
   - 角色列表: (包含 角色名, 身份描述, 性格特征)
   - 场景列表: (包含 场景序号, 地点, 时间, 剧情内容)
     - 剧情内容 内部包含: (说话人, 动作, 台词)
3. 角色名必须使用小说中的真实姓名，不得使用代号。
4. 动作描写要专业，台词要符合角色性格。"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        novel_text = data.get('text', '')
        
        if not novel_text:
            return jsonify({"error": "请输入小说内容"}), 400

        # 4. 调用 DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"请将以下小说内容转换为全中文标签的剧本：\n\n{novel_text}"},
            ],
            stream=False
        )
        
        yaml_content = response.choices[0].message.content.strip()
        
        # 5. 增强版清理 YAML 格式
        if "```" in yaml_content:
            match = re.search(r"```(?:yaml)?\s*([\s\S]*?)\s*```", yaml_content)
            if match:
                yaml_content = match.group(1).strip()
        
        # 移除可能残留在顶部的 "yaml" 字样
        if yaml_content.lower().startswith("yaml"):
            yaml_content = yaml_content[4:].strip()

        # 6. 自动保存
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"script_{timestamp}.yaml"
        filepath = os.path.join('scripts', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        return jsonify({
            "success": True,
            "yaml": yaml_content,
            "file_saved": filepath
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)