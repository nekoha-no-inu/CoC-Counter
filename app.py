import streamlit as st
import pandas as pd
import re
from collections import defaultdict

st.title("ログ集計アプリ")

# 1. テキスト入力
log_text = st.text_area("ログを貼り付けてください", height=400)

# 判定結果の種類
result_types = ["決定的成功/スペシャル", "スペシャル", "成功", "失敗", "致命的失敗"]

if st.button("集計する") and log_text.strip():
    # 集計用の辞書
    players = defaultdict(lambda: {rtype: [] for rtype in result_types})
    
    # ログを1行ずつ処理
    for line in log_text.splitlines():
        line = line.strip()
        
        # プレイヤー名の抽出
        match_name = re.search(r"\[main\]\s*(.*?)\s*:", line)
        if not match_name:
            continue
        player_name = match_name.group(1)
        
        # 技能名の抽出（【】内）
        match_skill = re.search(r"【(.*?)】", line)
        skill_name = match_skill.group(1) if match_skill else None
        
        # 判定結果の抽出（行末）
        for rtype in result_types:
            if line.endswith(rtype):
                if skill_name:
                    players[player_name][rtype].append(skill_name)
                else:
                    players[player_name][rtype].append("（技能名なし）")
                break

    # 集計表示
    for player, data in players.items():
        st.subheader(f"プレイヤー: {player}")
        summary = {rtype: len(skills) for rtype, skills in data.items()}
        st.write("判定結果の件数")
        st.table(pd.DataFrame(list(summary.items()), columns=["判定結果", "件数"]))
        
        st.write("判定結果ごとの技能名")
        for rtype, skills in data.items():
            st.write(f"**{rtype}**: {', '.join(skills) if skills else 'なし'}")
