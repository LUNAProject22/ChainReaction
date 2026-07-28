"""
Generic causal chain generator for video QA datasets.

Reads any flat annotation file (CSV or JSON), maps columns to the required
fields via flags, and writes a JSON file of causal chains:
    {"<key>": "event_A -> event_B -> event_C", ...}

The script resumes safely if interrupted — already-processed keys are skipped.

Usage:
    export OPENAI_API_KEY=<your-key>

    # Minimal — question/answer columns named "question" and "answer":
    python causal_chain_generator.py \
        --annotations data.csv --output chains.json

    # Custom column names, row filter, and key column:
    python causal_chain_generator.py \
        --annotations data.csv \
        --question-col Question --answer-col Answer \
        --key-col qid --filter type=CW \
        --output chains.json
"""

import argparse
import json
import os

import openai
import pandas as pd


_PROMPT_BASE = (
    "What is the causal chain in the following question-answer pair? "
    "Please return the concise causal chain in the form of "
    "event_A -> event_B -> event_C... without any additional text"
)

def load_annotations(path: str) -> pd.DataFrame:
    """Load a CSV or JSON annotation file into a DataFrame.

    JSON can be a list of objects or a dict-of-dicts (outer key becomes '_key').
    """
    if path.endswith(".csv"):
        return pd.read_csv(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return pd.DataFrame(data)
    # dict-of-dicts: preserve the outer key so it can be used as --key-col _key
    return pd.DataFrame([{"_key": k, **v} for k, v in data.items()])


def build_message(question: str, answer: str) -> str:
    return f"{_PROMPT_BASE}:\nQuestion: {question}\nAnswer: {answer}"


def generate_causal_chain(client: openai.OpenAI, message: str, model: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
    )
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(
        description="Generate causal chains for video QA pairs using GPT-4o."
    )
    parser.add_argument("--annotations", required=True, help="Path to annotation file (CSV or JSON).")
    parser.add_argument("--output", required=True, help="Output JSON file path.")
    parser.add_argument("--question-col", default="question", help="Column name for questions (default: question).")
    parser.add_argument("--answer-col", default="answer", help="Column name for answers (default: answer).")
    parser.add_argument("--key-col", default=None, help="Column to use as output key (default: row index).")
    parser.add_argument("--filter", default=None, metavar="COL=VAL", help="Only process rows where COL equals VAL (e.g. type=CW).")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI model (default: gpt-4o).")
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set.")
    client = openai.OpenAI(api_key=api_key)

    df = load_annotations(args.annotations)
    print(f"Loaded {len(df)} rows from {args.annotations}")

    if args.filter:
        col, val = args.filter.split("=", 1)
        df = df[df[col] == val]
        print(f"After filter '{args.filter}': {len(df)} rows")

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Load any existing results to support resuming an interrupted run.
    results = {}
    if os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            results = json.load(f)
        print(f"Resuming — {len(results)} entries already processed.")

    for i, row in df.iterrows():
        key = str(row[args.key_col]) if args.key_col else str(i)
        if key in results:
            continue

        question = str(row[args.question_col])
        answer = str(row[args.answer_col])

        chain = generate_causal_chain(client, build_message(question, answer), args.model)
        results[key] = chain

        # Write after every entry so progress is never lost on interruption.
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"Key: {key}\nQuestion: {question}\nAnswer: {answer}\nChain: {chain}")
        print("-" * 40)

    print(f"Done. {len(results)} causal chains saved to {args.output}")


if __name__ == "__main__":
    main()
