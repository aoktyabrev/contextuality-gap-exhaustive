#!/usr/bin/env python3
r"""Typeset papers/paper_A_contextuality_gaps.md as a PDF for a human reader.

    .venv/bin/python scripts/build_paper_pdf.py            # -> papers/<name>.pdf

Written rather than pandoc'd because the document has three properties a generic
converter gets wrong, and each of them is load-bearing here:

  1. The internal source annotations `[src: ...]` are for our own verification and must
     come OUT, without leaving dangling punctuation, orphaned colons, or a paragraph
     glued to the display formula that preceded it.
  2. The evidence tags [proved] / [measured] / [observed] are part of the TEXT and must
     stay, in every position including inside table cells.
  3. graph6 codes contain ` ? @ { } [ ] \ ~ _ ^ -- characters that both LaTeX and a
     line-breaker want to touch.  They are set in an unbreakable monospace box so that
     they cannot be hyphenated, re-wrapped, or silently mangled.

Mathematics is mapped character by character onto real LaTeX math (\\vartheta, \\succeq,
\\mathbb{Q}, super/subscript runs), so formulas set as formulas rather than as literal
Unicode in a text font.
"""
import sys, os, re, subprocess, shutil, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "papers", "paper_A_contextuality_gaps.md")

# ---------------------------------------------------------------- 1. strip [src: ...]

def strip_src(s):
    """Remove the internal annotations and heal the punctuation around them."""
    # the sentence in the reading conventions that describes them
    s = re.sub(r"\s*Internal source annotations `\[src: file\]` point at the repos\w*\s*"
               r">?\s*(file that\s*>?\s*)?holds the number\.", "", s)
    # a span that OPENS a paragraph: keep the paragraph break, drop the span
    s = re.sub(r"(\n\n)`\[src:.*?\]`[ \t]*", r"\1", s, flags=re.S)
    # a span at the end of / inside a line: drop it and the whitespace before it
    s = re.sub(r"[ \t\n]*`\[src:.*?\]`", "", s, flags=re.S)
    # heal
    s = re.sub(r"[ \t]+([.,;:)])", r"\1", s)
    s = re.sub(r"\(\s*\)", "", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\n[ \t]+\n", "\n\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)

    # A span that carried the punctuation of the sentence it closed leaves the NEXT
    # paragraph opening on a comma or a full stop.  Drop that orphan and restart the
    # sentence properly; a paragraph that is nothing but punctuation goes entirely.
    out = []
    for para in s.split("\n\n"):
        t = para.strip("\n")
        st = t.strip()
        if st and all(c in ".,;:) " for c in st):
            continue
        m = re.match(r"^([ \t]*)([.,;:]+)\s+(.*)$", t, flags=re.S)
        if m and not t.lstrip().startswith(("|", ">", "#", "-")):
            rest = m.group(3)
            k = 0
            while k < len(rest) and rest[k] in "*_`":
                k += 1
            if k < len(rest) and rest[k].islower():
                rest = rest[:k] + rest[k].upper() + rest[k + 1:]
            t = rest
        out.append(t)
    s = "\n\n".join(out)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s

# ---------------------------------------------------------------- 2. inline conversion

GREEK = {"ϑ": r"\vartheta", "α": r"\alpha", "Δ": r"\Delta", "χ": r"\chi", "ρ": r"\rho",
         "δ": r"\delta", "τ": r"\tau", "λ": r"\lambda", "η": r"\eta", "π": r"\pi",
         "θ": r"\theta", "ζ": r"\zeta", "Σ": r"\Sigma", "µ": r"\mu"}
OPS = {"≤": r"\leq", "≥": r"\geq", "≈": r"\approx", "≫": r"\gg", "∈": r"\in",
       "⪰": r"\succeq", "×": r"\times", "−": "-", "·": r"\cdot", "→": r"\to",
       "ℚ": r"\mathbb{Q}", "✓": r"\checkmark", "Ḡ": r"\bar{G}", "½": r"\tfrac{1}{2}",
       "ᵀ": r"^{\mathsf{T}}"}
