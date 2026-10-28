import argparse
import json
from dataclasses import asdict
from .adapters import load_dataset
from .application import EvaluateResponses


def main():
    parser = argparse.ArgumentParser(description="Offline, deterministic rubric evaluation")
    parser.add_argument("--dataset", default="data/evaluation-cases.json")
    parser.add_argument("--fail-on-rejection", action="store_true")
    args = parser.parse_args()
    cases, provider = load_dataset(args.dataset)
    results = EvaluateResponses(provider).execute(cases)
    accepted = sum(result.passed for result in results)
    print(json.dumps({"provider": "synthetic-fixtures", "total": len(results), "passed": accepted,
                      "pass_rate": accepted / len(results) if results else None,
                      "results": [asdict(result) for result in results]}, indent=2, sort_keys=True))
    if args.fail_on_rejection and accepted != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
