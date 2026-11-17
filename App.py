"""InsightLens - Complete Automated BI & Analytics Studio.
Run: streamlit run App.py
"""
import re
from html import escape
from io import BytesIO
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from colors import THEMES, MULTI_PALETTE, get_custom_css
from data.sample_dataset import SAMPLE_OPTIONS
from modules.cleaning import cached_fetch, fetch, read_any, tidy, clean
from modules.analysis import kinds, quality, insights

st.set_page_config(page_title="InsightLens Analytics", page_icon="📊", layout="wide")
_v = re.match(r"(\d+)\.(\d+)", st.__version__)
W = {"width": "stretch"} if _v and (int(_v[1]), int(_v[2])) >= (1, 50) else {"use_container_width": True}

ss = st.session_state
for a, b in dict(df=None, orig=None, name="", log=[], ver=0, flash=None, theme="Lavender Dream", dashboard_figs=[]).items():
    ss.setdefault(a, b)

current_colors = THEMES.get(ss.theme, THEMES["Lavender Dream"])
st.markdown(get_custom_css(current_colors), unsafe_allow_html=True)

# Custom CSS to hide the Streamlit top-right Deploy menu / button cleanly & style brand titles
st.markdown(f"""<style>
[data-testid="stToolbar"] {{visibility: hidden !important; display: none !important;}}
header {{visibility: hidden !important; display: none !important;}}

.sidebar-brand {{
    margin-bottom: 18px;
    line-height: 1.25;
}}
.sidebar-brand-bold {{
    font-size: 26px;
    font-weight: 800;
    color: {current_colors['primary']};
    letter-spacing: -0.5px;
}}
.sidebar-brand-light {{
    font-size: 14px;
    font-weight: 400;
    color: {current_colors['primary']};
    opacity: 0.85;
    margin-top: 2px;
}}

.main-brand {{
    margin-bottom: 12px;
    line-height: 1.2;
}}
.main-brand-bold {{
    font-size: 36px;
    font-weight: 800;
    color: {current_colors['primary']};
    letter-spacing: -0.6px;
}}
.main-brand-light {{
    font-size: 22px;
    font-weight: 400;
    color: {current_colors['primary']};
    opacity: 0.88;
}}
</style>""", unsafe_allow_html=True)

def show(d, h=360):
    d = d.copy(); d.columns = d.columns.astype(str)
    for c in d.columns:
        if d[c].dtype == object: d[c] = d[c].map(lambda v: v if pd.isna(v) else str(v))
    d.insert(0, "No.", np.arange(1, len(d) + 1))
    st.dataframe(d, height=h, hide_index=True, **W)

def kpi(title, val): 
    return f'''
    <div class="kpi-box">
        <div class="kpi-title">{escape(str(title))}</div>
        <div class="kpi-value">{escape(str(val))}</div>
    </div>
    '''

def commit(d, log):
    ss.df = d.reset_index(drop=True); ss.log = ss.log + log; ss.ver += 1; st.rerun()

with st.sidebar:
    st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-bold">📊 InsightLens</div>
            <div class="sidebar-brand-light">A LOW-CODE AUTOMATED DATA ANALYTICS PLATFORM
