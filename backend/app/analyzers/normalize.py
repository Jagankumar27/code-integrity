"""Preprocessing: language detection, comment removal, tokenisation, identifier/literal normalisation."""
import os, re, keyword

EXT = {".py": "python", ".java": "java", ".c": "c", ".h": "c",
       ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp"}
_C = set("auto break case char const continue default do double else enum extern float for goto if int long "
         "register return short signed sizeof static struct switch typedef union unsigned void volatile while".split())
KW = {
    "python": set(keyword.kwlist),
    "java": set("abstract boolean break byte case catch char class continue default do double else enum extends "
                "final finally float for if implements import instanceof int interface long new package private "
                "protected public return short static super switch this throw throws try void while".split()),
    "c": _C,
}
KW["cpp"] = _C | set("class namespace using new delete template public private protected virtual bool true "
                     "false try catch throw this nullptr".split())
# well-known library names are kept (they carry meaning); user identifiers become ID
KEEP = set("print len range input int str float sum min max abs sorted append printf scanf println cout cin endl "
           "main System out String Math sqrt pow list dict set enumerate zip map filter".split())

def detect_language(filename):
    return EXT.get(os.path.splitext(filename.lower())[1])

_STR = r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\''
_PY_CMT = re.compile(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|' + _STR + r')|(#[^\n]*)')
_C_CMT = re.compile(r'(' + _STR + r')|(//[^\n]*|/\*[\s\S]*?\*/)')
_TOK = re.compile(r'(?P<str>"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|' + _STR + r')|(?P<num>\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)'
                  r'|(?P<id>[A-Za-z_]\w*)|(?P<op>==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|%=|//|\*\*|&&|\|\||->|::|<<|>>|[^\s\w])')

def strip_comments(code, lang):
    rx = _PY_CMT if lang == "python" else _C_CMT
    # keep newline count so line numbers stay aligned with the original file
    return rx.sub(lambda m: m.group(1) if m.group(1) else "\n" * m.group(2).count("\n"), code)

def tokenize(code):
    toks, line, pos = [], 1, 0
    for m in _TOK.finditer(code):
        line += code.count("\n", pos, m.start()); pos = m.start()
        toks.append((m.lastgroup, m.group(), line))
    return toks

def norm_token(kind, text, lang):
    if kind == "id":
        return text if (text in KW[lang] or text in KEEP) else "ID"
    return {"num": "NUM", "str": "STR"}.get(kind, text)

def process(code, filename):
    lang = detect_language(filename) or "python"
    clean = strip_comments(code.replace("\r\n", "\n"), lang)
    toks = tokenize(clean)
    norm = [norm_token(k, t, lang) for k, t, _ in toks]
    by_line = {}
    for (k, t, l), n in zip(toks, norm):
        by_line.setdefault(l, []).append((k, t, n))
    # lines: (original line number, normalised text, [(kind, raw)])
    lines = [(l, " ".join(n for _, _, n in v), [(k, t) for k, t, _ in v]) for l, v in sorted(by_line.items())]
    text_lines = [" ".join(x.split()) for x in clean.splitlines() if x.strip()]
    return {"language": lang, "clean": clean, "tokens": toks, "norm": norm, "lines": lines, "text_lines": text_lines}