SUP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
       "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-"}
SUB = {"₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6", "₇": "7", "₉": "9"}

TEXT_ONLY = {"—": "---", "–": "--", "…": r"\dots{}", "§": r"\S{}", "†": r"\dag{}",
             "√": r"\ensuremath{\surd}"}

def esc(t):
    """Escape LaTeX specials in plain running text."""
    t = t.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
                 ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        t = t.replace(a, b)
    return t

def mono(code):
    """Monospace.  A graph6 code is boxed so it can never break; a path or URL, which
    would otherwise run into the margin, is allowed to break after / and . only."""
    breakable = ("/" in code or code.count(".") > 1) and len(code) > 16
    c = code.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
                 ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        c = c.replace(a, b)
    if breakable:
        c = c.replace("/", "/\\hspace{0pt}").replace(".", ".\\hspace{0pt}")
        return r"\texttt{" + c + "}"
    return r"\mbox{\texttt{" + c + "}}"

def mathify(t):
    """Unicode mathematics -> real LaTeX math, run by run."""
    # superscript / subscript runs first, so they attach to what precedes them
    t = re.sub("([" + "".join(SUP) + "]+)",
               lambda m: r"\ensuremath{^{" + "".join(SUP[c] for c in m.group(1)) + "}}", t)
    t = re.sub("([" + "".join(SUB) + "]+)",
               lambda m: r"\ensuremath{_{" + "".join(SUB[c] for c in m.group(1)) + "}}", t)
    t = re.sub(r"√\s*(\d+)", lambda m: r"\ensuremath{\sqrt{" + m.group(1) + "}}", t)
    for ch, mac in list(GREEK.items()) + list(OPS.items()):
        t = t.replace(ch, r"\ensuremath{" + mac + "}")
    for ch, rep in TEXT_ONLY.items():
        t = t.replace(ch, rep)
    return t

def inline(t):
    """Markdown inline -> LaTeX.  Code spans are protected from every other rule."""
    out, i, held = [], 0, []
    def stash(x):
        held.append(x)
        return "\x00%d\x00" % (len(held) - 1)
    # `` code `` (used for graph6) then ` code `
    t = re.sub(r"``\s*(.+?)\s*``", lambda m: stash(mono(m.group(1))), t, flags=re.S)
    t = re.sub(r"`([^`]+?)`", lambda m: stash(mono(m.group(1))), t, flags=re.S)
    # Sub/superscripts written in the source as X_y, X_{...} or X^{...} are mathematics,
    # not literal underscores and braces -- and a letter carrying a COMBINING MACRON
    # (K + U+0304, the complement of a complete graph) must become \bar{K}, or the bar
    # is silently dropped.  Both reached the first PDFs: K̄_{k−1} printed as "K_{k−1}".
    def _sub(m):
        base = GREEK.get(m.group(1), m.group(1))
        if m.group(2):                       # combining macron on the base
            base = r"\bar{" + base + "}"
        body = m.group(4)
        if body.startswith("{"):
            body = body[1:-1]
        for ch, mac in list(GREEK.items()) + list(OPS.items()):
            body = body.replace(ch, mac + " " if mac.startswith("\\") else mac)
        body = body.strip()
        if body in ROMAN_SUBS:
            body = r"\mathrm{" + body + "}"
        return stash(r"\ensuremath{" + base + m.group(3) + "{" + body + "}}")

    t = re.sub(r"([A-Za-z\u0391-\u03a9\u03b1-\u03c9\u03d1])(\u0304?)"
               r"([_^])(\{[^{}]{1,24}\}|[A-Za-z0-9]{1,6})(?![A-Za-z0-9])", _sub, t)
    # a bar with no subscript after it
    t = re.sub(r"([A-Za-z\u0391-\u03a9\u03b1-\u03c9\u03d1])\u0304",
               lambda m: stash(r"\ensuremath{\bar{"
                               + GREEK.get(m.group(1), m.group(1)) + "}}"), t)
    # markdown escapes: \* and \| are a literal asterisk and bar, not a backslash
    ESCAPED = {"*": "\x01", "|": "\x02", "_": "\x03", "[": "\x04", "]": "\x05"}
    for ch, tok in ESCAPED.items():
        t = t.replace("\\" + ch, tok)
    t = esc(t)
    t = mathify(t)
    # emphasis after escaping, so ** survives esc() untouched
    t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t, flags=re.S)
    t = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"\\emph{\1}", t)
    # markdown links
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1", t)
    # restore after emphasis, so a literal * is never read as markup
    for ch, tok in [("*", "\x01"), ("|", "\x02"), ("_", "\x03"),
                    ("[", "\x04"), ("]", "\x05")]:
        t = t.replace(tok, {"*": r"\textasteriskcentered{}", "|": r"\textbar{}",
                            "_": r"\_", "[": "[", "]": "]"}[ch])
    t = re.sub(r"\x00(\d+)\x00", lambda m: held[int(m.group(1))], t)
    return t