</div>
        </div>
    """, unsafe_allow_html=True)
    
    selected_theme = st.selectbox("Color Theme", list(THEMES.keys()), key="theme_selector")
    if selected_theme != ss.theme:
        ss.theme = selected_theme
        st.rerun()
    
    st.divider()
    st.subheader("Import & Load Data")
    import_mode = st.radio("Source Type", ["Preloaded Samples", "Upload File (CSV/Excel)", "Public URL"])
    
    try:
        if import_mode == "Preloaded Samples":
            chosen_sample = st.selectbox("Sample Dataset", list(SAMPLE_OPTIONS.keys()))
            if st.button("Load Sample Dataset", **W):
                raw_df = SAMPLE_OPTIONS[chosen_sample]()
                d0 = tidy(raw_df)
                ss.df, ss.orig, ss.name, ss.log, ss.ver, ss.dashboard_figs = d0, d0.copy(), chosen_sample, [], ss.ver + 1, []
                ss.flash = f"Loaded sample: {chosen_sample} ({len(d0):,} rows)"
                st.rerun()
        elif import_mode == "Upload File (CSV/Excel)":
            up = st.file_uploader("Upload CSV, Excel, JSON", type=["csv", "tsv", "txt", "xlsx", "xls", "json"])
            if st.button("Process Uploaded File", **W) and up is not None:
                raw_df = read_any(up.getvalue(), up.name)
                d0 = tidy(raw_df)
                ss.df, ss.orig, ss.name, ss.log, ss.ver, ss.dashboard_figs = d0, d0.copy(), up.name, [], ss.ver + 1, []
                ss.flash = f"Loaded file: {up.name} ({len(d0):,} rows)"
                st.rerun()
        else:
            url_input = st.text_input("Paste Data URL (CSV, Excel, GitHub Raw)", "https://raw.githubusercontent.com/vega/vega-datasets/master/data/airports.csv")
            if st.button("Fetch URL Data", **W) and url_input.strip():
                content, path = cached_fetch(url_input)
                raw_df = read_any(content, path)
                d0 = tidy(raw_df)
                nm = path.split("/")[-1] or "URL Dataset"
                ss.df, ss.orig, ss.name, ss.log, ss.ver, ss.dashboard_figs = d0, d0.copy(), nm, [], ss.ver + 1, []
                ss.flash = f"Fetched URL: {nm} ({len(d0):,} rows)"
                st.rerun()
    except Exception as e:
        st.error(f"Error loading source: {e}")

    if ss.df is not None:
        st.divider()
        c1, c2 = st.columns(2)
        if c1.button("Reset Data"):
            ss.df, ss.log, ss.ver, ss.dashboard_figs = ss.orig.copy(), [], ss.ver + 1, []
            st.rerun()
        if c2.button("Clear All"):
            ss.df = ss.orig = None; ss.log = []; ss.dashboard_figs = []; st.rerun()

st.markdown("""
    <div class="main-brand">
        <span class="main-brand-bold">📊 InsightLens</span>
        <span class="main-brand-light"> A LOW-CODE AUTOMATED DATA ANALYTICS PLATFORM
</span>
    </div>
