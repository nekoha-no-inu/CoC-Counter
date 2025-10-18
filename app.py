import streamlit as st
import pandas as pd
import re
from collections import defaultdict

st.title("CoCログ集計")

# テキスト入力
log_text = st.text_area("7版用：https://conutercoc7py-amnd7qebfctz5s6atkuapps.streamlit.app/", height=400)
log_text = st.text_area("ログを貼り付けてください", height=400)

# 判定結果の種類
result_types = ["クリティカル", "成功", "失敗", "ファンブル"]

if st.button("集計する") and log_text.strip():
    # 技能名セット（重複排除）
    players_skills = defaultdict(lambda: {rtype: set() for rtype in result_types})
    # 判定総数
    total_counts = defaultdict(int)
    # 件数カウント（重複含む）
    players_counts = defaultdict(lambda: {rtype: 0 for rtype in result_types})
    
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
        if not match_skill:
            continue
        skill_name = match_skill.group(1)
        
        # A: 【】の直前の数字
        pre_skill_part = line[:match_skill.start()]
        match_A = re.search(r"(\d+)", pre_skill_part)
        if not match_A:
            continue
        A = int(match_A.group(1))
        
        # B: 最後の > と > の間の数字
        match_B_all = re.findall(r"＞\s*(\d+)\s*＞", line)
        if not match_B_all:
            continue
        B = int(match_B_all[-1])
        
        # 判定
        category = None
        if B >=1 and B <=5 and B < A:
            category = "クリティカル"
        elif B >=6 and B <=99 and B <= A:
            category = "成功"
        elif B <=95 and B > A:
            category = "失敗"
        elif B >=96 and B > A:
            category = "ファンブル"
        if category:
            players_skills[player_name][category].add(skill_name)
            players_counts[player_name][category] += 1
            total_counts[player_name] += 1
    
    # 集計表示
    for player in players_counts:
        st.subheader(f"プレイヤー: {player}")
        st.write(f"**判定総数:** {total_counts[player]}")
        
        # 件数と確率
        summary_data = {}
        for rtype in result_types:
            count = players_counts[player][rtype]
            prob = (count / total_counts[player] * 100) if total_counts[player] > 0 else 0
            summary_data[rtype] = f"{count} ({prob:.1f}%)"
        df_summary = pd.DataFrame([summary_data], index=["件数（確率）"])
        st.table(df_summary)
        
        # 技能名まとめ（重複排除）
        st.write("**判定結果ごとの技能名（重複なし）**")
        skill_data = {rtype: ', '.join(players_skills[player][rtype]) if players_skills[player][rtype] else "なし" for rtype in result_types}
        df_skills = pd.DataFrame([skill_data], index=["技能名"])
        st.table(df_skills)
