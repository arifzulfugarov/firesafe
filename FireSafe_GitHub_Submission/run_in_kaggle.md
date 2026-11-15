# Running FireSafe in Kaggle

## 1. Attach datasets

Attach the **FireSafe AI v3 Training Data** dataset that contains:

```
FireSafe_AI/v3/papers/
  BASS-20140011099.pdf
  BASSII-20160000593.pdf
  saffire_research.pdf
  BRE-20160010073.pdf
  ACME-BRE-OVERVIEW.pdf
```

Upload or attach the source code separately. Kaggle mounts dataset files read-only under `/kaggle/input`.

## 2. Install application dependencies

```python
!pip -q install 'gradio>=5,<7' pandas matplotlib numpy pymupdf scikit-learn
```

## 3. Copy source code to writable directory

Adjust the dataset name if yours differs:

```python
from pathlib import Path
import shutil

apps = [p for p in Path('/kaggle/input').rglob('app.py') if 'firesafe' in str(p).lower()]
assert apps, 'Attach the source-code dataset first.'
out = Path('/kaggle/working/firesafe_submission')
shutil.copytree(apps[0].parent, out, dirs_exist_ok=True)
print(out / 'app.py')
```

## 4. Verify source indexing

```python
%run /kaggle/working/firesafe_submission/retrieval.py --papers /kaggle/input/datasets/arifengine/firesafe-ai-v3-training-data/FireSafe_AI/v3/papers
```

If paths differ, use `Path('/kaggle/input').rglob('BASS-20140011099.pdf')` to locate your attached dataset.

## 5. Start the dashboard

```python
%run /kaggle/working/firesafe_submission/app.py
```

For AI answers, **load the trained adapter and tokenizer in the notebook kernel first**. The model repository `arifengine/FireSafe-Qwen2.5-3B-v3.2-Reproduction` is private; do not put credentials in source code. Your notebook's Kaggle Secret named `HF-TOKEN` can be used in private sessions. If Qwen is not loaded, the dashboard must transparently display evidence-only or a connection message.

## 6. Verify the public demo

Ask: **How does airflow direction affect flame spread in microgravity?**

Check for relevant NASA PDF citations and source passages, and ensure the answer does not claim that opposed flow is universally faster than concurrent flow.

Gradio's public URL is temporary. Record a short demo and preserve a public repository/notebook for judge access.
