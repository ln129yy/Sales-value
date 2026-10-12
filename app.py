import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
import plotly.express as px

# 1. 取得資料庫連線密碼
DB_HOST = st.secrets["MYSQL_HOST"]
DB_PORT = st.secrets["MYSQL_PORT"]
DB_USER = st.secrets["MYSQL_USER"]
DB_PASSWORD = st.secrets["MYSQL_PASSWORD"]
DB_NAME = st.secrets["MYSQL_DB"]

# 2. 建立「F5 自動切換開關」
if os.path.exists("f5_switch.txt"):
    with open("f5_switch.txt", "r") as f:
        current_state = f.read().strip()
else:
    current_state = "updated"

if current_state == "original":
    target_csv = "sales_updated_300.csv"
    next_state = "updated"
    display_name = "更新版 (Updated 300)"
else:
    target_csv = "sales_original_300.csv"
    next_state = "original"
    display_name = "原始版 (Original 300)"

with open("f5_switch.txt", "w") as f:
    f.write(next_state)

st.title("動態銷售數據儀表板")

try:
    df_csv = pd.read_csv(target_csv, encoding='utf-8-sig')
    df_csv['net_sales'] = df_csv['unit_price'] * (df_csv['quantity'] - df_csv['returned_quantity'])
    
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    # 3. 解決 Primary Key 報錯：手動設定包含主鍵的資料表
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS sales_data"))
        conn.execute(text("""
            CREATE TABLE sales_data (
                sale_id BIGINT PRIMARY KEY,
                sale_date VARCHAR(255),
                product_id BIGINT,
                product_name VARCHAR(255),
                category VARCHAR(255),
                channel VARCHAR(255),
                unit_price BIGINT,
                quantity BIGINT,
                returned_quantity BIGINT,
                net_sales BIGINT
            )
        """))
    
    # 將資料「附加 (append)」進剛建好的表格裡
    df_csv.to_sql('sales_data', engine, if_exists='append', index=False)
    
    # 4. 從 MySQL 讀取資料來畫圖
    df_db = pd.read_sql("SELECT * FROM sales_data", engine)
    
    st.success(f"✅ F5 重新整理成功！目前 MySQL 資料庫與圖表已自動切換為：【{display_name}】")
    
    # 5. 繪製圖表
    sales_by_product = df_db.groupby('product_name')['net_sales'].sum().reset_index()
    fig = px.bar(sales_by_product, x='product_name', y='net_sales', title=f'各商品淨銷售額 - {display_name}', text_auto=True)
    st.plotly_chart(fig)

except Exception as e:
    st.error(f"發生錯誤。詳細錯誤: {e}")
