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
        category = data.get('category', '标准制片模式')

        # 核心指令：强制中文创作与结构化对齐
        prompt = f"""
        你是一位影视工业化制片专家。请将小说重构为【{category}】剧本。
        
        ### 任务要求：
        1. 完整性：无损保留原著的所有细节、对话和心理转折。
        2. 结构化：必须生成 25-40 个场次。
        3. 语言：剧本描写、台词、场景信息必须使用【中文】。
        4. 分布：将所有场次按叙事进度均匀分配到 ["序幕", "叙事发展", "冲突爆发", "高潮", "结局"]。

        输出板块要求（严格按以下标签输出）：

        [[DIAGNOSIS]]
        [文学诊断报告] (包含中文节奏建议)

        [[TEXT_VERSION]]
        [剧本正文]
        第 1 场：(地点)，(时间)，(内外景)
        画面描写：(细腻的中文动作描写)
        角色名：(台词)
        ...

        [[YAML_VERSION]]
        ---
        metadata:
          title: "生产映射数据"
        scenes:
          - scene_no: 1
            stage: "序幕"
            tension: 5
            setting: {{ loc: "地点", time: "时间", type: "内外景" }}
            props: ["道具"]
            characters: ["角色"]
            content:
              - type: "action"
                text: "画面动作"
              - type: "dialogue"
                role: "角色"
                text: "台词内容"
        ---
        """

        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位专业的中文剧本创作专家。"},
                {"role": "user", "content": prompt + "\n\n原文：\n" + raw_text}
            ],
            temperature=0.3
        )
        
        full_output = res.choices[0].message.content
        full_output = re.sub(r'[*#]', '', full_output)
        
        return jsonify({"success": True, "script": full_output})

    except Exception as e:
        return jsonify({"success": False, "msg": str(e)})

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        content, file_type = data.get('content', ''), data.get('type', 'docx')
        if not content: return jsonify({"success": False}), 400

        if file_type == 'yaml':
            filename = f"Production_Data_{int(time.time())}.yaml"
            path = os.path.join('scripts', filename)
            with open(path, "w", encoding="utf-8") as f: f.write(content)
        else:
            doc = Document()
            doc.styles['Normal'].font.name = 'SimSun'
            for line in content.split('\n'):
                line = line.strip()
                if not line: continue
                p = doc.add_paragraph()
                if "[" in line and "]" in line:
                    run = p.add_run(line)
                    run.font.bold, run.font.size = True, Pt(12)
                    run.font.color.rgb = RGBColor(230, 126, 34)
                else:
                    p.add_run(line)
            filename = f"Smart_Script_Export_{int(time.time())}.docx"
            path = os.path.join('scripts', filename)
            doc.save(path)
        return jsonify({"success": True, "filename": filename})
    except Exception as e: return jsonify({"success": False, "msg": str(e)})

@app.route('/get_file/<filename>')
def get_file(filename):
    return send_file(os.path.join('scripts', filename), as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('scripts'): os.makedirs('scripts')
    app.run(debug=True, port=5000)