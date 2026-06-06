import os
import time
import re
from flask import Flask, render_template, request, jsonify, send_file
from docx import Document
from docx.shared import Pt, RGBColor
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
        category = data.get('category', '电影')

        # 核心创意：系统级提示词升级，要求结构化输出
        prompt = f"""
        你是一位顶级影视编剧和导演。请将以下小说片段转化为{category}剧本，并提供专业分析。
        请严格按以下格式输出，不要使用任何Markdown符号（如*或#）：

        [角色分析]
        （在此提取并分析小说中的主要人物，包括外貌、性格及核心驱动力）

        [专业剧本]
        剧名：《名称》
        类别：{category}
        （场景序号. 地点 - 时间）
        角色名：（动作/神态）台词。

        [视觉分镜提示词]
        （为每个主要场景提供一段50字以内的视觉描述，用于AI绘图参考，格式：场景1：[描述]）
        """

        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text}
            ]
        )
        
        full_output = res.choices[0].message.content
        # 清洗冗余符号
        full_output = re.sub(r'[*#]', '', full_output)
        
        # 将结果存入临时文件以便下载
        with open("last_record.txt", "w", encoding="utf-8") as f:
            f.write(full_output)

        return jsonify({"success": True, "script": full_output})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "msg": str(e)})

@app.route('/download')
def download():
    try:
        if not os.path.exists("last_record.txt"): return "无记录可下载", 404
        with open("last_record.txt", "r", encoding="utf-8") as f:
            content = f.read()

        doc = Document()
        doc.styles['Normal'].font.name = 'SimSun'
        
        # 分段处理导出
        sections = content.split('\n\n')
        for section in sections:
            p = doc.add_paragraph()
            if "[角色分析]" in section or "[专业剧本]" in section or "[视觉分镜提示词]" in section:
                run = p.add_run(section)
                run.font.size = Pt(14)
                run.font.color.rgb = RGBColor(52, 73, 94)
            elif "剧名" in section:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(section)
                run.font.size = Pt(18)
            elif "场景" in section:
                p.paragraph_format.space_before = Pt(12)
                p.add_run(section)
            else:
                p.add_run(section)

        filename = f"AI_Script_{int(time.time())}.docx"
        path = os.path.join('scripts', filename)
        doc.save(path)
        return send_file(path, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    if not os.path.exists('scripts'): os.makedirs('scripts')
    app.run(debug=True, port=5000)