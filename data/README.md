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


