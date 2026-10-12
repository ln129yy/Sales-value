import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import plotly.express as px

# 1. 取得資料庫連線密碼
DB_HOST = st.secrets["MYSQL_HOST"]
DB_PORT = st.secrets["MYSQL_PORT"]
DB_USER = st.secrets["MYSQL_USER"]
DB_PASSWORD = st.secrets["MYSQL_PASSWORD"]
DB_NAME = st.secrets["MYSQL_DB"]

# 2. 建立「F5 自動切換開關」 (每次按 F5 重新整理，它就會自動換邊)
if os.path.exists("f5_switch.txt"):
    with open("f5_switch.txt", "r") as f:
        current_state = f.read().strip()
else:
    current_state = "updated"

# 決定這次 F5 要切換成哪一份資料
if current_state == "original":
    target_csv = "sales_updated_300.csv"
    next_state = "updated"
    display_name = "更新版 (Updated 300)"
else:
    target_csv = "sales_original_300.csv"
    next_state = "original"
    display_name = "原始版 (Original 300)"

# 記住下一次的狀態
with open("f5_switch.txt", "w") as f:
    f.write(next_state)

st.title("動態銷售數據儀表板")

try:
    # 3. 背景自動將資料覆寫進 MySQL (達成老師要求，不須手動動作)
    df_csv = pd.read_csv(target_csv, encoding='utf-8-sig')
    df_csv['net_sales'] = df_csv['unit_price'] * (df_csv['quantity'] - df_csv['returned_quantity'])
    
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    df_csv.to_sql('sales_data', engine, if_exists='replace', index=False)
    
    # 4. 從 MySQL 讀取資料來畫圖
    df_db = pd.read_sql("SELECT * FROM sales_data", engine)
    
    st.success(f"✅ F5 重新整理成功！目前 MySQL 資料庫與圖表已切換為：【{display_name}】")
    
    # 5. 繪製圖表
    sales_by_product = df_db.groupby('product_name')['net_sales'].sum().reset_index()
    fig = px.bar(sales_by_product, x='product_name', y='net_sales', title=f'各商品淨銷售額 - {display_name}', text_auto=True)
    st.plotly_chart(fig)

except Exception as e:
    st.error(f"發生錯誤，請確認儲存庫內是否有 {target_csv} 檔案。詳細錯誤: {e}")
