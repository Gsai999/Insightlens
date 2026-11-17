import json, re, warnings
from io import BytesIO, StringIO
import numpy as np
import pandas as pd
import requests
from urllib.parse import parse_qs, urlparse
import streamlit as st

def fix_url(u):
    u = u.strip(); p = urlparse(u); h = p.netloc.lower()
    if h == "github.com" and "/blob/" in p.path:
        return "https://raw.githubusercontent.com" + p.path.replace("/blob/", "/", 1)
    if h == "gist.github.com" and p.path.count("/") == 2:
        return f"https://gist.githubusercontent.com{p.path}/raw"
    if h == "docs.google.com" and "/spreadsheets/d/" in p.path:
        return f"https://docs.google.com/spreadsheets/d/{p.path.split('/d/')[1].split('/')[0]}/export?format=csv&gid={parse_qs(p.query).get('gid', ['0'])[0]}"
    if h == "drive.google.com":
        m = re.search(r"/d/([^/]+)", p.path); i = m[1] if m else parse_qs(p.query).get("id", [""])[0]
        if i: return f"https://drive.google.com/uc?export=download&id={i}"
    if "dropbox.com" in h:
        return re.sub(r"([?&])dl=0", r"\1dl=1", u) if "dl=" in u else u + ("&" if "?" in u else "?") + "dl=1"
    if h == "huggingface.co": return u.replace("/blob/", "/resolve/", 1)
    return u

def fetch(url):
    r = requests.get(fix_url(url), timeout=40, headers={"User-Agent": "Mozilla/5.0 InsightLens"})
    r.raise_for_status()
    return r.content, urlparse(r.url).path

@st.cache_data(ttl=3600, show_spinner="Downloading data from URL...")
def cached_fetch(url):
    return fetch(url)

def find_records(o, depth=0):
    if isinstance(o, list) and o and isinstance(o[0], dict): return o
    if isinstance(o, dict) and depth < 3:
        for v in o.values():
            r = find_records(v, depth + 1)
            if r: return r
    return None

@st.cache_data(show_spinner="Parsing dataset efficiently...")
def read_any(b, name=""):
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    
    # Use Rust-powered 'calamine' engine for blazing-fast Excel reading
    if b[:4] == b"PK\x03\x04" or ext in ("xlsx", "xlsm", "xls"): 
        return pd.read_excel(BytesIO(b), engine="calamine")
        
    if b[:4] == b"PAR1" or ext == "parquet": 
        return pd.read_parquet(BytesIO(b))
        
    text = b.decode("utf-16") if b.startswith((b"\xff\xfe", b"\xfe\xff")) else b.decode("utf-8-sig", errors="replace")
    s = text.lstrip()
    if s[:15].lower().startswith(("<!doctype", "<html")):
        try: tables = pd.read_html(StringIO(text))
        except ImportError: raise ValueError("Web page table parsing needs `pip install lxml`.")
        except ValueError: raise ValueError("Web page lacks a data table. Use a direct CSV / Excel / JSON link.")
        return max(tables, key=lambda t: t.size)
    if s[:1] in ("{", "[") or ext in ("json", "geojson"):
        try: obj = json.loads(text)
        except ValueError: obj = None
        if obj is not None:
            if isinstance(obj, dict) and isinstance(obj.get("features"), list):
                return pd.json_normalize([f.get("properties", {}) for f in obj["features"]])
            rec = find_records(obj)
            return pd.json_normalize(rec if rec else (obj if isinstance(obj, list) else [obj]))
    first = next((l for l in text.splitlines() if l.strip()), "")
    sep = max([",", ";", "\t", "|"], key=first.count)
    return pd.read_csv(StringIO(text), sep=sep, on_bad_lines="skip")

def tidy(raw):
    df, names, seen = raw.copy(), [], {}
    for i, c in enumerate(df.columns):
        n = re.sub(r"\s+", " ", str(c)).strip() or f"Column {i + 1}"
        seen[n] = seen.get(n, -1) + 1
        names.append(n if seen[n] == 0 else f"{n} ({seen[n]})")
    df.columns = names
    df = df.dropna(how="all").dropna(axis=1, how="all").reset_index(drop=True)
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_numeric_dtype(s) or pd.api.types.is_datetime64_any_dtype(s) or pd.api.types.is_bool_dtype(s): continue
        s = s.map(lambda v: v.strip() if isinstance(v, str) else v).replace("", np.nan)
        df[c] = s
        txt = s.dropna().astype(str)
        if txt.empty: continue
        if not txt.str.match(r"^0\d").any():
            num = pd.to_numeric(txt.str.replace(r"[,\s$€£₹%]", "", regex=True), errors="coerce")
            if num.notna().mean() >= .95: df[c] = num.reindex(s.index); continue
        if txt.head(200).str.match(r"^\s*(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})([ T]\d{1,2}:\d{2}.*)?\s*$").mean() >= .8:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                dt = pd.to_datetime(txt, errors="coerce", dayfirst=True)
            if dt.notna().mean() >= .8: 
                df[c] = dt.dt.strftime("%B %d, %Y").reindex(s.index)
    return df.reset_index(drop=True)

def clean(df, o):
    from modules.analysis import kinds
    d, log, k = df.copy(), [], kinds(df)
    txt = [c for c in d.columns if c in k["cat"] + k["id"] and not pd.api.types.is_numeric_dtype(d[c])]
    if o["drop"]: d = d.drop(columns=o["drop"]); log.append(f"Removed columns: {', '.join(o['drop'])}")
    if o["trim"]:
        for c in [c for c in txt if c in d]: d[c] = d[c].map(lambda v: re.sub(r"\s+", " ", v.strip()) if isinstance(v, str) else v).replace("", np.nan)
        log.append("Trimmed whitespace.")
    if o["empty"]: e = d.columns[d.isna().all()].tolist(); d = d.drop(columns=e); log.append(f"Removed {len(e)} empty columns.")
    
    if o.get("dupes_mode") == "Exact row match":
        b = len(d); d = d.drop_duplicates(); log.append(f"Removed {b - len(d):,} exact duplicate rows.")
    elif o.get("dupes_mode") == "Subset column match" and o.get("dupes_subset"):
        b = len(d); d = d.drop_duplicates(subset=o["dupes_subset"]); log.append(f"Removed {b - len(d):,} duplicate rows based on subset [{', '.join(o['dupes_subset'])}].")
    
    if o["na"] == "Drop rows with missing values":
        b = len(d); d = d.dropna(); log.append(f"Dropped {b - len(d):,} rows with missing values.")
    elif o["na"] == "Fill empty cells with 0":
        d = d.fillna(0); log.append("Filled all empty/missing cells with 0.")
    elif o["na"].startswith("Fill (median"):
        n = 0; skip = set(k["lat"] + k["lon"] + k["id"])
        for c in d.columns:
            m = int(d[c].isna().sum())
            if not m or c in skip or c in k["date"]: continue
            if pd.api.types.is_numeric_dtype(d[c]): fill = d[c].median()
            else: md = d[c].mode(); fill = md.iloc[0] if len(md) else None
            if fill is not None and pd.notna(fill): d[c] = d[c].fillna(fill); n += m
        log.append(f"Imputed {n:,} missing cells.")
    return d.reset_index(drop=True), log