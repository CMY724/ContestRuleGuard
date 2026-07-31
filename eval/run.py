"""Evaluation runner for ContestRuleGuard."""

import json
import sys
from pathlib import Path


def load_gold(gold_path: Path) -> dict:
    with open(gold_path, encoding="utf-8") as f:
        return json.load(f)


def load_predicted(results_path: Path) -> dict:
    with open(results_path, encoding="utf-8") as f:
        return json.load(f)


def compute_metrics(gold: dict, predicted: dict) -> dict:
    gold_rules = {r["rule_type"]: r for r in gold.get("rules", [])}
    pred_rules = {r["rule_type"]: r for r in predicted.get("rules", [])}

    matched = 0
    total_gold = len(gold_rules)
    total_pred = len(pred_rules)

    for rtype, gold_rule in gold_rules.items():
        if rtype in pred_rules:
            matched += 1

    recall = matched / total_gold if total_gold > 0 else 0.0
    precision = matched / total_pred if total_pred > 0 else 0.0
    f1 = 2 * recall * precision / (recall + precision) if (recall + precision) > 0 else 0.0

    return {
        "total_gold_rules": total_gold,
        "total_predicted_rules": total_pred,
        "matched_rules": matched,
        "recall": round(recall, 4),
        "precision": round(precision, 4),
        "f1": round(f1, 4),
    }


if __name__ == "__main__":
    gold_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("eval/gold/sample_gold.json")
    results_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("eval/results/sample_result.json")
    gold = load_gold(gold_path)
    predicted = load_predicted(results_path)
    metrics = compute_metrics(gold, predicted)
    print(json.dumps(metrics, indent=2))
