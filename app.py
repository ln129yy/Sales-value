import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import os

# 1. 取得資料庫連線密碼 (稍後會在平台後台設定)
DB_HOST = os.environ.get("MYSQL_HOST")
DB_PORT = os.environ.get("MYSQL_PORT", "3306")
DB_USER = os.environ.get("MYSQL_USER")
DB_PASSWORD = os.environ.get("MYSQL_PASSWORD")
DB_NAME = os.environ.get("MYSQL_DB", "defaultdb")

# 2. 連線至 MySQL 讀取資料 (取消長時間快取，確保 F5 能更新)
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
    st.error(f"資料庫連線失敗，請檢查設定。詳細錯誤: {e}")
