#!/usr/bin/env python3
"""Build the TimeSeries Path content bundle.

Usage:  python tools/build.py [--include-samples] [--skip-judge] [--strict]

Reads  content/  (stages, glossary, lessons, quizzes, cards, drills, problems, mock sets)
Writes site/data/content.js  (window.TSP_CONTENT = {...})  and site/engine/harness.py

Special fenced blocks in lesson.md (check, chart, widget, notebook, python) are replaced by
placeholders that the browser hydrates (see site/js/md.js). Everything else is rendered with
python-markdown. See docs/CONTENT_GUIDE.md for the formats.
"""
import argparse
import datetime
import html
import json
import os
import re
import shutil
import sys

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
# TSP_CONTENT lets tests build a different content folder (default: ./content).
CONTENT = os.environ.get("TSP_CONTENT") or os.path.join(ROOT, "content")
SITE = os.path.join(ROOT, "site")

SPECIAL = ("check", "chart", "widget", "notebook", "python")
WIDGETS = ["components", "moving-average", "ses-alpha", "holt-winters", "differencing", "acf",
           "train-test-split", "walk-forward", "lag-features", "quantile-loss", "anomaly-zscore",
           "chronos-tokens", "sliding-window", "conformal"]
GENERATORS = ["trend", "season", "noise", "randomWalk", "ar1", "step", "spike", "exp", "const"]
QTYPES = ["single", "multi", "numeric", "order"]
DIFFICULTIES = ["Easy", "Medium", "Hard"]
PTYPES = ["function", "class", "sql", "forecast"]
LEVELS = ["beginner", "intermediate", "advanced", "staff"]

# Required lesson sections, in order. Anything between "Why it matters" and "Worked example"
# is a concept chunk (at least one).
TAIL = ["Worked example", "Common mistakes", "Interview lens", "Real world"]


class Log:
    """Collects errors and warnings per context so the summary can group them."""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.by_stage = {}

    def err(self, where, msg, stage=None):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg, stage=None):
        self.warnings.append(f"{where}: {msg}")
        if stage:
            self.by_stage[stage] = self.by_stage.get(stage, 0) + 1


LOG = Log()


# ---------------------------------------------------------------- small helpers
def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_json(path, default=None):
    if not os.path.exists(path):
        return default
    try:
        return json.loads(read(path))
    except json.JSONDecodeError as e:
        LOG.err(rel(path), f"invalid JSON: {e}")
        return default


def rel(path):
    return os.path.relpath(path, ROOT)


def split_list(inner):
    """Split 'a, b, "c, d"' on commas that are not inside quotes."""
    out, cur, q = [], "", None
    for ch in inner:
        if q:
            if ch == q:
                q = None
            else:
                cur += ch
        elif ch in "\"'":
            q = ch
        elif ch == ",":
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip() or out:
        out.append(cur.strip())
    return [x for x in out if x != ""]


def strip_comment(v):
    """Remove a trailing ' # comment' that is outside quotes."""
    q = None
    for i, ch in enumerate(v):
        if q:
            if ch == q:
                q = None
        elif ch in "\"'":
            q = ch
        elif ch == "#" and (i == 0 or v[i - 1] in " \t"):
            return v[:i].rstrip()
    return v


def parse_front_matter(text, where):
    """Return (meta dict, body). Format: --- key: value lines ---"""
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        LOG.err(where, "missing front matter (--- … ---)")
        return {}, text
    meta, i = {}, 1
    while i < len(lines) and lines[i].strip() != "---":
        ln = lines[i]
        if ln.strip() and not ln.lstrip().startswith("#"):
            m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", ln)
            if m:
                k, v = m.group(1), strip_comment(m.group(2).strip())
                if v.startswith("[") and v.endswith("]"):
                    meta[k] = split_list(v[1:-1])
                else:
                    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                        v = v[1:-1]
                    meta[k] = v
            else:
                LOG.warn(where, f"front matter line not understood: {ln!r}")
        i += 1
    if i >= len(lines):
        LOG.err(where, "front matter is not closed with ---")
        return meta, ""
    return meta, "\n".join(lines[i + 1:])


def as_list(v):
    if v is None or v == "":
        return []
    return v if isinstance(v, list) else [v]


