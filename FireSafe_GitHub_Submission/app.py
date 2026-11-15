"""FireSafe guided research dashboard — standalone Kaggle Gradio application.
Uses curated observations from NASA publications; no live model or risk predictions.
"""
import html
from pathlib import Path
import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt

NASA_PDF = {
 'BASS':'https://ntrs.nasa.gov/api/citations/20140011099/downloads/20140011099.pdf',
 'BASSII':'https://ntrs.nasa.gov/api/citations/20160000593/downloads/20160000593.pdf',
 'SAFFIRE':'https://ntrs.nasa.gov/api/citations/20210011521/downloads/ICES%202021-266%200503-2021%20final.pdf',
 'BRE':'https://ntrs.nasa.gov/api/citations/20160010073/downloads/20160010073.pdf',
}

# Each numeric measurement is from the user's curated NASA paper notes.
# Source provenance should also be tied to PSI investigation data before final submission.
DATA = [
 {'id':'BASS','name':'BASS','category':'Solid fuels','fuel':'Thin solids; PMMA sphere; Nomex III','oxygen':'17–21.5% reported range','oxygen_num':None,'airflow':'Wind tunnel up to 40 cm/s','geometry':'Multiple solid sample shapes','measurement':'Opposed spread peaked at intermediate speed; concurrent rate increased with flow','source':'BASS:pdf-p2, BASS:pdf-p22','page':'BASS:pdf-p22','topics':'airflow oxygen thin fuel extinction pmma nomex'},
 {'id':'BASSII','name':'BASS-II','category':'Solid fuels','fuel':'PMMA sheets','oxygen':'Varied; consult experiment records','oxygen_num':None,'airflow':'Varied; consult experiment records','geometry':'0.1–0.4 mm PMMA sheets','measurement':'22 reported test points; sheet thickness 0.1–0.4 mm','source':'BASSII:pdf-p12','page':'BASSII:pdf-p12','topics':'pmma materials sample thickness tests oxygen'},
 {'id':'IV2','name':'Saffire IV-2','category':'Thick PMMA','fuel':'Thick PMMA','oxygen':'Air (percentage not reported here)','oxygen_num':None,'airflow':'Not in curated record','geometry':'Two-sided PMMA','measurement':'Flame length 9.5 cm at reported 400 s','source':'SAFFIRE:pdf-p8, SAFFIRE:pdf-p9','page':'SAFFIRE:pdf-p8','topics':'flame length pmma oxygen growth geometry'},
 {'id':'V3','name':'Saffire V-3','category':'Thick PMMA','fuel':'Thick PMMA','oxygen':'25.4%','oxygen_num':25.4,'airflow':'Not in curated record','geometry':'One-sided PMMA','measurement':'Flame length 11 cm at reported 450 s','source':'SAFFIRE:pdf-p9','page':'SAFFIRE:pdf-p9','topics':'flame length pmma oxygen growth geometry'},
 {'id':'BRE','name':'BRE','category':'Gaseous burner','fuel':'Ethylene burner (specified test)','oxygen':'30% (specified test)','oxygen_num':30.0,'airflow':'Not in curated record','geometry':'25 mm and 50 mm burners','measurement':'Heat flux: 3 and 7 kW/m², respectively, at 0.7 atm','source':'BRE:pdf-p6','page':'BRE:pdf-p6','topics':'flame gaseous burner ethylene heat flux oxygen'},
]
RECORDS = {d['name']:d for d in DATA}
SOURCES = {
 'BASS:pdf-p2': ('BASS','2', 'Microgravity wind-tunnel experiments aboard the ISS; airflow up to 40 cm/s, ambient oxygen range 17–21.5%.'),
 'BASS:pdf-p22': ('BASS','22','Opposed flow: steady spread; fastest at an intermediate flow speed. Concurrent flow: spread rate increased linearly; quenching observed around 1 cm/s.'),
 'BASSII:pdf-p12': ('BASSII','12','BASS-II reports 22 test points and PMMA sheet samples with thicknesses 0.1–0.4 mm.'),
 'SAFFIRE:pdf-p8': ('SAFFIRE','8','Saffire IV-2 and V-3 thick-fuel concurrent flames did not spread appreciably and instead advanced through surface regression near the leading edge.'),
 'SAFFIRE:pdf-p9': ('SAFFIRE','9','Saffire IV-2 flame length: 9.5 cm after 400 seconds in air. Saffire V-3: 11 cm after 450 seconds at 25.4% oxygen.'),
 'SAFFIRE:pdf-p10': ('SAFFIRE','10','Flow characteristics strongly influence low-gravity flame spread; normal-gravity t² growth predictions should not automatically be assumed.'),
 'BRE:pdf-p6': ('BRE','6','Specified ethylene tests: 25 mm burner at 3 kW/m² and 50 mm burner at 7 kW/m², at 30% oxygen and 0.7 atm.'),
}