# ---------------------------------------------------------------- 3. block conversion

def is_formula(lines):
    """A blockquote that is a display formula, not a quotation."""
    if len(lines) != 1:
        return False
    l = lines[0]
    return (len(l) < 120 and re.search(r"[=≤≥∈]", l)
            and re.search(r"[ϑαΔχ]|\bmax\b|\bmin\b", l))

# Width is measured in ems, not characters: in this font a digit is a quarter wider
# than a lowercase letter, and the series table is mostly digits.  Using a flat
# character count under-measures exactly the columns that overflowed.
EM_PER_LINE = 57.0            # text block / font size at \scriptsize
BUDGET = EM_PER_LINE

ROMAN_SUBS = {"max", "min"}   # operator names set upright, unlike index letters

_W_DIGIT, _W_UPPER, _W_LOWER, _W_SPACE, _W_PUNCT = 0.64, 0.68, 0.50, 0.28, 0.32

def _width_em(text):
    t = re.sub(r"[*`]", "", text)
    w = 0.0
    for ch in t:
        if ch.isdigit():
            w += _W_DIGIT
        elif ch.isupper():
            w += _W_UPPER
        elif ch == " ":
            w += _W_SPACE
        elif ch.isalpha():
            w += _W_LOWER
        else:
            w += _W_PUNCT
    return w

def _visual_len(cell):
    return _width_em(cell)

def col_spec(rows, align):
    """Plain l/r/c while the table fits; proportional p{} columns once it does not,
    so that a wide table is narrowed instead of running into the margin."""
    ncol = len(align)
    widest = [max((_visual_len(r[c]) for r in rows), default=1) for c in range(ncol)]
    if sum(widest) + 2 * ncol <= BUDGET and max(widest) <= 40:
        return "".join({"r": "r", "c": "c"}.get(a, "l") for a in align), False
    # Every column becomes a p{} box, so the total width is fixed by construction and
    # cannot depend on how wide LaTeX decides some cell is.  Each column gets a share
    # proportional to its content, but never less than its longest unbreakable token --
    # otherwise a graph6 code or a header word would stick out of its own column.
    def longest_token(c):
        """The widest thing in the column that cannot be broken across lines."""
        toks = []
        for r in rows:
            toks += re.sub(r"[*`]", "", r[c]).split()
        return max((_width_em(t) for t in toks), default=1.0) * 1.06   # + a little air

    BUDGET_F = 0.93                       # of \linewidth, leaving room for tabcolsep
    floor = [longest_token(c) for c in range(ncol)]
    tot_floor = sum(floor)
    if tot_floor >= BUDGET * 0.95:        # even the floors do not fit: scale them down
        fr = [BUDGET_F * f / tot_floor for f in floor]
    else:
        fr = [BUDGET_F * w / sum(widest) for w in widest]
        for _ in range(4):                # lift any column below its floor, rescale rest
            need = [max(0.0, BUDGET_F * floor[c] / BUDGET - fr[c]) for c in range(ncol)]
            if not any(n > 1e-4 for n in need):
                break
            slack = sum(fr[c] for c in range(ncol) if need[c] <= 1e-4)
            take = sum(need)
            if slack <= take:
                break
            for c in range(ncol):
                fr[c] = (BUDGET_F * floor[c] / BUDGET) if need[c] > 1e-4 else \
                        fr[c] * (slack - take) / slack
    spec = []
    for c in range(ncol):
        pre = {"r": "\\raggedleft", "c": "\\centering"}.get(align[c], "\\raggedright")
        spec.append(">{%s\\arraybackslash}p{%.4f\\linewidth}" % (pre, max(fr[c], 0.022)))
    return "".join(spec), True

