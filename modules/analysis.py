import pandas as pd
import numpy as np
import re

def kinds(df):
    # Safety guard: return empty lists if df is None or not a DataFrame
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return {"num": [], "cat": [], "date": [], "lat": [], "lon": [], "id": []}
    
    n, k = max(len(df), 1), {x: [] for x in ("num", "cat", "date", "lat", "lon", "id")}
    for c in df.columns:
        s, u = df[c], df[c].nunique()
        t = set(re.split(r"[^a-z0-9]+", str(c).lower()))
        if pd.api.types.is_datetime64_any_dtype(s) or (t & {"date", "time", "day", "month", "year", "joined"} and not t & {"code", "id", "city", "country", "name"}):
            k["date"].append(c)
        elif pd.api.types.is_bool_dtype(s): k["cat"].append(c)
        elif pd.api.types.is_numeric_dtype(s):
            v = s.dropna(); ints = len(v) > 0 and bool((v % 1 == 0).all())
            if t & {"lat", "latitude"}: k["lat"].append(c)
            elif t & {"lon", "lng", "long", "longitude"}: k["lon"].append(c)
            elif t & {"id", "index", "zip", "pin", "pincode", "postal", "phone", "sku"} or (ints and n > 20 and u / n > .98 and v.max() - v.min() <= 1.5 * n): k["id"].append(c)
            elif t & {"year", "month", "quarter", "week"} and ints and u <= 60: k["cat"].append(c)
            else: k["num"].append(c)
        elif u <= 50 or u / n <= .5: k["cat"].append(c)
        else: k["id"].append(c)
    return k

def quality(df):
    if df is None or not isinstance(df, pd.DataFrame) or df.empty: return 0, 0
    cells = max(df.size, 1)
    m = int(df.isna().sum().sum())
    for col in df.columns:
        if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            m += int((df[col].astype(str).str.strip() == "").sum())
    d = int(df.duplicated().sum())
    return m, d

def agg(df, by, val, how):
    if df is None or df.empty: return pd.DataFrame()
    key = df[by].astype("object").where(df[by].notna(), "(blank)").astype(str)
    s = key.groupby(key).size() if val is None else df[val].groupby(key).agg(how)
    return s.rename("Value").rename_axis("Label").reset_index()

def fmt(x):
    if x is None or pd.isna(x): return "–"
    for lim, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(x) >= lim: return f"{x / lim:,.1f}{suf}"
    return f"{x:,.0f}" if float(x).is_integer() else f"{x:,.2f}"

def insights(df, k, val, by, dc):
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return ["No data loaded to generate insights."]
    out, (m, d) = [], quality(df)
    out.append(f"Dataset contains {len(df):,} records and {df.shape[1]} fields ({m:,} missing/blank cells, {d} duplicate rows detected).")
    if by and by in df.columns:
        g = agg(df, by, val, "sum").sort_values("Value", ascending=False)
        if len(g) > 1:
            t, lo = g.iloc[0], g.iloc[-1]
            out.append(f"Grouped by {by}, {t['Label']} leads with {fmt(t['Value'])}; {lo['Label']} records the lowest at {fmt(lo['Value'])}.")
    return out