CSS = '''.gradio-container {max-width: 1200px !important;} .fs-note {color: #666}'''

def guide(message):
 return f'**Note:** {message}'

def details_text(d):
 url = NASA_PDF['SAFFIRE' if d['id'] in ('IV2','V3') else d['id']]
 return (f"### {d['name']} — research record\n\n"
         f"**Fuel:** {d['fuel']}  \n**Oxygen:** {d['oxygen']}  \n"
         f"**Airflow:** {d['airflow']}  \n**Geometry:** {d['geometry']}  \n"
         f"**Finding:** {d['measurement']}  \n**Page references:** `{d['source']}`  \n"
         f"[Open NASA research PDF]({url})\n\n"
         "*Descriptive evidence, not a mission-specific safety assessment.*")

def explorer(topic, search, name):
 key=(search or '').lower().strip(); topic=topic or 'All topics'
 out=[]
 for d in DATA:
  blob=' '.join(str(d[k]) for k in ('name','fuel','category','oxygen','airflow','measurement','topics')).lower()
  if key and key not in blob:continue
  if topic=='Oxygen 🫧' and 'oxygen' not in blob: continue
  if topic=='Airflow 💨' and not any(t in blob for t in ('airflow','flow')):continue
  if topic=='Flame growth 🔥' and not any(t in blob for t in ('flame','growth','spread')):continue
  if topic=='Fuel & materials 🧪' and not any(t in blob for t in ('pmma','solid','ethylene','fuel')):continue
  out.append({'Experiment':d['name'],'Fuel':d['fuel'],'Oxygen':d['oxygen'],'Airflow':d['airflow'],'Source':d['source']})
 return pd.DataFrame(out,columns=['Experiment','Fuel','Oxygen','Airflow','Source']),details_text(RECORDS[name]),guide(f"Found {len(out)} matching research records. Select an experiment to inspect its reported conditions and NASA page references.")

def oxygen_view(name):
 d=RECORDS[name]
 return (f'''<div class="fs-metric"><div class="k">{html.escape(name)} · oxygen condition</div><div class="v">{html.escape(d['oxygen'])}</div><p>🫧 Oxygen is a reported atmosphere condition—not automatically a measured fire hazard.</p></div>''',details_text(d))

def compare(a,b):
 da,db=RECORDS[a],RECORDS[b]
 rows=[('Fuel',da['fuel'],db['fuel']),('Oxygen',da['oxygen'],db['oxygen']),('Airflow',da['airflow'],db['airflow']),('Geometry',da['geometry'],db['geometry']),('Reported observation',da['measurement'],db['measurement']),('Evidence',da['source'],db['source'])]
 table=pd.DataFrame(rows,columns=['Dimension',a,b])
 if a==b: msg='You selected the same record twice. Choose another experiment to compare two conditions.'
 elif {a,b}=={'Saffire IV-2','Saffire V-3'}:msg='The reported flame lengths are 9.5 cm and 11 cm, but oxygen and PMMA geometry differ. This is NOT an oxygen-only causal experiment.'
 else: msg='Comparisons here are descriptive. Differences in fuel, oxygen, airflow, and apparatus may prevent direct numerical or causal comparisons.'
 return table,guide('Let’s check experimental conditions first. '+msg)

