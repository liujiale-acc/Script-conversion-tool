# AI 小说转剧本 YAML Schema 定义文档

## 1. 概述
本 Schema 旨在规范 AI 提取小说内容并转换为结构化剧本的过程。通过 YAML 格式，确保剧本在保持人类可读性的同时，能够被下游影视制作软件或自动化渲染引擎解析。

## 2. YAML 结构示例
```yaml
metadata:
  title: "章节名称/小说名"
  source_chapters: "第1-3章"
  generated_at: "2024-06-05"

characters:
  - id: "CHAR_01"
    name: "林之夏"
    description: "24岁，职场新人，性格坚韧，眼神明亮。"

scenes:
  - scene_number: 1
    setting:
      location: "办公室-室内"
      time: "日"
      atmosphere: "紧张、忙碌"
    content:
      - type: "action"
        text: "林之夏快速敲击着键盘，额头渗出细小的汗珠。"
      - type: "dialogue"
        role: "林之夏"
        text: "再快一点，就差最后一行代码了..."
      - type: "parenthetical"
        text: "（自言自语，带着些许哭腔）"