""", unsafe_allow_html=True)

if ss.flash:
    st.success(ss.flash)
    ss.flash = None

if ss.df is None:
    st.info("Please select a preloaded sample, upload an Excel/CSV file, or paste a public URL in the sidebar to begin.")
    st.stop()

df = ss.df; K = kinds(df); fdf = df

with st.sidebar:
    st.divider(); st.subheader("Global Slicers & Filters"); ver = ss.ver
    q = st.text_input("Search keyword", key=f"q{ver}")
    if q.strip():
        m = pd.Series(False, index=df.index)
        for c in K["cat"] + K["id"]: m |= df[c].astype(str).str.contains(q.strip(), case=False, regex=False, na=False)
        fdf = fdf[m]

st.caption(f"Active Dataset: {ss.name} · {len(df):,} rows · {df.shape[1]} columns")

pages = ["Overview & Profile", "Power Query (Cleaning)", "Column Renaming Studio", "Charts Studio (Visualizations)", "InsightLens Dashboard & Custom HTML Studio"]
page = st.radio("Workspace Tabs", pages, horizontal=True, label_visibility="collapsed")
st.divider()

if page == "Overview & Profile":
    a, b, c = st.columns(3)
    m_val, d_val = quality(df)
    a.markdown(kpi("Total Records", f"{len(df):,}"), unsafe_allow_html=True)
    b.markdown(kpi("Total Columns", f"{df.shape[1]}"), unsafe_allow_html=True)
    c.markdown(kpi("Missing / Blank Cells", f"{m_val:,}"), unsafe_allow_html=True)
    
    st.markdown("### Data Preview")
    show(df.head(100), 320)

elif page == "Power Query (Cleaning)":
    st.subheader("Power Query & Automated Cleaning Pipeline")
    c1, c2 = st.columns(2)
    trim_spaces = c1.checkbox("Trim whitespace / blank text → missing", True)
    empty_cols = c1.checkbox("Remove entirely empty columns", False)
    
    dupes_mode = c2.selectbox("Duplicate Handling Mode", ["None", "Exact row match", "Subset column match"])
    dupes_subset = []
    if dupes_mode == "Subset column match":
        dupes_subset = c2.multiselect("Select columns for duplicate matching", list(df.columns))

    na_handling = c1.selectbox("Missing Values Imputation", ["Leave unchanged", "Fill empty cells with 0", "Drop rows with missing values", "Fill (median / most frequent)"])
    cols_to_drop = c2.multiselect("Drop Unwanted Columns", list(df.columns))

    if st.button("Execute Cleaning Pipeline", **W):
        o = {"dupes_mode": dupes_mode, "dupes_subset": dupes_subset, "trim": trim_spaces, "empty": empty_cols, "na": na_handling, "drop": cols_to_drop}
        new_df, logs = clean(df, o)
        commit(new_df, logs)
        
    if ss.log:
        st.markdown("### Cleaning Activity Log:")
        for log in ss.log: st.markdown(f"- {log}")
    show(df.head(100), 320)

elif page == "Column Renaming Studio":
    st.subheader("Column Renaming Studio")
    st.markdown("Modify column names securely across your currently loaded dataset.")
    
    ed = st.data_editor(
        pd.DataFrame({"Original Name": df.columns, "New Name": df.columns, "Lock Name": False}),
        hide_index=True,
        disabled=["Original Name"],
        key=f"col_editor_dynamic_{ss.ver}",
        **W
    )

    if st.button("Apply Column Renaming", **W):
        new_names = []
        for _, r in ed.iterrows():
            nm = r["Original Name"] if r["Lock Name"] else str(r["New Name"]).strip()
            new_names.append(nm)
        if len(set(new_names)) != len(new_names):
            st.error("Column names must be unique.")
        else:
            out = df.copy()
            out.columns = new_names
            commit(out, ["Renamed columns successfully."])

elif page == "Charts Studio (Visualizations)":
    st.subheader("Advanced Charts Studio")
    st.markdown("Explore your charts and click **'📌 Add to Dashboard'** to pin them directly to your final Executive Dashboard.")
    
    if fdf.empty:
        st.warning("No rows match active filters.")
    else:
        C, N, D, all_cols = K["cat"] + K["date"], K["num"], K["date"], list(df.columns)
        chart_choice = st.selectbox("Select Visualization Type", [
            "1. Bar Chart (Aggregated)", "2. Line Trend Chart", "3. Area Timeline", 
            "4. Pie / Donut Breakdown", "5. Box Plot (Outliers)", 
            "6. Scatter Plot (Correlation)", "7. Correlation Heatmap", "8. Geographic Map View"
        ])
        
        fig = None
        try:
            if chart_choice.startswith("1."):
                x_dim = st.selectbox("X Dimension", C if C else all_cols)
                y_met = st.selectbox("Y Metric", N if N else all_cols)
                how = st.selectbox("Aggregation", ["sum", "mean", "count"])
                g = fdf.groupby(x_dim, dropna=False)[y_met].agg(how).reset_index().head(20)
                fig = px.bar(g, x=x_dim, y=y_met, color=x_dim, color_discrete_sequence=MULTI_PALETTE, title=f"Top {x_dim} by {how} of {y_met}")
                fig.update_layout(xaxis=dict(tickangle=-35, automargin=True))
            elif chart_choice.startswith("2."):
                x_dim = st.selectbox("Date / X Dimension", D if D else (C if C else all_cols))
                y_met = st.selectbox("Y Metric", N if N else all_cols)
                if pd.api.types.is_numeric_dtype(fdf[y_met]):
                    if D:
                        fig = px.line(fdf.sort_values(x_dim), x=x_dim, y=y_met, color_discrete_sequence=MULTI_PALETTE, title=f"Trend over Time: {y_met}")
                    else:
                        g = fdf.groupby(x_dim, dropna=False)[y_met].mean().reset_index().head(20)
                        fig = px.line(g, x=x_dim, y=y_met, markers=True, color_discrete_sequence=MULTI_PALETTE, title=f"Trend Analysis of {y_met} by {x_dim}")
                else:
                    g = fdf.groupby(x_dim, dropna=False).size().reset_index(name="Count").head(20)
                    fig = px.line(g, x=x_dim, y="Count", markers=True, color_discrete_sequence=MULTI_PALETTE, title=f"Frequency Count Trend of {x_dim}")
                fig.update_layout(xaxis=dict(tickangle=-35, automargin=True))
            elif chart_choice.startswith("3."):
                x_dim = st.selectbox("Date / X Dimension", D if D else (C if C else all_cols))
                y_met = st.selectbox("Y Metric", N if N else all_cols)
                if pd.api.types.is_numeric_dtype(fdf[y_met]):
                    if D:
                        fig = px.area(fdf.sort_values(x_dim), x=x_dim, y=y_met, color_discrete_sequence=MULTI_PALETTE, title=f"Cumulative Area: {y_met}")
                    else:
                        g = fdf.groupby(x_dim, dropna=False)[y_met].sum().reset_index().head(20)
                        fig = px.area(g, x=x_dim, y=y_met, color_discrete_sequence=MULTI_PALETTE, title=f"Cumulative Area of {y_met}")
                else:
                    g = fdf.groupby(x_dim, dropna=False).size().reset_index(name="Count").head(20)
                    fig = px.area(g, x=x_dim, y="Count", color_discrete_sequence=MULTI_PALETTE, title=f"Cumulative Count Area of {x_dim}")
                fig.update_layout(xaxis=dict(tickangle=-35, automargin=True))
            elif chart_choice.startswith("4."):
                cat = st.selectbox("Category Column", C if C else all_cols)
                g = fdf[cat].value_counts().reset_index().head(10)
                g.columns = ["Label", "Count"]
                fig = px.pie(g, names="Label", values="Count", hole=0.4, color_discrete_sequence=MULTI_PALETTE, title=f"Share Distribution of {cat}")
            elif chart_choice.startswith("5."):
                cat = st.selectbox("Category Group", C if C else all_cols)
                num = st.selectbox("Numeric Metric", N if N else all_cols)
                fig = px.box(fdf, x=cat, y=num, color=cat, color_discrete_sequence=MULTI_PALETTE, title=f"Box Plot: {num} across {cat}")
                fig.update_layout(xaxis=dict(tickangle=-35, automargin=True))
            elif chart_choice.startswith("6."):
                x = st.selectbox("X Numeric", N if len(N) > 0 else all_cols)
                y = st.selectbox("Y Numeric", N if len(N) > 1 else all_cols, index=min(1, len(all_cols)-1))
                color_group = st.selectbox("Color Grouping Category (Optional)", ["(None)"] + C)
                color_arg = None if color_group == "(None)" else color_group
                fig = px.scatter(fdf, x=x, y=y, color=color_arg, color_discrete_sequence=MULTI_PALETTE, opacity=0.8, title=f"Scatter: {y} vs {x}")
            elif chart_choice.startswith("7."):
                if len(N) >= 2:
                    fig = px.imshow(fdf[N].corr(), text_auto=".2f", aspect="auto", color_continuous_scale="Tealgrn", title="Correlation Matrix Heatmap")
                else:
                    fig = px.imshow(pd.DataFrame(np.eye(len(all_cols[:5])), index=all_cols[:5], columns=all_cols[:5]), text_auto=".2f", aspect="auto", color_continuous_scale="Mint", title="Feature Relationship Heatmap")
            elif chart_choice.startswith("8."):
                if K["lat"] and K["lon"]:
                    lat_col, lon_col = K["lat"][0], K["lon"][0]
                    hover_col = st.selectbox("Hover Label Details", ["(None)"] + all_cols)
                    hover_arg = None if hover_col == "(None)" else hover_col
                    size_col = st.selectbox("Marker Size Metric (Optional)", ["(Uniform)"] + N)
                    size_arg = None if size_col == "(Uniform)" else size_col
                    
                    fig = px.scatter_geo(
                        fdf.dropna(subset=[lat_col, lon_col]),
                        lat=lat_col,
                        lon=lon_col,
                        hover_name=hover_arg,
                        size=size_arg,
                        color=hover_arg if hover_arg else None,
                        color_discrete_sequence=MULTI_PALETTE,
                        projection="natural earth",
                        title="Geographic Map View"
                    )
                    fig.update_geos(showcountries=True, countrycolor="#d1d5db", showland=True, landcolor="#f3f4f6", showocean=True, oceancolor="#e0f2fe")
                else:
                    x_dim = st.selectbox("Map X Coordinate / Category", C if C else all_cols)
                    y_met = st.selectbox("Map Intensity Metric", N if N else all_cols)
                    g = fdf.groupby(x_dim, dropna=False)[y_met].sum().reset_index().head(20)
                    fig = px.density_heatmap(g, x=x_dim, y=y_met, z=y_met, color_continuous_scale="Tealgrn", title=f"Density Heatmap: {y_met} by {x_dim}")
        except Exception as e:
            st.warning(f"Could not render chart: {e}")

        if fig is not None:
            st.plotly_chart(fig, **W)
            if st.button("📌 Add to Dashboard", key="btn_add_dashboard"):
                ss.dashboard_figs.append(fig)
                st.success("Successfully pinned this chart to your Executive Dashboard!")

        st.markdown("### Automated Insights")
        for s in insights(fdf, K, N[0] if N else None, K["cat"][0] if K["cat"] else None, K["date"][0] if K["date"] else None):
            st.markdown(f'<div class="insight-card">{s}</div>', unsafe_allow_html=True)

else:  # InsightLens Dashboard & Custom HTML Studio
    st.subheader("InsightLens Executive Dashboard & Custom HTML Studio")
    if fdf.empty: 
        st.warning("No rows match active filters.")
    else:
        dash_title = st.text_input("Customize Dashboard Title", "InsightLens Executive Business Intelligence Dashboard")
        
        mis, dup = quality(fdf)
        c1, c2, c3 = st.columns(3)
        c1.markdown(kpi("Active Records", f"{len(fdf):,}"), unsafe_allow_html=True)
        c2.markdown(kpi("Total Columns", f"{fdf.shape[1]}"), unsafe_allow_html=True)
        c3.markdown(kpi("Missing Cells", f"{mis:,}"), unsafe_allow_html=True)

        st.divider()
        st.markdown(f"### {dash_title}")
        
        C, N, D, all_cols = K["cat"] + K["date"], K["num"], K["date"], list(df.columns)
        
        if ss.dashboard_figs:
            st.markdown(f"#### Pinned Visuals ({len(ss.dashboard_figs)})")
            if st.button("Clear All Pinned Dashboard Visuals"):
                ss.dashboard_figs = []
                st.rerun()
                
            for i in range(0, len(ss.dashboard_figs), 2):
                cols = st.columns(2)
                for j in range(2):
                    idx = i + j
                    if idx < len(ss.dashboard_figs):
                        with cols[j]:
                            fig_copy = ss.dashboard_figs[idx]
                            fig_copy.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=360)
                            st.plotly_chart(fig_copy, **W)
                            
                            if st.button(f"🗑️ Remove Chart #{idx + 1}", key=f"remove_fig_{idx}"):
                                ss.dashboard_figs.pop(idx)
                                st.rerun()
        else:
            st.info("No charts pinned yet! Go to **Charts Studio (Visualizations)** tab, generate any chart, and click **'📌 Add to Dashboard'** to build your custom view.")

        st.divider()
        st.markdown("### Live Row & Data Editor")
        edited_df = st.data_editor(fdf, num_rows="dynamic", key=f"live_editor_{ss.ver}", **W)
        if not edited_df.equals(fdf):
            if st.button("Save Live Edits"):
                ss.df = edited_df.reset_index(drop=True)
                ss.ver += 1
                st.success("Changes saved successfully!")
                st.rerun()

        st.divider()
        st.markdown("### Export & HTML Dashboard Report")
        st.markdown("Download your complete dataset, Excel workbook, or fully interactive HTML dashboard containing all your pinned visuals.")
        
        e1, e2, e3 = st.columns(3)
        e1.download_button("Download CSV", fdf.to_csv(index=False).encode("utf-8"), "insightlens_export.csv", "text/csv", **W)
        try:
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                fdf.to_excel(w, sheet_name="Data", index=False)
            e2.download_button("Download Excel Workbook", buf.getvalue(), "insightlens_report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", **W)
        except Exception:
            e2.caption("Excel export requires openpyxl.")
        
        export_figures = ss.dashboard_figs if ss.dashboard_figs else [px.bar(fdf.head(10), x=all_cols[0], y=all_cols[min(1, len(all_cols)-1)] if len(all_cols)>1 else all_cols[0], color_discrete_sequence=MULTI_PALETTE, title="Overview Summary")]
        charts_html_snippets = "".join([f'<div class="card">{fig.to_html(full_html=False, include_plotlyjs="cdn")}</div>' for fig in export_figures])
        
        html_dashboard = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{dash_title}</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: {current_colors['bg']}; color: #2D3142; margin: 0; padding: 30px; }}
                .header {{ background: #fff; padding: 24px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-bottom: 24px; border-left: 6px solid {current_colors['primary']}; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
                .card {{ background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-bottom: 24px; }}
                @media(max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{dash_title}</h1>
                <p><b>Dataset Source:</b> {ss.name} &bull; <b>Active Records:</b> {len(fdf):,}</p>
            </div>
            <div class="grid">
                {charts_html_snippets}
            </div>
        </body>
        </html>"""
        e3.download_button("Download HTML Dashboard", html_dashboard.encode("utf-8"), "insightlens_dashboard.html", "text/html", **W)