def rank(topic):
 topic=topic or 'Airflow 💨'
 keys={'Airflow 💨':['airflow','opposed','concurrent','flow'], 'Oxygen 🫧':['oxygen','atmosphere'], 'Flame growth 🔥':['flame','spread','length','growth'], 'Fuel & materials 🧪':['pmma','fuel','ethylene','sheet','nomex']}
 words=keys[topic]
 ranked=[]
 for d in DATA:
  blob=(d['measurement']+' '+d['topics']+' '+d['airflow']+' '+d['oxygen']).lower()
  score=sum(bool(w in blob) for w in words)
  ranked.append((score,d))
 ranked.sort(key=lambda x:(-x[0],x[1]['name']))
 result=pd.DataFrame([{'Rank':i+1,'Study':d['name'],'Matched topic terms':score,'Finding':d['measurement'],'Source':d['source']} for i,(score,d) in enumerate(ranked)])
 return result,guide('Ranking reflects topic-term relevance in these curated records, not severity, fire danger, or scientific importance. Scores are search diagnostics only.')

def evidence_view(key):
 source,pageno,summary=SOURCES[key]
 path=Path('/kaggle/input/datasets/arifengine/firesafe-ai-v3-training-data/FireSafe_AI/v3/papers') / {
 'BASS':'BASS-20140011099.pdf','BASSII':'BASSII-20160000593.pdf','SAFFIRE':'saffire_research.pdf','BRE':'BRE-20160010073.pdf'
 }[source]
 excerpt=summary
 suffix='Curated source summary (PDF not mounted).'
 if path.exists():
  try:
   import fitz
   with fitz.open(path) as pdf:
    excerpt=' '.join(pdf[int(pageno)-1].get_text('text').split())[:3000]
   suffix='Original extracted text from the indicated PDF page (may contain PDF extraction artifacts).'
  except Exception as exc:
   suffix=f'Could not read PDF page: {str(exc)[:120]}. Showing curated summary.'
 url=NASA_PDF[source]
 return (f'### [{key}]({url})\n\n**{suffix}**\n\n> '+excerpt.replace('\n','\n> ')+ '\n\n*Do not infer unreported conditions or hazard estimates from this passage.*')

def make_plot():
 fig,ax=plt.subplots(figsize=(8,3.4))
 fig.patch.set_facecolor('#FBF5EC'); ax.set_facecolor('#FFFCF7')
 xs=['Saffire IV-2','Saffire V-3']; vals=[9.5,11.0]
 bars=ax.bar(xs,vals,color=['#5B8DB8','#E8603C'],width=.48)
 ax.set_ylabel('Reported flame length (cm)');ax.set_ylim(0,13.5)
 for bar,value in zip(bars,vals):ax.text(bar.get_x()+bar.get_width()/2,value+.2,f'{value:g} cm',ha='center',fontsize=11,fontweight='bold')
 ax.spines[['top','right']].set_visible(False)
 fig.tight_layout();return fig


# Interactive Mission Control. The plots show reported quantities only, not model predictions.
QUESTIONS = {
 'How does airflow direction change flame spread?': ('BASS', 'Airflow'),
 'Which oxygen conditions appear in these studies?': ('Saffire V-3', 'Oxygen'),
 'What did Saffire observe about flame length?': ('Saffire IV-2', 'Flame growth'),
 'Which experiments used PMMA?': ('BASS-II', 'Materials'),
 'Why can’t we directly compare two flame lengths?': ('Saffire V-3', 'Comparison'),
}


def mission_start(question):
 name, subject = QUESTIONS[question]
 return name, mission_report(name, question), mission_chart(name, subject), mission_tip(name, question)


def mission_report(name, question):
 d = RECORDS[name]
 pdf = NASA_PDF['SAFFIRE' if d['id'] in ('IV2','V3') else d['id']]
 return (f'### 🔍 {name} · Your research finding\n\n'
         f'**Question:** {question}\n\n'
         f'**Fuel:** {d["fuel"]}  \n**Oxygen:** {d["oxygen"]}  \n'
         f'**Airflow:** {d["airflow"]}  \n**Test geometry:** {d["geometry"]}\n\n'
         f'**Reported NASA observation:** {d["measurement"]}\n\n'
         f'**Evidence:** `{d["source"]}` · [Open NASA publication]({pdf})\n\n'
         '*These are reported study conditions, not interactive fire predictions.*')


