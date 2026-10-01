"""Similarity engine: text, token, structural (AST), semantic (TF-IDF) + explanations from real evidence."""
import ast, math, re
from collections import Counter
from difflib import SequenceMatcher
from itertools import combinations
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .normalize import process, KW
from .. import config

CTRL = ["for", "while", "if", "elif", "else", "switch", "case", "try", "return", "def"]
MATH = {"+", "-", "*", "/", "%", "**", "//"}
SKEL = {"{", "}", "(", ")", ";", "=", "==", "+", "-", "*", "/", "%", "<", ">", "<=", ">=", "&&", "||", "++", "--", "[", "]"}
_FN = re.compile(r'\b[A-Za-z_]\w*\s*\([^;{}()]*\)\s*(?:const\s*)?\{')

def risk_level(pct):
    for lo, hi, label in config.RISK_BANDS:
        if lo <= pct < hi:
            return label
    return config.RISK_BANDS[-1][2]

def seq_ratio(a, b):
    return SequenceMatcher(None, a, b, autojunk=False).ratio() if (a or b) else 0.0

def ccos(a, b):
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    na, nb = math.sqrt(sum(v * v for v in a.values())), math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0

def shingles(seq, k=config.SHINGLE_SIZE):
    return {tuple(seq[i:i + k]) for i in range(max(1, len(seq) - k + 1))} if seq else set()

def ast_sequence(code):
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None
    out, stack = [], [tree]
    while stack:
        n = stack.pop()
        name = type(n).__name__
        if name not in ("Load", "Store", "Del"):
            out.append(name)
        stack.extend(reversed(list(ast.iter_child_nodes(n))))
    return out[:1500]

def structural(pa, pb):
    if pa["language"] == "python":
        sa, sb = ast_sequence(pa["clean"]), ast_sequence(pb["clean"])
        if sa is not None and sb is not None:
            return 0.6 * seq_ratio(sa, sb) + 0.4 * ccos(Counter(sa), Counter(sb)), "Python AST"
    ka = [n for n in pa["norm"] if n in KW[pa["language"]] or n in SKEL][:1500]
    kb = [n for n in pb["norm"] if n in KW[pb["language"]] or n in SKEL][:1500]
    return 0.6 * seq_ratio(ka, kb) + 0.4 * ccos(Counter(ka), Counter(kb)), "Token skeleton (AST fallback)"

def func_count(p):
    if p["language"] == "python":
        return p["norm"].count("def")
    return sum(1 for m in _FN.finditer(p["clean"]) if m.group().split("(")[0].strip() not in {"if", "for", "while", "switch", "catch"})

def line_alignment(pa, pb):
    la, lb = [x[1] for x in pa["lines"]], [x[1] for x in pb["lines"]]
    blocks, ren, matched = [], Counter(), 0
    for m in SequenceMatcher(None, la, lb, autojunk=False).get_matching_blocks():
        if m.size == 0 or (m.size == 1 and len(la[m.a].split()) < 4):
            continue
        matched += m.size
        blocks.append({"a": [pa["lines"][m.a][0], pa["lines"][m.a + m.size - 1][0]],
                       "b": [pb["lines"][m.b][0], pb["lines"][m.b + m.size - 1][0]], "lines": m.size})
        for k in range(m.size):
            for (ka, xa), (kb, xb) in zip(pa["lines"][m.a + k][2], pb["lines"][m.b + k][2]):
                if ka == kb == "id" and xa != xb:
                    ren[(xa, xb)] += 1
    best = {}
    for (xa, xb), c in ren.items():
        if xa not in best or c > best[xa][1]:
            best[xa] = (xb, c)
    renames = sorted(({"a": a, "b": b, "count": c} for a, (b, c) in best.items()), key=lambda r: -r["count"])
    return blocks, renames, matched, min(len(la), len(lb))

