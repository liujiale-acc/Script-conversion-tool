import os
import time
import re
from flask import Flask, render_template, request, jsonify, send_file
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        raw_text = data.get('text', '')
        category = data.get('category', '电影') # 修改为类别

        # 调整提示词，强调纯文本排版，不带任何符号
        prompt = f"""
        你是一位专业影视编剧。请将小说转为{category}剧本。
        要求：
        1. 严禁使用任何Markdown符号（如 *、#、**）。
        2. 格式结构：
           剧名：《名称》
           时长：10-15分钟
           类别：{category}
           
           主要人物设定：
           名字：描述。
           
           （场景序号. 地点 - 时间）
           角色名：（动作/神态）台词。
        """

        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text}
            ]
        )
        
        output = res.choices[0].message.content
        # 彻底清洗星号和井号，确保纯净
        output = re.sub(r'[*#]', '', output)
        
        with open("last_record.txt", "w", encoding="utf-8") as f:
            f.write(output)

        return jsonify({"success": True, "script": output})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route('/download')
def download():
    try:
        if not os.path.exists("last_record.txt"): return "404", 404
        with open("last_record.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        doc = Document()
        # 统一使用宋体，无加粗
        doc.styles['Normal'].font.name = 'SimSun'
        doc.styles['Normal'].font.size = Pt(11)

        for line in lines:
            line = line.strip()
            if not line: continue
            
            p = doc.add_paragraph()
            
            # 剧名：居中处理，但不加粗
            if line.startswith("剧名"):
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(line)
                run.font.size = Pt(16)
            
            # 场景行：增加段前间距，方便视觉切分，但不加粗
            elif line.startswith("（场景") or line.startswith("场景"):
                p.paragraph_format.space_before = Pt(18)
                p.add_run(line)
            
            # 其他内容：直接填入
            else:
                p.add_run(line)

        path = os.path.join('scripts', f"script_{int(time.time())}.docx")
        doc.save(path)
        return send_file(path, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    if not os.path.exists('scripts'): os.makedirs('scripts')
    app.run(debug=True)