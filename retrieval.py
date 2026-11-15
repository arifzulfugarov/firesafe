"""NASA PDF evidence retrieval for FireSafe.

Uses local PDF files only. No model or credentials required.
The PDF page number in citations is 1-based PDF page index.
"""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache

PDF_FILES = {
    "BASS": "BASS-20140011099.pdf",
    "BASSII": "BASSII-20160000593.pdf",
    "SAFFIRE": "saffire_research.pdf",
    "BRE": "BRE-20160010073.pdf",
    "ACME-BRE": "ACME-BRE-OVERVIEW.pdf",
}


def find_paper_root(root: str | Path | None = None) -> Path:
    """Locate attached PDF directory, or use an explicit directory."""
    if root is not None:
        p = Path(root)
        if not p.is_dir():
            raise FileNotFoundError(f"PDF directory does not exist: {p}")
        return p
    candidates = [
        Path('/kaggle/input/datasets/arifengine/firesafe-ai-v3-training-data/FireSafe_AI/v3/papers'),
        Path('papers'),
    ]
    candidates += [p.parent for p in Path('/kaggle/input').rglob(PDF_FILES['BASS'])] if Path('/kaggle/input').exists() else []
    for p in candidates:
        if (p / PDF_FILES['BASS']).is_file():
            return p
    raise FileNotFoundError('NASA PDF dataset not found. Attach FireSafe AI v3 Training Data to Kaggle, or pass --papers PATH.')


def build_index(root: str | Path | None = None, *, chunk_words: int = 200, stride_words: int = 150):
    """Return (passages, vectorizer, sparse_matrix). Fail loudly on missing dependencies."""
    import pymupdf
    from sklearn.feature_extraction.text import TfidfVectorizer

    folder = find_paper_root(root)
    passages = []
    for source, filename in PDF_FILES.items():
        pdf = folder / filename
        if not pdf.is_file():
            print(f'WARNING: missing PDF: {pdf}')
            continue
        with pymupdf.open(str(pdf)) as doc:
            for pdf_page, page in enumerate(doc, start=1):
                words = page.get_text('text').split()
                for i in range(0, len(words), stride_words):
                    chunk = words[i:i + chunk_words]
                    if len(chunk) < 25:
                        continue
                    passages.append({
                        'source': source,
                        'filename': filename,
                        'page': pdf_page,
                        'citation': f'{source}:pdf-p{pdf_page}',
                        'text': ' '.join(chunk),
                    })
    if not passages:
        raise RuntimeError(f'Zero searchable passages extracted from {folder}; verify PDF extraction and dependencies.')
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), sublinear_tf=True)
    matrix = vectorizer.fit_transform([p['text'] for p in passages])
    return passages, vectorizer, matrix


def retrieve(question: str, index, *, top_k: int = 4):
    """Return ranked passages with unique (source, page), positive matching scores."""
    import numpy as np
    passages, vectorizer, matrix = index
    if not question or not question.strip():
        return []
    scores = (matrix @ vectorizer.transform([question]).T).toarray().ravel()
    seen = set()
    results = []
    for item in np.argsort(scores)[::-1]:
        i = int(item)
        if scores[i] <= 0:
            break
        p = passages[i]
        key = (p['source'], p['page'])
        if key in seen:
            continue
        seen.add(key)
        results.append({**p, 'score': float(scores[i])})
        if len(results) >= top_k:
            break
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='FireSafe NASA PDF retrieval smoke test')
    parser.add_argument('--papers', default=None, help='Folder containing NASA PDFs')
    parser.add_argument('--question', default='How does airflow direction affect flame spread in microgravity?')
    args = parser.parse_args()
    idx = build_index(args.papers)
    print('Indexed passages:', len(idx[0]))
    results = retrieve(args.question, idx)
    print('Retrieved pages:', len(results))
    for item in results:
        print(f"  [{item['citation']}] score={item['score']:.3f}")
    if not results:
        raise SystemExit('No matches. Try another question.')


if __name__ == '__main__':
    main()