def mission_tip(name, question):
 if 'compare' in question.lower() or name.startswith('Saffire'):
  msg='Notice the oxygen and material geometry! Saffire IV-2 and V-3 were not controlled oxygen-only comparisons. Open Compare Experiments to investigate.'
 elif name == 'BASS':
  msg='BASS reports different airflow trends for opposed and concurrent flow. See its PDF p22. Avoid assuming one configuration is always faster.'
 elif name == 'BASS-II':
  msg='BASS-II used PMMA sheet thicknesses of 0.1–0.4 mm in 22 test points. Look at the experiment record before comparing outcomes.'
 else:
  msg='Every number depends on its experimental setup. Open NASA Evidence to check its original context.'
 return guide(msg)


def mission_chart(name, subject):
 fig, ax = plt.subplots(figsize=(8.2,3.2))
 fig.patch.set_facecolor('#FBF5EC');ax.set_facecolor('#FFFCF7')
 if subject in ('Flame growth','Comparison') or name in ('Saffire IV-2','Saffire V-3'):
  labels=['Saffire IV-2','Saffire V-3']; values=[9.5,11.0]
  colors=['#E8603C' if name==labels[0] else '#9AB2C7', '#E8603C' if name==labels[1] else '#9AB2C7']
  bars=ax.bar(labels,values,color=colors,width=.50)
  ax.set_ylim(0,13.5);ax.set_ylabel('Reported flame length (cm)')
  for b,v in zip(bars,values):ax.text(b.get_x()+b.get_width()/2,v+.2,f'{v:g} cm',ha='center')
  ax.set_title('Different test conditions: not an oxygen-only comparison',fontsize=11)
 elif name=='BASS':
  labels=['Min oxygen','Max oxygen'];values=[17.0,21.5]
  bars=ax.bar(labels,values,color=['#5B8DB8','#E8603C'],width=.45)
  ax.set_ylim(0,26);ax.set_ylabel('Reported atmospheric oxygen (%)')
  for b,v in zip(bars,values):ax.text(b.get_x()+b.get_width()/2,v+.4,f'{v:g}%',ha='center')
  ax.set_title('BASS reported oxygen range (not flame-spread rates)',fontsize=11)
 elif name=='BASS-II':
  labels=['Minimum','Maximum'];values=[0.1,0.4]
  bars=ax.bar(labels,values,color=['#5B8DB8','#E8603C'],width=.45)
  ax.set_ylim(0,.5);ax.set_ylabel('PMMA sheet thickness (mm)')
  for b,v in zip(bars,values):ax.text(b.get_x()+b.get_width()/2,v+.012,f'{v:g} mm',ha='center')
  ax.set_title('BASS-II sample thickness range',fontsize=11)
 else:
  labels=['25 mm burner','50 mm burner'];values=[3,7]
  bars=ax.bar(labels,values,color=['#5B8DB8','#E8603C'],width=.45)
  ax.set_ylim(0,9);ax.set_ylabel('Reported heat flux (kW/m²)')
  for b,v in zip(bars,values):ax.text(b.get_x()+b.get_width()/2,v+.18,f'{v:g}',ha='center')
  ax.set_title('BRE specified test: 30% O₂, 0.7 atm',fontsize=11)
 ax.spines[['top','right']].set_visible(False)
 fig.tight_layout()
 return fig


def mission_select(name, question):
 return mission_report(name,question), mission_chart(name,QUESTIONS[question][1]), mission_tip(name,question)


# Free-form, source-grounded AI question answering (Overview).
# The large language model is never silently substituted with template answers.
PAPER_ROOT = Path('/kaggle/input/datasets/arifengine/firesafe-ai-v3-training-data/FireSafe_AI/v3/papers')
PAPER_FILES = {
    'BASS': 'BASS-20140011099.pdf',
    'BASSII': 'BASSII-20160000593.pdf',
    'SAFFIRE': 'saffire_research.pdf',
    'BRE': 'BRE-20160010073.pdf',
    'ACME-BRE': 'ACME-BRE-OVERVIEW.pdf',
}
_rag_cache = None