def table(block):
    # split on unescaped bars only: a cell may legitimately contain \| (as in |Aut|)
    rows = [[c.strip() for c in re.split(r"(?<!\\)\|",
                                         re.sub(r"^\||\|\s*$", "", l.strip()))]
            for l in block]
    sep = rows[1]
    align = ["r" if s.endswith(":") and not s.startswith(":") else
             "c" if s.startswith(":") and s.endswith(":") else "l" for s in sep]
    head, body = rows[0], rows[2:]
    ncol = len(align)
    fix = lambda r: (r + [""] * ncol)[:ncol]
    spec, narrowed = col_spec([head] + body, align)
    size = r"\scriptsize" if narrowed else r"\footnotesize"
    hdr = " & ".join(r"\textbf{%s}" % inline(c) for c in fix(head)) + r" \\"
    rows_tex = [" & ".join(inline(c) for c in fix(r)) + r" \\" for r in body]

    # A table longer than a page must break, or it runs off the bottom and over the
    # folio -- which is what the appendix table did.  longtable repeats the header.
    if len(body) > 16:
        return ["{" + size + r"\setlength{\tabcolsep}{3pt}",
                r"\begin{longtable}{" + spec + "}",
                r"\toprule", hdr, r"\midrule", r"\endfirsthead",
                r"\toprule", hdr, r"\midrule", r"\endhead",
                r"\bottomrule", r"\endlastfoot"] + rows_tex + [r"\end{longtable}}"]

    o = [r"\begin{center}" + size + r"\setlength{\tabcolsep}{3pt}",
         r"\begin{tabular}{" + spec + "}", r"\toprule", hdr, r"\midrule"]
    o += rows_tex
    o += [r"\bottomrule", r"\end{tabular}", r"\end{center}"]
    return o

