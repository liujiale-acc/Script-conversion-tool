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

        # v2.0 升级版 Prompt：保留原有功能，新增[剧本诊断报告]
        prompt = f"""
        你是一位顶级影视编剧、导演和剧本医生。请将小说转为{category}剧本。
        请严格按以下格式输出，严禁使用Markdown符号（如*或#）：

        [剧本诊断报告]
        1. 戏剧张力评分：(0-10分)
        2. 节奏建议：(一句话)
        3. 核心冲突：(简述)

        [角色画像分析]
        （提取主要人物的外貌、性格及动机）

        [专业剧本正文]
        剧名：《名称》
        （场景序号. 地点 - 时间）
        角色名：（动作/神态）台词。

        [视觉分镜提示词]
        （为主要场景提供AI绘图描述）
        """

        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text}
            ]
        )
        
        full_output = res.choices[0].message.content
        full_output = re.sub(r'[*#]', '', full_output)
        
        # 存入临时文件（作为备份）
        with open("last_record.txt", "w", encoding="utf-8") as f:
            f.write(full_output)

        return jsonify({"success": True, "script": full_output})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route('/download', methods=['POST'])
def download():
    try:
        # v2.0 改进：接收前端传回的最新文本（包含用户的手动修改）
        data = request.get_json()
        content = data.get('content', '')
        
        if not content:
            return jsonify({"success": False, "msg": "内容为空"}), 400

        doc = Document()
        doc.styles['Normal'].font.name = 'SimSun'
        
        sections = content.split('\n')
        for line in sections:
            line = line.strip()
            if not line: continue
            
            p = doc.add_paragraph()
            # 针对不同板块设置样式
            if any(tag in line for tag in ["[剧本诊断报告]", "[角色画像分析]", "[专业剧本正文]", "[视觉分镜提示词]"]):
                run = p.add_run(line)
                run.font.size = Pt(14)
                run.font.bold = True
                run.font.color.rgb = RGBColor(44, 62, 80)
            elif "剧名" in line:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(line)
                run.font.size = Pt(16)
            else:
                p.add_run(line)

        filename = f"AI_Script_v2_{int(time.time())}.docx"
        path = os.path.join('scripts', filename)
        doc.save(path)
        # 返回文件名，让前端触发下载
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route('/get_file/<filename>')
def get_file(filename):
    return send_file(os.path.join('scripts', filename), as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('scripts'): os.makedirs('scripts')
    app.run(debug=True, port=5000)