def _notebook_value(key):
    """Find objects created in earlier Kaggle notebook cells, including %run."""
    try:
        ip = get_ipython()
        if ip is not None and key in ip.user_ns:
            return ip.user_ns[key]
    except Exception:
        pass
    return globals().get(key)


def _find_pdf_root():
    if PAPER_ROOT.exists():
        return PAPER_ROOT
    for p in Path('/kaggle/input').rglob('BASS-20140011099.pdf'):
        return p.parent
    return None


def _build_nasa_search():
    global _rag_cache
    if _rag_cache is not None:
        return _rag_cache
    root = _find_pdf_root()
    if root is None:
        _rag_cache = ([], None, None)
        return _rag_cache
    try:
        import pymupdf
        from sklearn.feature_extraction.text import TfidfVectorizer
        passages = []
        for source, filename in PAPER_FILES.items():
            file = root / filename
            if not file.exists():
                continue
            with pymupdf.open(str(file)) as doc:
                for page_idx, page in enumerate(doc):
                    words = ' '.join(page.get_text('text').split()).split()
                    for start in range(0, len(words), 155):
                        chunk = words[start:start+200]
                        if len(chunk) < 30:
                            continue
                        passages.append({
                            'citation': f'{source}:pdf-p{page_idx+1}',
                            'text': ' '.join(chunk),
                            'source': source,
                            'page': page_idx + 1,
                            'filename': filename,
                        })
        if not passages:
            _rag_cache = ([], None, None)
        else:
            vec = TfidfVectorizer(stop_words='english', ngram_range=(1,2), sublinear_tf=True)
            mat = vec.fit_transform([p['text'] for p in passages])
            _rag_cache = (passages, vec, mat)
    except ImportError as exc:
        raise RuntimeError('NASA PDF indexing dependency is missing. Install pymupdf and scikit-learn.') from exc
    if not _rag_cache[0]:
        raise RuntimeError(f'NASA PDFs were found at {root}, but no searchable text was indexed.')
    return _rag_cache


def _retrieve_nasa_for_ai(question, top_k=4):
    import numpy as np
    passages, vec, mat = _build_nasa_search()
    if not passages:
        return []
    score = (mat @ vec.transform([question]).T).toarray().ravel()
    order = np.argsort(score)[::-1]
    result, used = [], set()
    for idx in order:
        idx = int(idx)
        if score[idx] <= 0:
            break
        item = passages[idx]
        page = (item['source'], item['page'])
        if page in used:
            continue
        result.append(item)
        used.add(page)
        if len(result) >= top_k:
            break
    return result