# ---------------------------------------------------------------- markdown pipeline
class Renderer:
    """Markdown → HTML with placeholders for special blocks and [[links]]."""

    FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([\w+-]*)\s*$")

    def __init__(self, glossary, lessons_by_id, problems_by_slug):
        self.glossary = glossary
        self.lessons = lessons_by_id
        self.problems = problems_by_slug
        self.missing_terms = {}
        self.md = markdown.Markdown(extensions=["tables", "fenced_code"], output_format="html")

    # -- fenced block extraction -------------------------------------------------
    def extract_blocks(self, text, where):
        """Replace special fences with tokens; keep other lines untouched."""
        out, blocks = [], []
        lines = text.replace("\r\n", "\n").split("\n")
        i = 0
        while i < len(lines):
            m = self.FENCE.match(lines[i])
            if not m:
                out.append(lines[i])
                i += 1
                continue
            fence, lang = m.group(2), m.group(3).lower()
            j = i + 1
            body = []
            while j < len(lines):
                c = self.FENCE.match(lines[j])
                if c and c.group(2)[0] == fence[0] and len(c.group(2)) >= len(fence) and not c.group(3):
                    break
                body.append(lines[j])
                j += 1
            if j >= len(lines):
                LOG.err(where, f"unclosed code fence starting at line {i + 1}")
            if lang in SPECIAL:
                token = f"TSPBLOCK{len(blocks)}TSP"
                blocks.append((lang, "\n".join(body), i + 1))
                out += ["", token, ""]
            else:
                out += lines[i:j + 1]
            i = j + 1
        return "\n".join(out), blocks

    def block_html(self, lang, code, line, where):
        if lang == "python":
            return f'<pre class="tsp-code" data-lang="python">{html.escape(code.rstrip())}</pre>'
        if lang == "notebook":
            return f'<pre class="tsp-code" data-lang="notebook">{html.escape(code.rstrip())}</pre>'
        try:
            spec = json.loads(code)
        except json.JSONDecodeError as e:
            LOG.err(where, f"invalid JSON in ```{lang} block at line {line}: {e}")
            return f'<div class="tsp-error">Broken {lang} block</div>'
        ctx = f"{where} ({lang} block, line {line})"
        if lang == "check":
            validate_question(spec, ctx)
        elif lang == "chart":
            validate_chart(spec, ctx)
        elif lang == "widget":
            if spec.get("name") not in WIDGETS:
                LOG.err(ctx, f"unknown widget {spec.get('name')!r}")
        data = html.escape(json.dumps(spec, ensure_ascii=False, separators=(",", ":")), quote=True)
        return f'<div class="tsp-{lang}" data-spec="{data}"></div>'

    # -- inline [[…]] links ---------------------------------------------------------
    LINK = re.compile(r"\[\[([^\[\]]+?)\]\]")
    CODE_SPAN = re.compile(r"(`+)(.+?)\1", re.S)

    def protect_links(self, text):
        """Replace [[x]] outside code with tokens so markdown cannot mangle them."""
        links = []
        fence_open = None
        out = []
        for ln in text.split("\n"):
            m = self.FENCE.match(ln)
            if m:
                if fence_open is None:
                    fence_open = m.group(2)
                elif m.group(2)[0] == fence_open[0] and len(m.group(2)) >= len(fence_open) and not m.group(3):
                    fence_open = None
                out.append(ln)
                continue
            if fence_open is not None:
                out.append(ln)
                continue
            parts, last = [], 0
            for cm in self.CODE_SPAN.finditer(ln):
                parts.append(self._tok(ln[last:cm.start()], links))
                parts.append(cm.group(0))
                last = cm.end()
            parts.append(self._tok(ln[last:], links))
            out.append("".join(parts))
        return "\n".join(out), links

    def _tok(self, s, links):
        def sub(m):
            links.append(m.group(1))
            return f"TSPLINK{len(links) - 1}TSP"
        return self.LINK.sub(sub, s)

    def link_html(self, raw, where, stage):
        raw = raw.strip()
        if raw.startswith("lesson:"):
            lid = raw[7:].strip()
            les = self.lessons.get(lid)
            if not les:
                LOG.err(where, f"[[lesson:{lid}]] points to an unknown lesson")
                return html.escape(lid)
            return f'<a class="tsp-xref" href="#/lesson/{lid}">{html.escape(les["title"])}</a>'
        if raw.startswith("problem:"):
            slug = raw[8:].strip()
            p = self.problems.get(slug)
            if not p:
                LOG.err(where, f"[[problem:{slug}]] points to an unknown problem")
                return html.escape(slug)
            return f'<a class="tsp-xref" href="#/problem/{slug}">{html.escape(p["title"])}</a>'
        term, _, shown = raw.partition("|")
        term = term.strip()
        key = term.lower()
        shown = (shown or term).strip()
        if key not in self.glossary:
            self.missing_terms.setdefault(key, set()).add(where)
            cls = "tsp-term missing"
        else:
            cls = "tsp-term"
        return (f'<span class="{cls}" data-term="{html.escape(key, quote=True)}" tabindex="0">'
                f'{html.escape(shown)}</span>')

    # -- public ---------------------------------------------------------------------
    def render(self, text, where, stage=None):
        text, blocks = self.extract_blocks(text, where)
        text, links = self.protect_links(text)
        self.md.reset()
        out = self.md.convert(text)
        for n, (lang, code, line) in enumerate(blocks):
            tok = f"TSPBLOCK{n}TSP"
            h = self.block_html(lang, code, line, where)
            out = out.replace(f"<p>{tok}</p>", h).replace(tok, h)
        for n, raw in enumerate(links):
            out = out.replace(f"TSPLINK{n}TSP", self.link_html(raw, where, stage))
        return out


