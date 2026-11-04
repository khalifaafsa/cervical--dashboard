import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Cervical Cancer Dashboard", layout="wide")
st.title("Cervical Cancer Screening Dashboard")
st.caption("Anonymized Register | Oct 2025")

@st.cache_data
def load():
    df = pd.read_csv("Cervical_Cancer_Register_Oct-2025_3_CLEAN.csv", low_memory=False)
    df.columns = [c.strip() for c in df.columns]
    # find real column names
    date_col = [c for c in df.columns if 'Visit Date' in c][0] if any('Visit Date' in c for c in df.columns) else df.columns[1]
    age_col = [c for c in df.columns if 'Age' in c][0] if any('Age' in c for c in df.columns) else None
    df['Visit Date'] = pd.to_datetime(df[date_col], errors='coerce', dayfirst=True)
    df['Month'] = df['Visit Date'].dt.to_period('M').astype(str)
    if age_col:
        df['Age'] = pd.to_numeric(df[age_col], errors='coerce')
    return df

df = load()

st.sidebar.header("Filters")
hiv_col = 'HIV Status' if 'HIV Status' in df.columns else df.columns[5]
visit_col = 'Visit Type' if 'Visit Type' in df.columns else df.columns[2]

hiv = st.sidebar.multiselect("HIV Status", options=df[hiv_col].dropna().unique(), default=list(df[hiv_col].dropna().unique()))
visit = st.sidebar.multiselect("Visit Type", options=df[visit_col].dropna().unique(), default=list(df[visit_col].dropna().unique()))

fdf = df[df[hiv_col].isin(hiv) & df[visit_col].isin(visit)]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Screened", len(fdf))
c2.metric("HIV Positive", int((fdf[hiv_col].astype(str).str.contains("Positive", case=False, na=False)).sum()))
c3.metric("Median Age", f"{fdf['Age'].median():.0f}" if 'Age' in fdf.columns and fdf['Age'].notna().any() else "-")
c4.metric("Months", fdf['Month'].nunique())

st.subheader("Screening by Month")
monthly = fdf.groupby('Month').size().reset_index(name='Count')
st.plotly_chart(px.bar(monthly, x='Month', y='Count'), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("By HIV Status")
    st.plotly_chart(px.pie(fdf, names=hiv_col), use_container_width=True)
with col2:
    st.subheader("By Visit Type")
    st.plotly_chart(px.pie(fdf, names=visit_col), use_container_width=True)

if 'Age' in fdf.columns:
    st.subheader("Age Distribution")
    st.plotly_chart(px.histogram(fdf, x='Age', nbins=20), use_container_width=True)

st.subheader("Data Table")
st.dataframe(fdf, use_container_width=True)
st.download_button("Download Filtered Data", fdf.to_csv(index=False), "filtered.csv")
