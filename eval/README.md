# 赛规通评测数据集

## 结构
- cases/ — 真实竞赛规则文档样本
- gold/ — 人工标注的正确答案
- aselines/ — 基线方法结果
- 
esults/ — 赛规通运行结果

## 评测维度
1. 规则召回率 (Recall): 发现多少条真实规则
2. 规则精确率 (Precision): 抽取的规则中有多少是正确的
3. 字段准确率 (Field Accuracy): deadline/eligibility 等字段值是否准确
4. 证据溯源率 (Evidence Traceability): 每条规则是否有可追溯的证据来源
5. 冲突发现率 (Conflict Detection): 是否发现文档间的规则冲突
