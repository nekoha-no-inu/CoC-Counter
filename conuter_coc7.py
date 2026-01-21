import streamlit as st
import pandas as pd
import re
from collections import defaultdict

st.title("ログ集計アプリ（CoC7版・分類別対応）")

# テキスト入力
st.write("6版用：https://coc-counter.streamlit.app/")
log_text = st.text_area("ログを貼り付けてください", height=400)

# 判定結果の種類
result_types = ["＞ クリティカル", "＞ イクストリーム成功", "＞ ハード成功", "＞ レギュラー成功", "＞ 成功", "＞ 失敗", "＞ ファンブル"]

# 分類の種類
categories = ["SAN", "能力値", "技能"]

if st.button("集計する") and log_text.strip():
    # === データ構造 ===
    # プレイヤーごとに分類別の結果を記録
    players_counts = defaultdict(lambda: {cat: {rtype: [] for rtype in result_types} for cat in categories})
    players_skills = defaultdict(lambda: {cat: {rtype: set() for rtype in result_types} for cat in categories})
    total_counts = defaultdict(lambda: {cat: 0 for cat in categories})
    
    # === ログ解析 ===
    for line in log_text.splitlines():
        line = line.strip()
        
        # プレイヤー名
        match_name = re.search(r"\[main\]\s*(.*?)\s*:", line)
        if not match_name:
            continue
        player_name = match_name.group(1)
        
        # 技能名
        match_skill = re.search(r"【(.*?)】", line)
        skill_name = match_skill.group(1) if match_skill else "（技能名なし）"
        
        # 分類判定
        ability_keywords = ["STR", "CON", "POW", "DEX", "APP", "SIZ", "INT", "EDU"]
        if skill_name == "正気度ロール":
            category_type = "SAN"
        elif any(k in skill_name for k in ability_keywords):
            category_type = "能力値"
        else:
            category_type = "技能"
        
        # 判定結果
        for rtype in result_types:
            if line.endswith(rtype):
                players_counts[player_name][category_type][rtype].append(1)
                total_counts[player_name][category_type] += 1
                players_skills[player_name][category_type][rtype].add(skill_name)
                break

    # === 集計表示 ===
    for player in players_counts:
        st.subheader(f"プレイヤー: {player}")

        # 総合判定総数（すべての分類合計）
        total_all = sum(total_counts[player].values())
        st.write(f"**総合判定総数:** {total_all}")

        # 分類ごとの統計表示
        for cat in categories:
            st.markdown(f"### 🗂️ {cat}判定")
            st.write(f"**判定総数:** {total_counts[player][cat]}")

            if total_counts[player][cat] > 0:
                # 件数まとめ
                summary = {rtype: len(players_counts[player][cat][rtype]) for rtype in result_types}
                df_summary = pd.DataFrame([summary], index=["件数"])
                st.table(df_summary)

                # 技能名まとめ（重複排除）
                st.write("**判定結果ごとの技能名（重複なし）**")
                skill_data = {
                    rtype: ', '.join(sorted(players_skills[player][cat][rtype])) if players_skills[player][cat][rtype] else "なし"
                    for rtype in result_types
                }
                df_skills = pd.DataFrame([skill_data], index=["技能名"])
                st.table(df_skills)
            else:
                st.write("判定なし。")

        # 総合統計
        st.markdown("### 📊 総合（全分類合計）")
        combined_counts = {rtype: 0 for rtype in result_types}
        for cat in categories:
            for rtype in result_types:
                combined_counts[rtype] += len(players_counts[player][cat][rtype])
        df_summary_all = pd.DataFrame([combined_counts], index=["件数"])
        st.table(df_summary_all)