def _ask_loaded_qwen(messages):
    """Use only an actually loaded inference function or model."""
    inference = _notebook_value('generate_firesafe')
    if callable(inference):
        return str(inference(messages, max_new_tokens=280)).strip()

    model = _notebook_value('model')
    tokenizer = _notebook_value('tokenizer')
    if model is None or tokenizer is None:
        return None
    import torch
    try:
        from unsloth import FastLanguageModel
        FastLanguageModel.for_inference(model)
    except ImportError:
        model.eval()
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    encoded = tokenizer(prompt, return_tensors='pt', add_special_tokens=False)
    device = next(model.parameters()).device
    encoded = {k: v.to(device) for k,v in encoded.items()}
    with torch.inference_mode():
        ids = model.generate(
            **encoded, max_new_tokens=280, do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(ids[0][encoded['input_ids'].shape[-1]:], skip_special_tokens=True).strip()


def answer_firesafe_question(question):
    question = (question or '').strip()
    if not question:
        return 'Enter a question about microgravity combustion or NASA experiments.', ''
    try:
        records = _retrieve_nasa_for_ai(question, top_k=4)
    except Exception as exc:
        return 'NASA retrieval failed. Check that the NASA PDF dataset is attached and that pymupdf and scikit-learn are installed.', f'Error: `{type(exc).__name__}: {exc}`'
    if not records:
        return ('NASA evidence is not available for this question. Attach the existing NASA PDF dataset to Kaggle. '
                'No AI answer was generated without source context.'), ''

    context = '\n\n'.join(f"[{r['citation']}]\n{r['text']}" for r in records)
    messages = [
        {'role':'system','content':(
            'You are FireSafe AI, a careful microgravity combustion research assistant. '
            'Answer the specific question using ONLY the NASA passages supplied below. '
            'Cite the supplied [SOURCE:pdf-pN] identifiers for every experimental claim. '
            'Clearly distinguish measured observations from experimental aims and interpretation. '
            'Never invent numbers, causal comparisons, fire-risk estimates or missing data. '
            'If the evidence does not support an answer, explicitly say what is missing. '
            'Keep the answer concise and scientifically qualified.')},
        {'role':'user','content':f'RESEARCH QUESTION:\n{question}\n\nNASA EVIDENCE:\n{context}'}
    ]

    sources = '\n\n'.join(
        f"**[{r['citation']}]** · {r['filename']} · PDF page {r['page']}\n\n> "
        + r['text'][:850].replace('\n',' ') + ('…' if len(r['text'])>850 else '')
        for r in records
    )
    try:
        answer = _ask_loaded_qwen(messages)
        if not answer:
            return (
                '**Qwen is not connected in this notebook.** The NASA evidence was retrieved successfully '
                'and appears below. Load your FireSafe Qwen adapter and tokenizer, then ask again. '
                'This app does not fabricate AI answers when the model is absent.'
            ), sources
        return answer + '\n\n*AI interpretation — scientific review pending.*', sources
    except Exception as exc:
        return (
            '**Qwen inference failed.** NASA evidence is available below. '
            'Check the model and tokenizer in the notebook before retrying. '
            f'Error: `{type(exc).__name__}: {str(exc)[:240]}`'
        ), sources



# Four-task interface: AI → Experiment → Comparison → NASA source.
# No theme redesign, mascot, prediction engine, or unsupported metric sliders.
def study_overview(name):
    d = RECORDS[name]
    source = d['source'].split(',')[0].strip()
    intro = {
      'BASS': 'How do oxygen conditions and the direction of airflow influence burning and flame spread on solid fuels in microgravity?',
      'BASS-II': 'How do thin PMMA sheet configurations and imposed airflow relate to combustion behavior?',
      'Saffire IV-2': 'How did a two-sided thick PMMA sample burn in the reported Saffire IV test?',
      'Saffire V-3': 'What flame growth was recorded for one-sided thick PMMA at the reported atmosphere?',
      'BRE': 'What burner heat-flux measurements were reported for the specified ethylene burner setups?',
    }
    return (f'### {name} — what NASA investigated\n\n'
            f'**Research focus:** {intro.get(name, "Microgravity combustion conditions.")}\n\n'
            f'**Fuel and geometry:** {d["fuel"]}; {d["geometry"]}\n\n'
            f'**Atmosphere:** {d["oxygen"]}\n\n'
            f'**Airflow:** {d["airflow"]}\n\n'
            f'**Reported finding:** {d["measurement"]}\n\n'
            f'**Evidence reference:** `{d["source"]}`\n\n'
            f'*Conditions belong to the individual study; this is not a combustion simulation.*'), source


def filter_studies(topic, keyword):
    keyword = (keyword or '').lower().strip()
    term_map = {
      'All research': None,
      'Airflow and flame spread': ['airflow', 'flow', 'spread'],
      'Oxygen and atmosphere': ['oxygen', 'atmosphere'],
      'Flame growth and extinction': ['flame', 'growth', 'extinction'],
      'Materials and fuel': ['pmma', 'fuel', 'ethylene', 'nomex'],
    }
    terms = term_map.get(topic)
    rows = []
    for d in DATA:
        blob = ' '.join(str(d[k]) for k in ('name','fuel','oxygen','airflow','measurement','topics','geometry')).lower()
        if keyword and keyword not in blob: continue
        if terms and not any(term in blob for term in terms): continue
        rows.append({'Experiment':d['name'], 'What was reported':d['measurement'], 'Evidence':d['source']})
    frame = pd.DataFrame(rows, columns=['Experiment','What was reported','Evidence'])
    if not rows:
        note = 'No curated records match your filter. Try a broader topic. This is a small prototype collection.'
        choices = gr.update(choices=list(RECORDS), value='BASS')
    else:
        note = f'{len(rows)} matching records. Select a study below to inspect what was actually measured.'
        names = [row['Experiment'] for row in rows]
        choices = gr.update(choices=names, value=names[0])
    return frame, note, choices


def source_for_study(name):
    record = RECORDS[name]
    return record['source'].split(',')[0].strip()


def compare_science(a,b):
    table, note = compare(a,b)
    if a==b:
        context = 'Select two different records to review the evidence.'
    elif {a,b} == {'Saffire IV-2','Saffire V-3'}:
        context = ('**What can be said:** each report provides a flame-length observation for its own conditions.\n\n'
                   '**What cannot be claimed:** the different lengths demonstrate an oxygen-only effect. '
                   'Sample geometry, observation time, and atmosphere differ.')
    else:
        context = ('**What can be said:** these studies report their respective test conditions and observations.\n\n'
                   '**What remains uncertain:** differences in fuel, airflow, apparatus, or units may prevent '
                   'a controlled quantitative comparison. Compare matching outcomes only when supported by the reports.')
    return table, context + '\n\n' + note


def evidence_topic_results(search):
    if not (search or '').strip():
        return 'Enter a science term, experiment name or question to search the mounted NASA papers.'
    results = _retrieve_nasa_for_ai(search, top_k=5)
    if not results:
        return '**No searchable NASA PDFs found**, or no matching source passages. Attach the NASA research dataset.'
    parts = []
    for r in results:
        key = r['citation']
        url = NASA_PDF.get(r['source'], '')
        link = f' · [Open NASA publication]({url})' if url else ''
        parts.append(f'### `{key}`{link}\n\n> {r["text"][:1050]}\n\n'
                     f'*Extracted PDF text, page {r["page"]}. Check original page formatting for context.*')
    return '\n\n---\n\n'.join(parts)


with gr.Blocks(title='FireSafe AI — NASA Research') as demo:
    gr.Markdown('''# 🔥 FireSafe AI
**NASA Microgravity Combustion Research**

Ask research questions, explore experiments, and compare conditions using NASA research evidence.''')
    with gr.Tabs():
        with gr.Tab('💬 Ask FireSafe AI'):
            gr.Markdown('''## Ask a research question
Write your own question. FireSafe retrieves supporting NASA PDF passages and uses your loaded Qwen model (load your FireSafe adapter for fine-tuned responses) to prepare an evidence-based answer.

**You can ask:** *How does airflow affect flame spread?* · *What did Saffire observe?* · *Can we compare two different tests?*''')
            q = gr.Textbox(label='Your research question', lines=3,
                           placeholder='e.g. Does more airflow always increase flame-spread rate in microgravity?')
            with gr.Row():
                example = gr.Dropdown(
                    ['How does airflow affect flame spread in microgravity?',
                     'What did Saffire IV-2 and Saffire V-3 observe?',
                     'How did the BASS experiment investigate airflow and oxygen?',
                     'Why can’t we attribute Saffire IV-2 vs V-3 differences to oxygen alone?',
                     'What are the limitations of extrapolating microgravity fire data to a spacecraft?'],
                    label='Try an example question', value=None, scale=4)
                ask = gr.Button('Ask FireSafe AI', variant='primary', scale=1)
            answer = gr.Markdown(label='Research answer')
            with gr.Accordion('Supporting NASA passages (open to verify)', open=False):
                cited = gr.Markdown()
            gr.Markdown('**Interpretation note:** Generated responses are research assistance, not certified scientific conclusions. Verify claims using the PDF evidence.')
            example.change(lambda x: x or '', [example], [q])
            ask.click(answer_firesafe_question,[q],[answer,cited])
            q.submit(answer_firesafe_question,[q],[answer,cited])
            gr.Markdown('---\\n### How to use FireSafe\\n**1. Ask** a question → **2. Explore** a relevant experiment → **3. Compare** research conditions → **Verify** the retrieved passages beneath the AI answer.')

        with gr.Tab('🔬 Explore Experiments'):
            gr.Markdown('''## What did NASA actually test?
Choose a research topic or look up a study. For each experiment, the dashboard explains the question, material, oxygen and airflow conditions, measured observations, and source.''')
            with gr.Row():
                topic = gr.Dropdown(
                    ['All research','Airflow and flame spread','Oxygen and atmosphere',
                     'Flame growth and extinction','Materials and fuel'],
                    label='Research topic', value='All research')
                keyword = gr.Textbox(label='Search for a material, measurement or study',
                                    placeholder='e.g. PMMA, BASS, 25.4%')
            listing = gr.Dataframe(value=filter_studies('All research','')[0],
                                   interactive=False, label='Matching NASA experiments')
            count = gr.Markdown('Select a record to inspect its original test conditions.')
            name = gr.Dropdown(list(RECORDS), value='BASS', label='Open experiment details')
            detail = gr.Markdown(value=study_overview('BASS')[0])
            gr.Markdown('''**Why oxygen and airflow matter:** They are experimental *conditions*, not sliders for generating fictional predictions. Compare them only alongside fuel geometry and apparatus.''')
            topic.change(filter_studies,[topic,keyword],[listing,count,name])
            keyword.change(filter_studies,[topic,keyword],[listing,count,name])
            name.change(lambda n: study_overview(n)[0],[name],[detail])

        with gr.Tab('⚖️ Compare Studies'):
            gr.Markdown('''## Do these experiments actually measure comparable things?
Choose two studies. FireSafe displays their fuel, oxygen, airflow, geometry, observations and citation labels side by side—then explains limitations.''')
            with gr.Row():
                study_a=gr.Dropdown(list(RECORDS),value='Saffire IV-2',label='Study A')
                study_b=gr.Dropdown(list(RECORDS),value='Saffire V-3',label='Study B')
            compare_btn=gr.Button('Compare study conditions',variant='primary')
            cmp_table=gr.Dataframe(value=compare_science('Saffire IV-2','Saffire V-3')[0],
                                   interactive=False,label='Side-by-side experimental conditions')
            cmp_note=gr.Markdown(value=compare_science('Saffire IV-2','Saffire V-3')[1])
            compare_btn.click(compare_science,[study_a,study_b],[cmp_table,cmp_note])
            study_a.change(compare_science,[study_a,study_b],[cmp_table,cmp_note])
            study_b.change(compare_science,[study_a,study_b],[cmp_table,cmp_note])
            gr.Markdown('''**Example:** Saffire IV-2 and V-3 reported 9.5 cm at 400 s and 11 cm at 450 s, respectively. Their geometries and atmospheres differ; the graph alone cannot isolate the effect of oxygen.''')

        with gr.Tab('📄 Research Evidence', visible=False):
            gr.Markdown('''## Read the original NASA evidence
Use this page to audit scientific claims instead of relying on an AI answer or a chart alone.''')
            search_pdf=gr.Textbox(label='Search all attached NASA PDFs',
                                  placeholder='e.g. opposed airflow flame spread; Saffire PMMA oxygen')
            search_btn=gr.Button('Find matching passages',variant='primary')
            passages=gr.Markdown()
            search_btn.click(evidence_topic_results,[search_pdf],[passages])
            search_pdf.submit(evidence_topic_results,[search_pdf],[passages])
            gr.Markdown('---\\n### Inspect a specific cited page')
            key=gr.Dropdown(list(SOURCES),value='BASS:pdf-p22',label='NASA document and PDF page')
            excerpt=gr.Markdown(value=evidence_view('BASS:pdf-p22'))
            key.change(evidence_view,[key],[excerpt])
    gr.Markdown('---\\n*FireSafe is a research prototype based on selected NASA publications. No predictive flame simulation or fire-safety certification is performed. Experimental measurements require their original conditions and sources.*')

if __name__ == '__main__':
    demo.queue().launch(server_name='0.0.0.0', server_port=None, share=True, inline=False, css=CSS)
