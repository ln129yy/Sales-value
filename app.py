import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# 1. 取得資料庫連線密碼
DB_HOST = st.secrets["MYSQL_HOST"]
DB_PORT = st.secrets["MYSQL_PORT"]
DB_USER = st.secrets["MYSQL_USER"]
DB_PASSWORD = st.secrets["MYSQL_PASSWORD"]
DB_NAME = st.secrets["MYSQL_DB"]

# 2. 連線至 MySQL 讀取資料 (ttl=2 代表快取只保留2秒，確保 F5 能立刻抓新資料)
@st.cache_data(ttl=2) 
def load_data():
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    df = pd.read_sql("SELECT * FROM sales_data", engine)
    return df

st.title("動態銷售數據儀表板")

try:
    df = load_data()
    st.success(f"✅ 成功從 MySQL 讀取最新資料！目前共 {len(df)} 筆。")
    
    # 繪製圖表
    sales_by_product = df.groupby('product_name')['net_sales'].sum().reset_index()
    fig = px.bar(sales_by_product, x='product_name', y='net_sales', title='各商品淨銷售額', text_auto=True)
    st.plotly_chart(fig)
    
except Exception as e:
    st.error(f"資料庫連線失敗。詳細錯誤: {e}")
