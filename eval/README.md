# ContestRuleGuard Evaluation Dataset

## Overview
6 competition notice cases covering diverse competition types and rule patterns.

## Cases

| # | Case | Type | Key Rule Types |
|---|------|------|----------------|
| 1 | sample_rule_notice | 校赛AI | eligibility, team_size, deadline, anonymity, file_required, file_constraint |
| 2 | provincial_innovation | 省级创新创业 | eligibility, team_size, deadline, file_required, file_constraint, anonymity, consistency |
| 3 | national_programming | 全国程序设计 | eligibility, team_size, deadline, file_required, file_constraint, anonymity |
| 4 | math_modeling | 数学建模 | eligibility, team_size, deadline, file_required, file_constraint, anonymity |
| 5 | english_speech | 英语演讲 | eligibility, team_size, deadline, file_required, file_constraint |
| 6 | multi_track | 多赛道计算机设计 | eligibility, team_size, deadline, file_required, file_constraint, anonymity, consistency |

## Running Evaluation

```bash
cd eval
python run.py
```

## Adding New Cases

1. Create `cases/your_case.txt` with the competition notice text
2. Create `gold/your_case_gold.json` with expected rules
3. Run evaluation to verify
