小说自动化转剧本工具

本项目是一个基于 Python Flask 框架开发的自动化创作助手，旨在将小说文本快速转换为符合工业标准的剧本格式。

核心功能

多类别适配：支持电影、电视剧、短剧、微电影等多种影视类别的针对性排版。
专业排版输出：自动解析场景、人物小传、动作描写及角色台词，去除任何 Markdown 干扰符号。
Word 一键导出：支持生成 `.docx` 格式文档，并针对场景行和剧名进行了文档流间距优化，符合拍摄手稿需求。
实时预览：前端支持剧本字数统计与实时转换结果预览。

技术栈

后端: Python 3.9 / Flask
模型调用: DeepSeek API
文档处理: python-docx
前端: HTML5 / CSS3 / JavaScript (Fetch API)

目录结构

```text
.
├── app.py              # 后端核心逻辑与 API 路由
├── templates/          # 前端视图文件
│   └── index.html      # 交互界面
├── scripts/            # 导出的 Word 脚本存放目录
├── .env                # 配置文件（存放 API Key，需自行创建）
└── requirements.txt    # 项目依赖清单