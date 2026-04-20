import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ---------------------------------------------------------
# フォント設定（日本語対応）
# ---------------------------------------------------------
font_path = "ipaexg.ttf"
font_manager.fontManager.addfont(font_path)
plt.rcParams["font.family"] = "IPAexGothic"

# ---------------------------------------------------------
# 列名ゆれを吸収する関数
# ---------------------------------------------------------
def normalize_columns(df):
    rename_map = {
        "日付": ["日付", "にちじ", "date"],
        "種目": ["種目", "しゅもく", "event"],
        "距離": ["距離", "きょり", "distance"],
        "タイム": ["タイム", "time"],
        "長水路or短水路": ["長水路or短水路", "長短", "pool"],
        "メモ": ["メモ", "memo"]
    }
    new_cols = {}
    for col in df.columns:
        found = False
        for key, patterns in rename_map.items():
            if col in patterns:
                new_cols[col] = key
                found = True
                break
        if not found:
            new_cols[col] = col
    df = df.rename(columns=new_cols)
    return df

# ---------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------
st.title("楓果 Swimming Record Dashboard")

file_path = "楓果記録.xlsx"
sheet_name = "Sheet1"

# ---------------------------------------------------------
# データ読み込み
# ---------------------------------------------------------
data = pd.read_excel(file_path, sheet_name=sheet_name, usecols="A:F")
data = normalize_columns(data)

# ★ 日付を datetime に変換（これがないと sort_values でエラー）
data["日付"] = pd.to_datetime(data["日付"], errors="coerce")

# ---------------------------------------------------------
# 種目・距離選択
# ---------------------------------------------------------
events = sorted(data["種目"].dropna().unique())
event = st.selectbox("種目を選択", events)

distances = sorted(data[data["種目"] == event]["距離"].dropna().unique())
distance = st.selectbox("距離を選択", distances)

# ---------------------------------------------------------
# フィルタリング
# ---------------------------------------------------------
filtered = data[(data["種目"] == event) & (data["距離"] == distance)]
filtered = filtered.sort_values("日付")

# ---------------------------------------------------------
# ベストタイム（短水路・長水路を別々に表示）
# ---------------------------------------------------------
st.subheader("ベストタイム（短水路）")
best_short = data[(data["距離"] == distance) & (data["長水路or短水路"] == "短水路")]

if not best_short.empty:
    t = best_short["タイム"].min()
    d = best_short.loc[best_short["タイム"].idxmin(), "日付"]
    st.write(f"ベストタイム：**{t} 秒**")
    st.write(f"更新日：{d.date()}")
else:
    st.write("データなし")

st.subheader("ベストタイム（長水路）")
best_long = data[(data["距離"] == distance) & (data["長水路or短水路"] == "長水路")]

if not best_long.empty:
    t = best_long["タイム"].min()
    d = best_long.loc[best_long["タイム"].idxmin(), "日付"]
    st.write(f"ベストタイム：**{t} 秒**")
    st.write(f"更新日：{d.date()}")
else:
    st.write("データなし")

# ---------------------------------------------------------
# グラフ表示
# ---------------------------------------------------------
st.subheader("記録推移グラフ")

if not filtered.empty:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(filtered["日付"], filtered["タイム"], marker="o")
    ax.set_xlabel("日付")
    ax.set_ylabel("タイム（秒）")
    ax.set_title(f"{event} {distance}m の記録推移")
    ax.grid(True)
    st.pyplot(fig)
else:
    st.write("データがありません。")

# ---------------------------------------------------------
# 表示
# ---------------------------------------------------------
st.subheader("記録一覧")
st.dataframe(filtered)