def convert(md):
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1
            continue
        if re.match(r"^---+\s*$", l):
            i += 1
            continue
        m = re.match(r"^(#{2,4})\s+(.*)$", l)
        if m:
            lvl = len(m.group(1))
            body = m.group(2).strip()
            # "### 1.2 Title" -> a numbered section whose number is the document's own
            num = re.match(r"^([\d.]+)\s+(.*)$", body)
            cmd = {2: "section", 3: "subsection", 4: "subsubsection"}[lvl]
            if num:
                out.append(r"\%s*{\texorpdfstring{%s\quad %s}{%s %s}}"
                           % (cmd, num.group(1), inline(num.group(2)),
                              num.group(1), re.sub(r"[*`]", "", num.group(2))))
                out.append(r"\addcontentsline{toc}{%s}{%s\quad %s}"
                           % (cmd, num.group(1), re.sub(r"[*`]", "", num.group(2))))
                out.append(r"\label{sec:%s}" % num.group(1))
            else:
                out.append(r"\%s*{%s}" % (cmd, inline(body)))
                out.append(r"\addcontentsline{toc}{%s}{%s}" % (cmd, re.sub(r"[*`]", "", body)))
            i += 1
            continue
        if l.lstrip().startswith("|") and i + 1 < len(lines) and re.match(
                r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            blk = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                blk.append(lines[i]); i += 1
            out += table(blk)
            continue
        if l.lstrip().startswith(">"):
            blk = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                blk.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            paras, cur = [], []
            for b in blk:
                if b.strip():
                    cur.append(b)
                elif cur:
                    paras.append(cur); cur = []
            if cur:
                paras.append(cur)
            if len(paras) == 1 and is_formula([" ".join(paras[0])]):
                out.append(r"\begin{center}\itshape " + inline(" ".join(paras[0])) + r"\end{center}")
            else:
                out.append(r"\begin{quotesec}")
                for p in paras:
                    out.append(inline(" ".join(p)))
                    out.append("")
                out.append(r"\end{quotesec}")
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", l):
            ordered = bool(re.match(r"^\s*\d+\.\s+", l))
            env = "enumerate" if ordered else "itemize"
            out.append(r"\begin{%s}\setlength{\itemsep}{2pt}" % env)
            while i < len(lines):
                mm = re.match(r"^\s*(?:[-*]|\d+\.)\s+(.*)$", lines[i])
                if not mm:
                    if lines[i].strip() and lines[i].startswith((" ", "\t")):
                        out.append(inline(lines[i].strip())); i += 1; continue
                    break
                item = [mm.group(1)]; i += 1
                while (i < len(lines) and lines[i].strip()
                       and not re.match(r"^\s*(?:[-*]|\d+\.)\s+", lines[i])
                       and not lines[i].lstrip().startswith(("|", ">", "#"))):
                    item.append(lines[i].strip()); i += 1
                out.append(r"\item " + inline(" ".join(item)))
                while i < len(lines) and not lines[i].strip():
                    nxt = i + 1
                    if nxt < len(lines) and re.match(r"^\s*(?:[-*]|\d+\.)\s+", lines[nxt]):
                        i += 1
                    else:
                        break
            out.append(r"\end{%s}" % env)
            continue
        para = []
        while (i < len(lines) and lines[i].strip()
               and not lines[i].lstrip().startswith(("|", ">", "#"))
               and not re.match(r"^\s*(?:[-*]|\d+\.)\s+", lines[i])
               and not re.match(r"^---+\s*$", lines[i])):
            para.append(lines[i]); i += 1
        if para:
            out.append(inline(" ".join(para)))
            out.append("")
    return "\n".join(out)

def check_emphasis(md):
    """Fail the build on markdown emphasis that straddles a block boundary.

    THE BUG THIS CATCHES, named so the check is not vacuous: a **bold** pair whose
    opening marker is on a blockquote line and whose closing marker is on the plain
    paragraph after it.  Each block is converted separately, so neither half ever
    matches the emphasis regex and the asterisks are printed as literal characters.
    Document-wide the count of "**" is still EVEN, so a parity check over the whole
    file sees nothing -- this happened, in section 1.2, and reached both PDFs.
    """
    lines = md.split("\n")

    def kindof(l):
        st = l.lstrip()
        if not st:
            return None
        if st.startswith(">"):
            return "quote"
        if st.startswith("|"):
            return "table"
        if st.startswith("#"):
            return "head"
        if re.match(r"^\s*([-*]|\d+\.)\s", l):
            return "list"
        return "para"

    blocks, cur, kind = [], [], None
    for i, l in enumerate(lines):
        k = kindof(l)
        if k is None:
            if cur:
                blocks.append((kind, cur))
            cur, kind = [], None
            continue
        if kind is None:
            kind = k
        if k != kind and not (kind == "list" and k == "para"):
            blocks.append((kind, cur))
            cur, kind = [], k
        cur.append((i + 1, l))
    if cur:
        blocks.append((kind, cur))

    bad = []
    for k, blk in blocks:
        txt = " ".join(re.sub(r"^\s*>\s?", "", l) for _, l in blk)
        if txt.count("**") % 2:
            bad.append((blk[0][0], blk[-1][0], txt[:120]))
    if bad:
        for a, b, t in bad:
            print("UNBALANCED ** across a block boundary, lines %d-%d:\n    %s" % (a, b, t),
                  file=sys.stderr)
        raise SystemExit("emphasis would print as literal asterisks; fix the source")


# ---------------------------------------------------------------- 3a. editions

# Two copies go out and they are NOT interchangeable.  Anything addressed to a
# particular reader belongs in the authors' copy and must not reach a journal; the
# differences are spelled out here rather than hidden behind a flag, so that they can
# be audited by reading this list.
# The offer of joint authorship that used to live in section 3.3 was made in
# correspondence, was answered by both authors on 2026-09-04 (separate papers, confirmed
# by the lead author), and is therefore gone from the source itself.  Section 3.3 is now
# one paragraph in both editions and no text edit distinguishes them -- the editions
# differ only in the title block, which DATE_LINE below supplies.
JOURNAL_EDITS = []

DATE_LINE = {
    "authors": ("Draft of 4 September 2026" + chr(92)*2 + "[2pt]"
                + chr(92) + "small Prepared for the authors of arXiv:2605.12828 "
                "ahead of submission"),
    "journal": "4 September 2026",
}

OUT_NAME = {
    "authors": "Oktiabrev_theta_alpha_gaps_n11_FOR-AUTHORS_draft.pdf",
    "journal": "Oktiabrev_theta_alpha_gaps_n11_FOR-EJC_submission.pdf",
}


def apply_edition(body, edition):
    if edition == "authors":
        return body
    for old_t, new_t in JOURNAL_EDITS:
        if old_t not in body:
            raise SystemExit("edition edit did not match; the source moved:\n" + old_t[:90])
        body = body.replace(old_t, new_t)
    return body


# ---------------------------------------------------------------- 4. driver

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\usepackage{amsmath,amssymb}
\usepackage[margin=25mm]{geometry}
\usepackage{array,booktabs,longtable}
\usepackage[protrusion=true,expansion=false]{microtype}
\usepackage[dvipsnames]{xcolor}
\usepackage[hidelinks,bookmarks=true]{hyperref}
\setmainfont{DejaVu Serif}[Scale=0.92, Ligatures=TeX]
\setmonofont{DejaVu Sans Mono}[Scale=0.82]
\newenvironment{quotesec}
  {\begin{list}{}{\setlength{\leftmargin}{1.6em}\setlength{\rightmargin}{1.2em}%
   \setlength{\topsep}{4pt}}\item[]\small}
  {\end{list}}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt plus 1pt}
