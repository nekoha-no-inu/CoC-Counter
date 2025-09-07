import streamlit as st
import pandas as pd
import re
from collections import defaultdict

st.title("ログ集計アプリ（表形式改良版）")

# テキスト入力
log_text = st.text_area("ログを貼り付けてください", height=400)

# 判定結果の種類
result_types = ["決定的成功/スペシャル", "スペシャル", "成功", "失敗", "致命的失敗"]

if st.button("集計する") and log_text.strip():
    # 集計用の辞書（技能名を set で重複排除）
    players = defaultdict(lambda: {rtype: set() for rtype in result_types})
    total_counts = defaultdict(int)
    
    # ログ解析
    for line in log_text.splitlines():
        line = line.strip()
        
        # プレイヤー名の抽出
        match_name = re.search(r"\[main\]\s*(.*?)\s*:", line)
        if not match_name:
            continue
        player_name = match_name.group(1)
        
        # 技能名の抽出
        match_skill = re.search(r"【(.*?)】", line)
        skill_name = match_skill.group(1) if match_skill else "（技能名なし）"
        
        # 判定結果の抽出（行末）
        for rtype in result_types:
            if line.endswith(rtype):
                players[player_name][rtype].add(skill_name)
                total_counts[player_name] += 1
                break

    # 集計表示
    for player, data in players.items():
        st.subheader(f"プレイヤー: {player}")
        st.write(f"**判定総数:** {total_counts[player]}")

        # 件数まとめ
        summary = {rtype: len(skills) for rtype, skills in data.items()}
        df_summary = pd.DataFrame([summary], index=["件数"])
        st.table(df_summary)
        
        # 技能名まとめ
        st.write("**判定結果ごとの技能名（重複なし）**")
        skill_data = {rtype: ', '.join(skills) if skills else "なし" for rtype, skills in data.items()}
        df_skills = pd.DataFrame([skill_data], index=["技能名"])
        st.table(df_skills)
