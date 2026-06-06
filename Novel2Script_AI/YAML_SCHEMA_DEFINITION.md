剧本全要素数字化协议 (Full-Mapping YAML Schema)

1. 设计初衷
本 Schema 不仅是为了满足格式要求，更是为了实现剧本的“数字化双胞胎”。每一段台词、每一个动作描写在 YAML 中都有唯一的 `type` 标签和归属场景。

2. 字段详细说明
- metadata: 记录剧本基本属性，方便影视资产管理。
- analysis: 数字化映射“剧本医生”模块，将感性的评价量化为机器可读的 `tension_score`。
- characters: 将角色小传结构化，便于对接数字人生成引擎。
- scenes: 
    - `setting`: 结构化场景头，可一键导出通告单。
    - `content`: 核心区域。通过 `type: action` 或 `type: dialogue` 严格映射剧本每一行内容，确保数据无损转换。
    - `visual_prompt`: 为每个场景预留视觉接口，支持一键驱动 AI 绘画工具。

3. 对议题三要求的响应
本 Schema 完美支持了长达 3 章节以上的小说处理，通过 `scene_no` 的无限扩展能力，确保了大型长篇叙事作品的结构化稳定性。