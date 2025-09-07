# app.py
import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="テキスト集計アプリ", layout="wide")
st.title("テキスト集計アプリ（キーワード自由指定）")

st.markdown("**使い方**: テキストを貼り付け、カウントしたいキーワードをカンマまたは改行で入力して「集計する」を押してください。")

text = st.text_area("テキスト（本文）", height=250, placeholder="ここに文章を貼り付けてください。")
keywords_input = st.text_area("キーワード（カンマ区切りまたは改行で複数指定）", height=80,
                             placeholder="例: 猫,犬,鳥  または\n猫\n犬\n鳥")

col1, col2 = st.columns(2)
with col1:
    case_insensitive = st.checkbox("大文字小文字を区別しない (case-insensitive)", value=True)
with col2:
    use_regex = st.checkbox("キーワードを正規表現として扱う (regex)", value=False)

if st.button("集計する"):
    if not text.strip():
        st.warning("本文のテキストを入力してください。")
    elif not keywords_input.strip():
        st.warning("キーワードを入力してください。")
    else:
        # キーワードを改行・カンマで分割してリスト化
        raw_keys = re.split(r"[,\n]+", keywords_input)
        keywords = [k.strip() for k in raw_keys if k.strip()]

        results = []
        t = text
        flags = re.MULTILINE
        if case_insensitive:
            flags |= re.IGNORECASE

        for kw in keywords:
            if use_regex:
                try:
                    matches = re.findall(kw, t, flags=flags)
                    count = len(matches)
                except re.error as e:
                    count = None
                    st.error(f"正規表現エラー: `{kw}` -> {e}")
            else:
                # 単純文字列検索（必要なら大文字小文字変換）
                if case_insensitive:
                    count = t.lower().count(kw.lower())
                else:
                    count = t.count(kw)
            results.append({"キーワード": kw, "出現回数": count})

        df = pd.DataFrame(results)
        st.subheader("集計結果")
        st.table(df)

        # CSV ダウンロード（Excelで日本語を読みやすくするため UTF-8 BOM を付ける）
        csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("CSVをダウンロード", data=csv_bytes, file_name="results.csv", mime="text/csv")
