import streamlit as st
import pandas as pd
import re
from collections import defaultdict

st.title("ログ集計アプリ（CoC7版）")

# テキスト入力
log_text = st.text_area("ログを貼り付けてください", height=400)

# 判定結果の種類
result_types = ["＞ クリティカル", "＞ イクストリーム成功", "＞ ハード成功", "＞ レギュラー成功", "＞ 成功", "＞ 失敗", "＞ ファンブル"]

if st.button("集計する") and log_text.strip():
    # 件数は重複を許可するためリスト、技能名は重複排除のため set
    players_counts = defaultdict(lambda: {rtype: [] for rtype in result_types})
    players_skills = defaultdict(lambda: {rtype: set() for rtype in result_types})
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
        
        # 判定結果の抽出（末尾が完全一致するか確認）
        for rtype in result_types:
            if line.endswith(rtype) and (rtype != "失敗" or line.endswith("失敗") and not line.endswith("致命的失敗")):
                players_counts[player_name][rtype].append(1)
                total_counts[player_name] += 1
                players_skills[player_name][rtype].add(skill_name)
                break

    # 集計表示
    for player in players_counts:
        st.subheader(f"プレイヤー: {player}")
        st.write(f"**判定総数:** {total_counts[player]}")

        # 件数まとめ（重複を含む）
        summary = {rtype: len(players_counts[player][rtype]) for rtype in result_types}
        df_summary = pd.DataFrame([summary], index=["件数"])
        st.table(df_summary)
        
        # 技能名まとめ（重複排除）
        st.write("**判定結果ごとの技能名（重複なし）**")
        skill_data = {rtype: ', '.join(players_skills[player][rtype]) if players_skills[player][rtype] else "なし" for rtype in result_types}
        df_skills = pd.DataFrame([skill_data], index=["技能名"])
        st.table(df_skills)