# ---------------------------------------------------------------- validation of specs
def validate_question(q, where):
    if not isinstance(q, dict):
        LOG.err(where, "question must be an object")
        return
    t = q.get("type", "single")
    if t not in QTYPES:
        LOG.err(where, f"unknown question type {t!r}")
        return
    if not q.get("q"):
        LOG.err(where, "question has no 'q' text")
    opts = q.get("options")
    why = q.get("why")
    if t in ("single", "multi", "order"):
        if not isinstance(opts, list) or len(opts) < 2:
            LOG.err(where, f"{t} question needs 'options' (2 or more)")
            return
    if t == "single":
        a = q.get("answer")
        if not isinstance(a, int) or isinstance(a, bool) or not 0 <= a < len(opts):
            LOG.err(where, f"single answer index {a!r} is out of range (0..{len(opts) - 1})")
    if t == "multi":
        a = q.get("answer")
        if (not isinstance(a, list) or not a
                or any(not isinstance(x, int) or not 0 <= x < len(opts) for x in a)):
            LOG.err(where, f"multi answer {a!r} must be a list of valid option indexes")
    if t in ("single", "multi"):
        if not isinstance(why, list) or len(why) != len(opts):
            LOG.err(where, f"'why' must be a list with one reason per option ({len(opts)})")
    if t == "numeric":
        if not isinstance(q.get("answer"), (int, float)) or isinstance(q.get("answer"), bool):
            LOG.err(where, "numeric answer must be a number")
        if "tol" not in q:
            LOG.warn(where, "numeric question without 'tol' (exact match will be used)")
    if t in ("numeric", "order") and not isinstance(why, str):
        LOG.err(where, f"'why' must be a string for {t} questions")


def validate_chart(spec, where):
    series = spec.get("series")
    if not isinstance(series, list) or not series:
        LOG.err(where, "chart needs a non-empty 'series' list")
        return
    for s in series:
        if "y" not in s and "gen" not in s:
            LOG.err(where, f"series {s.get('name')!r} needs 'y' or 'gen'")
        for g in s.get("gen", []):
            if not (isinstance(g, list) and g and g[0] in GENERATORS):
                LOG.err(where, f"unknown generator {g!r}")
        if "gen" in s and "n" not in s:
            LOG.err(where, f"series {s.get('name')!r} with 'gen' needs 'n'")


# ---------------------------------------------------------------- loaders
def load_stages():
    stages = read_json(os.path.join(CONTENT, "stages.json"), [])
    ids = set()
    for s in stages:
        if s["id"] in ids:
            LOG.err("stages.json", f"duplicate stage id {s['id']}")
        ids.add(s["id"])
    return stages


