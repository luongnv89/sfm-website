#!/usr/bin/env python3
"""Checks run before every deploy (and locally: python3 scripts/check-site.py site).

1. Every local link, image, stylesheet and font a page refers to exists
   inside the site folder, and every #id link has its target.
2. Nothing is loaded from another site: no external script, stylesheet,
   font or image, no inline script or style, no style attribute. The pages'
   Content-Security-Policy would block these; the privacy policy says there
   are none.

Exit codes: 0 all checks pass, 1 a check failed, 2 usage error.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

LOADS = {("script", "src"), ("img", "src"), ("source", "srcset"), ("link", "href")}
# <link> relations that only name a URL and fetch nothing.
NO_FETCH_RELS = {"canonical"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.loads, self.problems = set(), [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if "style" in a:
            self.problems.append(f"style attribute on <{tag}>")
        if tag == "style":
            self.problems.append("inline <style>")
        if tag == "script":
            self.problems.append("<script> (the site ships no JavaScript)")
        if any(k.startswith("on") for k in a):
            self.problems.append(f"event handler attribute on <{tag}>")
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        for t, attr in LOADS:
            if tag == t and a.get(attr):
                if t == "link" and a.get("rel", "") in NO_FETCH_RELS:
                    continue
                self.loads.append(a[attr])


def main() -> int:
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        print("usage: check-site.py SITE_DIR", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).resolve()
    pages = {}
    for path in sorted(root.glob("*.html")):
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        pages[path.name] = page
    failures = []

    def local(page_name, ref):
        target, _, frag = ref.partition("#")
        target = target.split("?")[0]
        name = target.lstrip("/") if target else page_name
        file = (root / name).resolve()
        if root not in file.parents and file != root:
            return f"{ref}: leaves the site folder"
        if file.is_dir():
            file = file / "index.html"
        if not file.exists():
            return f"{ref}: no such file"
        if frag and file.suffix == ".html" and frag not in pages[file.name].ids:
            return f"{ref}: no element with id {frag}"
        return None

    for name, page in pages.items():
        for problem in page.problems:
            failures.append(f"{name}: {problem}")
        for ref in page.loads:
            if re.match(r"^(https?:)?//|^data:", ref):
                failures.append(f"{name}: loads {ref} from outside the site")
            elif (err := local(name, ref)) is not None:
                failures.append(f"{name}: {err}")
        for ref in page.links:
            if re.match(r"^(https?|mailto):", ref):
                continue
            if (err := local(name, ref)) is not None:
                failures.append(f"{name}: {err}")

    for css in sorted(root.rglob("*.css")):
        text = re.sub(r"/\*.*?\*/", "", css.read_text(encoding="utf-8"), flags=re.S)
        if "@import" in text:
            failures.append(f"{css.name}: @import")
        for ref in re.findall(r"url\(\s*[\"']?([^\"')]+)", text):
            if re.match(r"^(https?:)?//|^data:", ref):
                failures.append(f"{css.name}: loads {ref} from outside the site")
            elif not (css.parent / ref).resolve().exists():
                failures.append(f"{css.name}: {ref}: no such file")

    for failure in failures:
        print(f"FAIL {failure}")
    print(f"{len(pages)} pages checked, {len(failures)} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
