import os
import time
import re
from flask import Flask, render_template, request, jsonify, send_file
from docx import Document
from docx.shared import Pt, RGBColor
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

        # v2.1 工业级修复版 Prompt：使用唯一标签确保解析成功
        prompt = f"""
        你是一位影视工业化专家。请将小说章节转换为{category}剧本。
        请严格按以下顺序输出，并包含所有标签（严禁使用Markdown符号）：

        [[DIAGNOSIS]]
        [剧本诊断报告]
        张力评分：(0-10分)
        节奏建议：(详细分析)
        核心冲突：(简述)

        [[TEXT_VERSION]]
        [角色画像分析]
        (提取人物外貌、性格、动机)

        [专业剧本正文]
        (剧本正文内容，包含场景、台词、动作)

        [视觉分镜提示词]
        (场景视觉描述)

        [[YAML_VERSION]]
        ---
        metadata:
          title: "剧名"
          category: "{category}"
        analysis:
          tension_score: 10
          rhythm_advice: "节奏建议"
        characters:
          - name: "角色名"
            traits: ["特征"]
        scenes:
          - scene_no: 1
            setting: {{ loc: "地点", time: "时间", type: "内/外" }}
            content:
              - type: "action"
                text: "动作描写"
              - type: "dialogue"
                role: "角色名"
                emotion: "神态"
                text: "台词内容"
            visual_prompt: "分镜提示词"
        ---
        """

        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text}
            ]
        )
        
        full_output = res.choices[0].message.content
        full_output = re.sub(r'[*#]', '', full_output) # 清理杂质
        
        return jsonify({"success": True, "script": full_output})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        content = data.get('content', '')
        file_type = data.get('type', 'docx')
        
        if not content:
            return jsonify({"success": False, "msg": "内容为空"}), 400

        if file_type == 'yaml':
            filename = f"script_digital_{int(time.time())}.yaml"
            path = os.path.join('scripts', filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            doc = Document()
            for line in content.split('\n'):
                line = line.strip()
                if not line: continue
                p = doc.add_paragraph()
                if "[" in line and "]" in line:
                    run = p.add_run(line)
                    run.font.bold = True
                else:
                    p.add_run(line)
            filename = f"AI_Script_v2.1_{int(time.time())}.docx"
            path = os.path.join('scripts', filename)
            doc.save(path)

        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route('/get_file/<filename>')
def get_file(filename):
    return send_file(os.path.join('scripts', filename), as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('scripts'): os.makedirs('scripts')
    app.run(debug=True, port=5000)