def load_glossary(include_samples=False):
    """Merge content/glossary.json and content/*/glossary.*.json (first wins)."""
    merged, source = {}, {}
    files = [os.path.join(CONTENT, "glossary.json")]
    for d in sorted(os.listdir(CONTENT)):
        p = os.path.join(CONTENT, d)
        if os.path.isdir(p) and (include_samples or not d.startswith("_")):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p))
                      if re.match(r"^glossary\..+\.json$", f)]
    for f in files:
        data = read_json(f, {})
        if not isinstance(data, dict):
            LOG.err(rel(f), "glossary must be an object")
            continue
        for term, val in data.items():
            key = term.strip().lower()
            if isinstance(val, str):
                val = {"simple": val}
            if not isinstance(val, dict) or not val.get("simple"):
                LOG.err(rel(f), f"term {term!r} needs a 'simple' text")
                continue
            if key in merged:
                if merged[key].get("simple") != val.get("simple"):
                    LOG.warn(rel(f), f"term {term!r} also defined in {source[key]} with a different text (first wins)")
                continue
            merged[key] = {"term": term.strip(), "simple": val["simple"], "example": val.get("example", "")}
            source[key] = rel(f)
    return merged


def listdirs(path):
    return sorted(d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)))


def stage_dirs(include_samples):
    for d in listdirs(CONTENT):
        if d.startswith("_") and not include_samples:
            continue
        yield d


def split_sections(body):
    """Split Markdown at '## ' headings (ignoring fenced code). Returns [(title, text)]."""
    sections, cur_title, cur, fence = [], None, [], None
    pre = []
    for ln in body.replace("\r\n", "\n").split("\n"):
        m = Renderer.FENCE.match(ln)
        if m:
            if fence is None:
                fence = m.group(2)
            elif m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence) and not m.group(3):
                fence = None
        h = re.match(r"^##\s+(.+?)\s*#*\s*$", ln) if fence is None and not ln.startswith("###") else None
        if h:
            if cur_title is not None:
                sections.append((cur_title, "\n".join(cur).strip("\n")))
            cur_title, cur = h.group(1).strip(), []
        elif cur_title is None:
            pre.append(ln)
        else:
            cur.append(ln)
    if cur_title is not None:
        sections.append((cur_title, "\n".join(cur).strip("\n")))
    return "\n".join(pre).strip(), sections


def section_kind(title):
    n = norm(title)
    return {"warmup": "warmup", "whyitmatters": "why", "workedexample": "worked",
            "commonmistakes": "mistakes", "interviewlens": "interview", "realworld": "realworld",
            "stafflens": "staff", "keypoints": "keypoints"}.get(n, "concept")


def check_section_order(kinds, where, first_of_s0):
    """Enforce: [warmup] why concept+ worked mistakes interview realworld [staff] keypoints."""
    expected_tail = ["worked", "mistakes", "interview", "realworld"]
    k = list(kinds)
    if k and k[0] == "warmup":
        k = k[1:]
    elif not first_of_s0:
        LOG.err(where, "missing '## Warm-up' section (only the first lesson of S0 may skip it)")
    if not k or k[0] != "why":
        LOG.err(where, "'## Why it matters' must come first (after Warm-up)")
        return
    k = k[1:]
    n_concept = 0
    while k and k[0] == "concept":
        n_concept += 1
        k = k[1:]
    if n_concept == 0:
        LOG.err(where, "needs at least one concept chunk between 'Why it matters' and 'Worked example'")
    for need in expected_tail:
        if not k or k[0] != need:
            LOG.err(where, f"expected section '{need}' here; found {k[0] if k else 'end of lesson'} "
                           f"(order: Warm-up, Why it matters, concepts, Worked example, Common mistakes, "
                           f"Interview lens, Real world, [Staff lens], Key points)")
            return
        k = k[1:]
    if k and k[0] == "staff":
        k = k[1:]
    if k != ["keypoints"]:
        LOG.err(where, "last section must be '## Key points' (nothing after it)")


def count_words(s):
    return len(re.findall(r"\w+", s))


