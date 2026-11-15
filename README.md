# 🔥 FireSafe AI

**NASA microgravity combustion research dashboard and source-grounded Qwen assistant**

FireSafe helps users ask questions about NASA combustion studies, browse selected experimental findings, and compare reported test conditions. It is a research **prototype**, not a certified combustion simulator.

## Researcher workflow

1. **Ask FireSafe AI:** Type a free-form question. FireSafe retrieves NASA PDF passages and, **only when the trained model has been loaded**, asks Qwen to prepare a source-grounded explanation.
2. **Explore Experiments:** Inspect research purposes, fuels, atmospheres, airflow conditions, findings, and page references for BASS, BASS-II, Saffire and BRE.
3. **Compare Studies:** View experiments side by side and see limitations arising from differences in geometry, atmosphere, fuel or measurement definitions.

The submitted app hides the standalone Research Evidence tab. Retrieved sources are still displayed with AI answers.

## Technology

Python, Gradio, PyMuPDF, scikit-learn TF-IDF, Qwen2.5-3B-Instruct with LoRA, Kaggle GPU, Hugging Face. Audio used in the demonstration may be credited separately if applicable.

## Project files

- `app.py` — standalone Gradio dashboard. It contains its own NASA PDF retrieval and can run in evidence-only mode without Qwen.
- `retrieval.py` — **separately executable implementation** of PDF indexing and passage search, for inspection and smoke testing. `app.py` presently uses its own retrieval functions rather than importing this module.
- `evaluation.py` — retrieval smoke tests only; **not** a claim of model accuracy or scientific verification.
- `requirements.txt` — dashboard dependencies.
- `sources.md` — NASA publication references and PDF page conventions.
- `run_in_kaggle.md` — reproduction steps.
- `training-notebook-link.md` — link to the existing Kaggle notebook; the full notebook is **not included** in this package.

## Quick start on Kaggle

1. Attach the existing NASA `FireSafe AI v3 Training Data` dataset.
2. Upload the project source or attach the Kaggle dataset containing `app.py`.
3. Run `!pip install -q -r requirements.txt` or install the listed dependencies in a notebook cell.
4. Run `%run /kaggle/working/FireSafe_GitHub_Submission/app.py` (adjust the path to wherever you copy the source).
5. Open the temporary Gradio URL. **The server goes offline when the Kaggle session ends.**

The AI assistant needs an actual fine-tuned Qwen adapter loaded into the **same notebook session** as `model` / `tokenizer`, or a callable `generate_firesafe(messages,max_new_tokens=280)`. The Qwen adapter is in the private repository `arifengine/FireSafe-Qwen2.5-3B-v3.2-Reproduction` at the time of writing; public reviewers cannot reproduce model answers until appropriate access is granted. **Never commit Hugging Face tokens or Kaggle secrets.**

## Verify PDF search independently

```bash
python retrieval.py --papers /path/to/NASA/papers
python evaluation.py --papers /path/to/NASA/papers
```

If PDF indexing returns zero passages, check that the PDFs are available and PyMuPDF is installed. The indexing module raises a clear error instead of silently returning an empty index.

## Source code and training

Training notebook: https://www.kaggle.com/code/arifengine/firesafe-ai-v3-qwen-training/notebook

See `sources.md` for the NASA publications. See `run_in_kaggle.md` for reproducible application steps. Share an archived demo video and a public copy of the source so the project remains reviewable when the Gradio URL expires.

## Scientific integrity

Fine-tuning and retrieval are not proof of scientific correctness. FireSafe can retrieve irrelevant passages or generate unsupported answers. Validate claims against original sources and preserve experimental context. The system does not generate new experimental data or certify spacecraft/planetary-habitat safety.
