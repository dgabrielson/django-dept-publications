import re
import unicodedata

from . import conf


def fix_reference_key(value, allow_unicode=False):
    """
    Modified from django 2.0.5 slugify to preserve case.

    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value).strip()
    return re.sub(r"[-\s]+", "-", value)


def latex_to_unicode_cyrillic(s):
    table = {
        "\\cprime": "\u042c",  # soft sign
        "\\cdprime": "\u042a",  # hard sign
        "\\cprime": "ь",  # "soft sign"
        "\\cdprime": "ъ",  # "hard sign"
        "\\u{i}": "й",  # "i-kratkaya"
        '\\"{e}': "ё",  # "yoh"
        "\\`{e}": "э",  # "e-oborotnoye"
        "\\`{E}": "Э",  # "E-oborotnoye"
    }
    for k, v in table.items():
        s = s.replace(k, v)
    return s


def latex_unicode_fixes(s):
    from bibtexparser.latexenc import latex_to_unicode

    fixers = [latex_to_unicode, latex_to_unicode_cyrillic]

    def _fix(s):
        for f in fixers:
            s = f(s)
        return s

    if conf.get("preserve-math-mode"):
        # only fix non-math-mode parts
        safety_map = {
            "\\$": ":ESC:DOLLAR:",
            "\\(": ":ESC:$:OPENMATH:",
            "\\)": ":ESC:$:CLOSEMATH:",
        }
        for k, v in safety_map.items():
            s = s.replace(k, v)
        parts = s.split("$")
        mathmode = False
        fixed = []
        for p in parts:
            if mathmode:
                fixed.append(p)
            else:
                fixed.append(_fix(p))
            mathmode = not mathmode
        s = "$".join(fixed)
        for k, v in safety_map.items():
            s = s.replace(v, k)
        return s

    else:
        return _fix(s)