def parse_lesson_raw(stage_folder, lesson_dir):
    """Parse front matter and split sections; rendering happens later."""
    lpath = os.path.join(lesson_dir, "lesson.md")
    where = rel(lpath)
    if not os.path.exists(lpath):
        LOG.warn(rel(lesson_dir), "lesson folder has no lesson.md (skipped)")
        return None
    meta, body = parse_front_matter(read(lpath), where)
    folder = os.path.basename(lesson_dir)
    lid = meta.get("id", folder)
    if lid != folder:
        LOG.err(where, f"id {lid!r} must equal folder name {folder!r}")
    m = re.match(r"^(s\d+)-(\d+)-", lid)
    if not m:
        LOG.err(where, f"id {lid!r} must look like s1-03-slug")
        stage = stage_folder
    else:
        stage = m.group(1)
        if not stage_folder.startswith("_") and stage != stage_folder:
            LOG.err(where, f"id prefix {stage!r} does not match stage folder {stage_folder!r}")
    for req in ("title", "minutes", "goals"):
        if not meta.get(req):
            LOG.err(where, f"front matter is missing '{req}'")
    try:
        minutes = int(meta.get("minutes", 0) or 0)
    except ValueError:
        LOG.err(where, "minutes must be a number")
        minutes = 0
    level = meta.get("level", "beginner")
    if level not in LEVELS:
        LOG.warn(where, f"level {level!r} is not one of {LEVELS}", stage)
    _, sections = split_sections(body)
    return {"id": lid, "stage": stage, "dir": lesson_dir, "where": where, "title": meta.get("title", lid),
            "minutes": minutes, "level": level, "goals": as_list(meta.get("goals")),
            "prereqs": as_list(meta.get("prereqs")), "tags": as_list(meta.get("tags")),
            "skills": as_list(meta.get("skills")), "raw_sections": sections,
            "order": int(m.group(2)) if m else 0}


def parse_problem_raw(pdir, lesson_id, stage):
    where = rel(os.path.join(pdir, "problem.md"))
    meta, body = parse_front_matter(read(os.path.join(pdir, "problem.md")), where)
    slug = meta.get("slug", os.path.basename(pdir))
    if slug != os.path.basename(pdir):
        LOG.err(where, f"slug {slug!r} must equal folder name {os.path.basename(pdir)!r}")
    if meta.get("difficulty") not in DIFFICULTIES:
        LOG.err(where, f"difficulty must be one of {DIFFICULTIES}")
    ptype = meta.get("type", "function")
    if ptype not in PTYPES:
        LOG.err(where, f"type must be one of {PTYPES}")
    if not meta.get("title"):
        LOG.err(where, "missing title")
    # Split the body at '### Hints' and '### Solution explanation'.
    desc, hints, sol = [], [], []
    cur, fence = desc, None
    for ln in body.replace("\r\n", "\n").split("\n"):
        m = Renderer.FENCE.match(ln)
        if m:
            if fence is None:
                fence = m.group(2)
            elif m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence) and not m.group(3):
                fence = None
        if fence is None:
            t = re.match(r"^###\s+(.+?)\s*$", ln)
            if t and norm(t.group(1)) == "hints":
                cur = hints
                continue
            if t and norm(t.group(1)) in ("solutionexplanation", "solution"):
                cur = sol
                continue
        cur.append(ln)
    hint_items = []
    for ln in hints:
        m = re.match(r"^\s*\d+[.)]\s+(.*)$", ln)
        if m:
            hint_items.append(m.group(1))
        elif ln.strip() and hint_items:
            hint_items[-1] += " " + ln.strip()
    if len(hint_items) < 3:
        LOG.warn(where, f"has {len(hint_items)} hints (3 expected)", stage)
    if not "".join(sol).strip():
        LOG.err(where, "missing '### Solution explanation'")
    files = {}
    for fn in ("starter.py", "solution.py", "tests.py"):
        p = os.path.join(pdir, fn)
        files[fn] = read(p) if os.path.exists(p) else ""
    return {"slug": slug, "dir": pdir, "where": where, "title": meta.get("title", slug),
            "difficulty": meta.get("difficulty", "Easy"), "type": ptype,
            "tags": as_list(meta.get("tags")), "skills": as_list(meta.get("skills")),
            "packages": [p for p in as_list(meta.get("packages")) if p],
            "companies_style": as_list(meta.get("companies_style")),
            "lesson": lesson_id, "stage": stage, "desc": re.sub(r"^(\*\*(?:Input|Output|Explanation):\*\*.*?)\s*$", r"\1  ", "\n".join(desc).strip(), flags=re.M),
            "hints": hint_items, "sol": "\n".join(sol).strip(), "files": files}


