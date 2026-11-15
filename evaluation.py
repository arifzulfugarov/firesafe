"""Smoke tests for FireSafe's PDF retrieval (NOT a model-quality benchmark).

Run: python evaluation.py --papers /path/to/papers
"""
import argparse
from retrieval import build_index, retrieve

QUESTIONS = [
    'How does airflow affect flame spread in microgravity?',
    'What oxygen concentration was used in the Saffire V-3 test?',
    'What did BASS-II report for PMMA sheet samples?',
    'What heat flux did the BRE burner tests report?',
]


def run(papers=None):
    index = build_index(papers)
    print(f'PASS: indexed {len(index[0])} source passages')
    count = 0
    for question in QUESTIONS:
        found = retrieve(question, index, top_k=4)
        status = 'PASS' if found else 'FAIL'
        print(f'{status}: {question}')
        print('  citations:', ', '.join(x['citation'] for x in found) or '(none)')
        count += bool(found)
    print(f'Retrieval smoke-test coverage: {count}/{len(QUESTIONS)}')
    if count != len(QUESTIONS):
        raise SystemExit(1)
    print('NOTE: This checks retrieval only. It does not validate Qwen answers or citation entailment.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--papers', default=None)
    args = parser.parse_args()
    run(args.papers)
