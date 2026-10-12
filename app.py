import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# 讀取密碼
DB_HOST = st.secrets["MYSQL_HOST"]
DB_PORT = st.secrets["MYSQL_PORT"]
DB_USER = st.secrets["MYSQL_USER"]
DB_PASSWORD = st.secrets["MYSQL_PASSWORD"]
DB_NAME = st.secrets["MYSQL_DB"]

# 無條件直接連線資料庫 (移除 @st.cache_data，確保 F5 絕對更新)
engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
df = pd.read_sql("SELECT * FROM sales_data", engine)

# 顯示標題與圖表
st.title("動態銷售數據儀表板")
sales_by_product = df.groupby('product_name')['net_sales'].sum().reset_index()
fig = px.bar(sales_by_product, x='product_name', y='net_sales', title='各商品淨銷售額', text_auto=True)
st.plotly_chart(fig)
