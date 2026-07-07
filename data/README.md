## Data Format

Each dataset JSON file is a dictionary mapping a key to its causal chain annotation. The key format differs per dataset:

### CausalChaos
Keys are **QIDs** (question IDs) as strings.

```json
{
  "1": { ... },
  "2": { ... }
}
```

### NextQA
Keys are **`{video_id}/{qid}`** pairs.

```json
{
  "8968804598/0": { ... },
  "2617504308/3": { ... }
}
```

### CausalVidQA
Keys are the **question ID / folder name** directly (the video clip identifier used in the original dataset).

```json
{
  "--DiygSPius_000052_000062": { ... },
  "--GEr5-PyTI_000000_000010": { ... }
}
```

## Generating Your Own Chains

[utils/causal_chain_generator.py](utils/causal_chain_generator.py) is a generic script for generating causal chain annotations from any video QA dataset. It accepts CSV or JSON annotation files, maps columns to the required fields via flags, and writes a JSON file of causal chains in the format used by this dataset.

The script uses GPT-4o by default, and a predefined simple prompt as used in our experiments. We encourage users to explore more diverse prompts and newer models for potentially richer causal chains. The script resumes safely if interrupted — already-processed keys are skipped.

**Requirements:** set your OpenAI API key:
```bash
export OPENAI_API_KEY=<your-key>
```

**Minimal usage** (columns named `question` and `answer`):
```bash
python utils/causal_chain_generator.py \
    --annotations data.csv --output chains.json
```

**Custom column names, row filter, and key column:**
```bash
python utils/causal_chain_generator.py \
    --annotations data.csv \
    --question-col Question --answer-col Answer \
    --key-col qid --filter type=CW \
    --output chains.json
```

| Flag | Default | Description |
|---|---|---|
| `--annotations` | *(required)* | Path to annotation file (CSV or JSON) |
| `--output` | *(required)* | Output JSON file path |
| `--question-col` | `question` | Column name for questions |
| `--answer-col` | `answer` | Column name for answers |
| `--key-col` | row index | Column to use as the output key |
| `--filter` | — | Only process rows where `COL=VAL` (e.g. `type=CW`) |
| `--model` | `gpt-4o` | OpenAI model to use |