def explain(pa, pb, s, blocks, renames, matched, denom):
    ex = []
    if s["structural"] >= 70:
        ex.append({"title": "Similar control-flow / AST structure",
                   "evidence": f"Structural similarity is {s['structural']}% (method: {s['method']})."})
    if len(renames) >= 2 and s["token"] - s["text"] >= 10:
        ex.append({"title": "Similar structure despite renamed variables",
                   "evidence": f"{len(renames)} identifiers renamed consistently, e.g. " +
                               ", ".join(f"{r['a']}→{r['b']}" for r in renames[:5]) +
                               f". Text similarity ({s['text']}%) is lower than token similarity ({s['token']}%)."})
    ca, cb = Counter(t for t in pa["norm"] if t in CTRL), Counter(t for t in pb["norm"] if t in CTRL)
    if sum(ca.values()) >= 3 and all(abs(ca[k] - cb[k]) <= 1 for k in CTRL) and ccos(ca, cb) >= 0.9:
        ex.append({"title": "Similar control-flow constructs",
                   "evidence": "; ".join(f"{k}: {ca[k]} vs {cb[k]}" for k in CTRL if ca[k] or cb[k])})
    fa, fb = func_count(pa), func_count(pb)
    if fa >= 2 and fa == fb:
        ex.append({"title": "Similar function organisation", "evidence": f"Both files define {fa} functions/methods."})
    if denom and matched / denom >= 0.4:
        ex.append({"title": "Similar sequence of statements",
                   "evidence": f"{matched} of {denom} lines align in the same order after normalisation ({len(blocks)} matching blocks)."})
    ma, mb = Counter(t for t in pa["norm"] if t in MATH), Counter(t for t in pb["norm"] if t in MATH)
    if sum(ma.values()) >= 3 and ccos(ma, mb) >= 0.9:
        ex.append({"title": "Similar mathematical operations",
                   "evidence": "Operators A: " + ", ".join(f"{k}×{v}" for k, v in ma.items()) +
                               " | B: " + ", ".join(f"{k}×{v}" for k, v in mb.items())})
    if not ex:
        ex.append({"title": "No strong shared patterns detected",
                   "evidence": f"Overall similarity {s['overall']}% is below the level where shared patterns were found."})
    return ex

def compare(pa, pb, sem):
    s = {"text": seq_ratio(pa["text_lines"], pb["text_lines"]) * 100}
    a, b = shingles(pa["norm"]), shingles(pb["norm"])
    s["token"] = (2 * len(a & b) / (len(a) + len(b)) * 100) if (a or b) else 0.0
    st, method = structural(pa, pb)
    s["structural"], s["semantic"] = st * 100, max(0.0, min(1.0, sem)) * 100
    s = {k: round(v, 1) for k, v in s.items()}
    s["method"] = method
    s["overall"] = round(sum(config.WEIGHTS[k] * s[k] for k in config.WEIGHTS), 1)
    blocks, renames, matched, denom = line_alignment(pa, pb)
    return {**s, "risk": risk_level(s["overall"]), "blocks": blocks, "renames": renames[:10],
            "explanations": explain(pa, pb, s, blocks, renames, matched, denom)}

def analyze_batch(items, pairs=None):
    """items: [{id, filename, code}]. pairs: optional list of (id_a, id_b); default = all same-language pairs."""
    procs = {i["id"]: process(i["code"], i["filename"]) for i in items}
    by_lang = {}
    for i, p in procs.items():
        by_lang.setdefault(p["language"], []).append(i)
    results = []
    for ids in by_lang.values():
        if len(ids) < 2:
            continue
        docs = []
        for i in ids:
            n = procs[i]["norm"]
            docs.append(" ".join(n + [f"{x}_{y}" for x, y in zip(n, n[1:])]))
        try:
            S = cosine_similarity(TfidfVectorizer(token_pattern=r"\S+", lowercase=False, sublinear_tf=True).fit_transform(docs))
        except ValueError:
            S = [[0] * len(ids) for _ in ids]
        idx = {i: k for k, i in enumerate(ids)}
        for x, y in (pairs or combinations(ids, 2)):
            if x in idx and y in idx:
                results.append({"a": x, "b": y, **compare(procs[x], procs[y], float(S[idx[x]][idx[y]]))})
    return results