\sloppy
\hyphenpenalty=1000
\title{@TITLE@}
\author{@AUTHOR@}
\date{@DATE@}
\begin{document}
\maketitle
\thispagestyle{plain}
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=None)
    ap.add_argument("--keep-tex", action="store_true")
    ap.add_argument("--edition", choices=("authors", "journal"),
                    default="authors")
    a = ap.parse_args()

    raw = open(a.src, encoding="utf-8").read()
    fm = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
    meta, body = {}, raw
    if fm:
        for line in fm.group(1).split("\n"):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"')
        body = raw[fm.end():]

    check_emphasis(body)
    body = apply_edition(body, a.edition)
    body = strip_src(body)
    assert "[src:" not in body, "an internal annotation survived stripping"

    head = (PREAMBLE
            .replace("@TITLE@", inline(meta.get("title", "Untitled")))
            .replace("@AUTHOR@", inline(meta.get("author", "")))
            .replace("@DATE@", DATE_LINE[a.edition]))
    tex = head + convert(body) + "\n\\end{document}\n"

    out_pdf = a.out or os.path.join(ROOT, "papers", OUT_NAME[a.edition])
    work = os.path.join(ROOT, "papers", ".texbuild")
    os.makedirs(work, exist_ok=True)
    stem = os.path.splitext(os.path.basename(out_pdf))[0]
    texf = os.path.join(work, stem + ".tex")
    open(texf, "w", encoding="utf-8").write(tex)

    for _ in range(3):                      # 3 passes: refs and bookmarks settle
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                            os.path.basename(texf)],
                           cwd=work, capture_output=True, text=True)
    if r.returncode != 0:
        tail = r.stdout[-4000:]
        print(tail)
        print("BUILD FAILED", file=sys.stderr)
        return 1
    shutil.copy(os.path.join(work, stem + ".pdf"), out_pdf)
    print("wrote", out_pdf)
    if a.keep_tex:
        print("tex kept at", texf)
    return 0

if __name__ == "__main__":
    sys.exit(main())