def visible_cases(tests_src, where):
    """Execute tests.py once to learn the case list (names, visible calls)."""
    import harness
    ns = {"__name__": "tests"}
    ns.update(harness.HELPERS)
    try:
        exec(compile(tests_src, "tests.py", "exec"), ns)
    except Exception as e:  # noqa
        LOG.err(where, f"tests.py does not run: {e!r}")
        return [], 0
    cases = ns.get("CASES")
    if not isinstance(cases, list):
        LOG.err(where, "tests.py defines no CASES list")
        return [], 0
    out = []
    for c in cases:
        if c.get("visible"):
            item = {"name": c.get("name", "Case"), "call": c["call"]}
            for k in ("expected", "tol", "check_index"):
                if k in c:
                    item[k] = c[k]
            out.append(item)
    return out, len(cases)


# ---------------------------------------------------------------- main build
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-samples", action="store_true", help="also build content/_* folders")
    ap.add_argument("--skip-judge", action="store_true", help="do not run the reference solutions")
    ap.add_argument("--strict", action="store_true", help="treat missing glossary terms as errors")
    args = ap.parse_args()

    stages = load_stages()
    stage_ids = [s["id"] for s in stages]
    glossary = load_glossary(args.include_samples)

    # ---- pass 1: discover lessons + problems (no rendering yet) ----
    lessons, problems = {}, {}
    for sf in stage_dirs(args.include_samples):
        sdir = os.path.join(CONTENT, sf)
        if not sf.startswith("_") and sf not in stage_ids:
            LOG.warn(f"content/{sf}", "folder is not a stage id in stages.json (skipped)")
            continue
        for ld in listdirs(sdir):
            lraw = parse_lesson_raw(sf, os.path.join(sdir, ld))
            if not lraw:
                continue
            if lraw["id"] in lessons:
                LOG.err(lraw["where"], f"duplicate lesson id {lraw['id']}")
                continue
            if lraw["stage"] not in stage_ids:
                LOG.err(lraw["where"], f"unknown stage {lraw['stage']!r}")
                continue
            lessons[lraw["id"]] = lraw
            pdir_root = os.path.join(lraw["dir"], "problems")
            lraw["problem_slugs"] = []
            if os.path.isdir(pdir_root):
                for pd_ in listdirs(pdir_root):
                    pdir = os.path.join(pdir_root, pd_)
                    if not os.path.exists(os.path.join(pdir, "problem.md")):
                        continue
                    praw = parse_problem_raw(pdir, lraw["id"], lraw["stage"])
                    if praw["slug"] in problems:
                        LOG.err(praw["where"], f"duplicate problem slug {praw['slug']}")
                        continue
                    problems[praw["slug"]] = praw
                    lraw["problem_slugs"].append(praw["slug"])

    # prereqs
    for l in lessons.values():
        for p in l["prereqs"]:
            if p not in lessons:
                LOG.err(l["where"], f"prereq {p!r} does not exist")

    # ---- pass 2: render ----
    rend = Renderer(glossary, lessons, problems)
    first_in_s0 = min((l["id"] for l in lessons.values() if l["stage"] == "s0"), default=None)
    out_lessons = {}
    counts = {"quizzes": 0, "cards": 0, "drills": 0, "questions": 0}
    for lid in sorted(lessons, key=lambda i: (stage_ids.index(lessons[i]["stage"]), lessons[i]["order"], i)):
        l = lessons[lid]
        kinds = [section_kind(t) for t, _ in l["raw_sections"]]
        check_section_order(kinds, l["where"], lid == first_in_s0)
        sections = []
        for (title, text), kind in zip(l["raw_sections"], kinds):
            sid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "section"
            if kind == "concept" and count_words(re.sub(r"```.*?```", "", text, flags=re.S)) > 220:
                LOG.warn(l["where"], f"section '{title}' is long (>220 words); aim for ~150", l["stage"])
            sections.append({"id": sid, "title": title, "kind": kind,
                             "html": rend.render(text, f"{l['where']} §{title}", l["stage"])})
        d = l["dir"]
        quiz = read_json(os.path.join(d, "quiz.json"))
        if quiz is None:
            LOG.err(l["where"], "missing quiz.json")
            quiz = {"pass": 0.8, "questions": []}
        else:
            qs = quiz.get("questions", [])
            if not 5 <= len(qs) <= 8:
                LOG.warn(rel(os.path.join(d, "quiz.json")), f"has {len(qs)} questions (5-8 expected)", l["stage"])
            for n, q in enumerate(qs):
                validate_question(q, f"{rel(os.path.join(d, 'quiz.json'))} Q{n + 1}")
            quiz.setdefault("pass", 0.8)
            counts["quizzes"] += 1
            counts["questions"] += len(qs)
        cards = read_json(os.path.join(d, "cards.json"))
        if cards is None:
            LOG.err(l["where"], "missing cards.json")
            cards = []
        else:
            cw = rel(os.path.join(d, "cards.json"))
            if not 4 <= len(cards) <= 8:
                LOG.warn(cw, f"has {len(cards)} cards (4-8 expected)", l["stage"])
            for n, c in enumerate(cards):
                if not (isinstance(c, dict) and c.get("front") and c.get("back")):
                    LOG.err(cw, f"card {n + 1} needs 'front' and 'back'")
                    continue
                if count_words(c["front"]) > 15 or count_words(c["back"]) > 35:
                    LOG.warn(cw, f"card {n + 1} is long (front<=15, back<=35 words)", l["stage"])
            counts["cards"] += len(cards)
        drill = None
        dpath = os.path.join(d, "drill.json")
        if os.path.exists(dpath):
            drill = build_drill(read_json(dpath, {}), rel(dpath), rend, l["stage"])
            counts["drills"] += 1
        out_lessons[lid] = {
            "id": lid, "stage": l["stage"], "title": l["title"], "minutes": l["minutes"],
            "level": l["level"], "goals": l["goals"], "prereqs": l["prereqs"], "tags": l["tags"],
            "skills": l["skills"], "sections": sections, "quiz": quiz, "cards": cards,
            "drill": drill, "problems": l["problem_slugs"],
        }

    # problems
    out_problems = {}
    from check_problem import check as check_problem
    for slug, p in problems.items():
        w = p["where"]
        for fn in ("starter.py", "solution.py", "tests.py"):
            if not p["files"][fn].strip():
                LOG.err(w, f"missing or empty {fn}")
        vis, total = visible_cases(p["files"]["tests.py"], w)
        if not args.skip_judge:
            for e in check_problem(p["dir"]):
                LOG.err(w, e)
        out_problems[slug] = {
            "slug": slug, "title": p["title"], "difficulty": p["difficulty"], "type": p["type"],
            "tags": p["tags"], "skills": p["skills"], "packages": p["packages"],
            "style": p["companies_style"], "lesson": p["lesson"], "stage": p["stage"],
            "descriptionHtml": rend.render(p["desc"], w, p["stage"]),
            "hints": [rend.render(h, w, p["stage"]) for h in p["hints"]],
            "solutionHtml": rend.render(p["sol"], w, p["stage"]),
            "starter": p["files"]["starter.py"], "solution": p["files"]["solution.py"],
            "tests": p["files"]["tests.py"], "visible": vis, "nCases": total,
        }

    # mock sets
    mock_sets = []
    mpath = os.path.join(CONTENT, "s13", "mock_sets.json")
    for ms in read_json(mpath, []) or []:
        for slug in ms.get("problems", []):
            if slug not in problems:
                LOG.err(rel(mpath), f"mock set {ms.get('id')} uses unknown problem {slug!r}")
        mock_sets.append(ms)
    ids = [m.get("id") for m in mock_sets]
    if len(ids) != len(set(ids)):
        LOG.err(rel(mpath), "duplicate mock set ids")

    # glossary: missing terms
    for term, wheres in sorted(rend.missing_terms.items()):
        msg = f"term [[{term}]] is not in the glossary (used in {len(wheres)} place(s), e.g. {sorted(wheres)[0]})"
        (LOG.err if args.strict else LOG.warn)("glossary", msg)

    # stages output
    out_stages = []
    for s in stages:
        ls = [i for i, l in out_lessons.items() if l["stage"] == s["id"]]
        out_stages.append({**s, "lessons": ls})

    total_q = sum(len(l["quiz"].get("questions", [])) for l in out_lessons.values())
    bundle = {
        "built": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "samples": args.include_samples,
        "counts": {"stages": len(stages), "lessons": len(out_lessons), "problems": len(out_problems),
                   "quizzes": counts["quizzes"], "quizQuestions": total_q, "cards": counts["cards"],
                   "drills": counts["drills"], "glossary": len(glossary), "mockSets": len(mock_sets)},
        "stages": out_stages, "lessons": out_lessons, "problems": out_problems,
        "glossary": glossary, "mockSets": mock_sets,
    }

    print_summary(out_stages, out_lessons, out_problems)
    for w in LOG.warnings[:60]:
        print("WARN ", w)
    if len(LOG.warnings) > 60:
        print(f"WARN  … and {len(LOG.warnings) - 60} more warnings")
    for e in LOG.errors:
        print("ERROR", e)
    if LOG.errors:
        print(f"\nBuild FAILED with {len(LOG.errors)} error(s).")
        return 1

    os.makedirs(os.path.join(SITE, "data"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "engine"), exist_ok=True)
    with open(os.path.join(SITE, "data", "content.js"), "w", encoding="utf-8") as f:
        f.write("window.TSP_CONTENT = ")
        json.dump(bundle, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    shutil.copyfile(os.path.join(ROOT, "tools", "harness.py"), os.path.join(SITE, "engine", "harness.py"))
    size = os.path.getsize(os.path.join(SITE, "data", "content.js")) / 1024
    print(f"\nWrote site/data/content.js ({size:.0f} KB) and site/engine/harness.py. "
          f"{len(LOG.warnings)} warning(s).")
    return 0


def build_drill(d, where, rend, stage):
    if not isinstance(d, dict) or not d.get("sections"):
        LOG.err(where, "drill needs 'sections'")
        return None
    for k in ("title", "prompt", "model_answer", "rubric"):
        if not d.get(k):
            LOG.err(where, f"drill is missing '{k}'")
    secs = d.get("sections", [])
    ma = d.get("model_answer", {}) or {}
    for s in secs:
        if s.get("id") not in ma:
            LOG.err(where, f"model_answer has no entry for section {s.get('id')!r}")
    return {
        "title": d.get("title", ""), "minutes": int(d.get("minutes", 45)), "level": d.get("level", ""),
        "promptHtml": rend.render(d.get("prompt", ""), where + " prompt", stage),
        "sections": [{"id": s.get("id"), "label": s.get("label", ""), "hint": s.get("hint", "")} for s in secs],
        "modelHtml": {k: rend.render(v, f"{where} model_answer.{k}", stage) for k, v in ma.items()},
        "rubric": d.get("rubric", []),
        "followUps": d.get("follow_ups", []),
    }


def print_summary(stages, lessons, problems):
    rows = []
    for s in stages:
        ls = [lessons[i] for i in s["lessons"]]
        rows.append((s["id"], s["title"][:30], len(ls), sum(len(l["problems"]) for l in ls),
                     sum(1 for l in ls if l["quiz"].get("questions")), sum(len(l["cards"]) for l in ls),
                     LOG.by_stage.get(s["id"], 0)))
    print(f"{'stage':<6}{'title':<32}{'lessons':>8}{'problems':>9}{'quizzes':>8}{'cards':>6}{'warns':>6}")
    for r in rows:
        print(f"{r[0]:<6}{r[1]:<32}{r[2]:>8}{r[3]:>9}{r[4]:>8}{r[5]:>6}{r[6]:>6}")
    print(f"{'total':<38}{sum(r[2] for r in rows):>8}{sum(r[3] for r in rows):>9}"
          f"{sum(r[4] for r in rows):>8}{sum(r[5] for r in rows):>6}{len(LOG.warnings):>6}")


if __name__ == "__main__":
    sys.exit(main())
