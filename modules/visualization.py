import plotly.express as px
import pydeck as pdk
import pandas as pd
import numpy as np
from colors import MULTI_PALETTE

def render_density_heatmap(df):
    lat_cols = [c for c in df.columns if any(k in c.lower() for k in ["lat", "latitude"])]
    lon_cols = [c for c in df.columns if any(k in c.lower() for k in ["lon", "lng", "longitude"])]
    
    if lat_cols and lon_cols:
        map_df = df.copy()
        map_df["lat"] = pd.to_numeric(map_df[lat_cols[0]], errors="coerce")
        map_df["lon"] = pd.to_numeric(map_df[lon_cols[0]], errors="coerce")
        map_df = map_df.dropna(subset=["lat", "lon"])
        
        if map_df.empty:
            return None, "No valid coordinate rows available for heat map rendering."
            
        layer = pdk.Layer(
            "HeatmapLayer",
            data=map_df,
            get_position=["lon", "lat"],
            radiusPixels=50,
            intensity=1,
            threshold=0.05
        )
        view_state = pdk.ViewState(
            latitude=float(map_df["lat"].mean()),
            longitude=float(map_df["lon"].mean()),
            zoom=2,
            pitch=0
        )
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=True)
        return r, None
    else:
        return None, "Dataset requires explicit Latitude and Longitude columns to render a Density Heat Map."

def get_chart(df, chart_type, x_col, y_col=None, color_col=None):
    fig = None
    if chart_type == "Bar Chart":
        agg_df = df.groupby(x_col, as_index=False)[y_col].sum() if y_col else df[x_col].value_counts().reset_index()
        agg_df.columns = [x_col, "Value"]
        fig = px.bar(agg_df.head(15), x=x_col, y="Value", color=x_col, color_discrete_sequence=MULTI_PALETTE, title=f"Bar Chart: {y_col or 'Count'} by {x_col}")
    elif chart_type == "Line Chart":
        fig = px.line(df.sort_values(by=x_col), x=x_col, y=y_col, color=color_col, color_discrete_sequence=MULTI_PALETTE, title=f"Line Chart: {y_col} over {x_col}")
    elif chart_type == "Pie Chart":
        pie_data = df[x_col].value_counts().reset_index().head(10)
        pie_data.columns = [x_col, "Count"]
        fig = px.pie(pie_data, names=x_col, values="Count", hole=0.4, color_discrete_sequence=MULTI_PALETTE, title=f"Distribution of {x_col}")
    elif chart_type == "Scatter Plot":
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, color_discrete_sequence=MULTI_PALETTE, title=f"Scatter: {y_col} vs {x_col}")
    elif chart_type == "Correlation Heatmap":
        num_df = df.select_dtypes(include=np.number)
        if len(num_df.columns) > 1:
            fig = px.imshow(num_df.corr(), text_auto=".2f", aspect="auto", color_continuous_scale="Tealgrn", title="Numeric Feature Correlation Matrix")
            
    if fig:
        fig.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=40, b=20))
    return fig