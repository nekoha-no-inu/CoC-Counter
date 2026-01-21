import streamlit as st
import pandas as pd
import re
import ast
import operator
from collections import defaultdict

st.title("ログ集計アプリ（CoC6版・分類別対応）")

# テキスト入力
st.write("7版用：https://conutercoc7py-amnd7qebfctz5s6atkuapps.streamlit.app/")
log_text = st.text_area("ログを貼り付けてください", height=400)

# 判定結果の種類
result_types = ["クリティカル", "成功", "失敗", "ファンブル"]
# 分類の種類
categories = ["SAN", "能力値", "技能"]

# === 安全な数式評価関数 ===
allowed_ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg
}

def safe_eval(expr):
    """数字と + - * / // ** のみを安全に評価する"""
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in allowed_ops:
                raise ValueError("Unsupported operator")
            return allowed_ops[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in allowed_ops:
                raise ValueError("Unsupported unary operator")
            return allowed_ops[type(node.op)](_eval(node.operand))
        elif isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Unsupported constant")
        elif isinstance(node, ast.Num):  # Python 3.7以前
            return node.n
        else:
            raise ValueError("Unsupported expression type")

    tree = ast.parse(expr, mode='eval')
    return _eval(tree)


if st.button("集計する") and log_text.strip():
    # 各分類ごとの技能名セット・件数・判定総数
    players_skills = defaultdict(lambda: {
        cat: {rtype: set() for rtype in result_types} for cat in categories
    })
    players_counts = defaultdict(lambda: {
        cat: {rtype: 0 for rtype in result_types} for cat in categories
    })
    total_counts = defaultdict(lambda: {cat: 0 for cat in categories})
    
    # ログ解析
    for line in log_text.splitlines():
        line = line.strip()
        
        # プレイヤー名
        match_name = re.search(r"\[main\]\s*(.*?)\s*:", line)
        if not match_name:
            continue
        player_name = match_name.group(1)
        
        # 技能名
        match_skill = re.search(r"【(.*?)】", line)
        if not match_skill:
            continue
        skill_name = match_skill.group(1)
        
        # === 分類の決定 ===
        ability_keywords = ["STR", "CON", "POW", "DEX", "APP", "SIZ", "INT", "EDU"]
        if skill_name == "正気度ロール":
            category_type = "SAN"
        elif any(k in skill_name for k in ability_keywords):
            category_type = "能力値"
        else:
            category_type = "技能"
        
        # === Aの抽出（数式対応） ===
        pre_skill_part = line[:match_skill.start()]
        match_A = re.search(r"(\d[\d\+\-\*/ ]*\d?)\s*$", pre_skill_part)
        if not match_A:
            continue
        expr = match_A.group(1).strip()
        try:
            A = int(safe_eval(expr))
        except Exception:
            continue
        
        # B: 最後の > と > の間の数字
        match_B_all = re.findall(r"＞\s*(\d+)\s*＞", line)
        if not match_B_all:
            continue
        B = int(match_B_all[-1])
        
        # 判定分類
        result_type = None
        if B >= 1 and B <= 5 and B < A:
            result_type = "クリティカル"
        elif B >= 6 and B <= 99 and B <= A:
            result_type = "成功"
        elif B <= 95 and B > A:
            result_type = "失敗"
        elif B >= 96 and B > A:
            result_type = "ファンブル"
        
        if result_type:
            players_skills[player_name][category_type][result_type].add(skill_name)
            players_counts[player_name][category_type][result_type] += 1
            total_counts[player_name][category_type] += 1
    
    # === 集計表示 ===
    for player in players_counts:
        st.subheader(f"プレイヤー: {player}")
        total_all = sum(total_counts[player].values())
        st.write(f"**総合判定総数:** {total_all}")
        
        for cat in categories:
            st.markdown(f"### 🗂️ {cat}判定")
            st.write(f"**判定総数:** {total_counts[player][cat]}")
            
            # 件数と確率
            if total_counts[player][cat] > 0:
                summary_data = {}
                for rtype in result_types:
                    count = players_counts[player][cat][rtype]
                    prob = (count / total_counts[player][cat] * 100)
                    summary_data[rtype] = f"{count} ({prob:.1f}%)"
                df_summary = pd.DataFrame([summary_data], index=["件数（確率）"])
                st.table(df_summary)
            else:
                st.write("判定なし。")
            
            # 技能名まとめ
            skill_data = {
                rtype: ', '.join(sorted(players_skills[player][cat][rtype])) 
                if players_skills[player][cat][rtype] else "なし"
                for rtype in result_types
            }
            df_skills = pd.DataFrame([skill_data], index=["技能名"])
            st.table(df_skills)
        
        # --- 総合集計 ---
        st.markdown("### 📊 総合（全ての分類）")
        combined_counts = {rtype: 0 for rtype in result_types}
        for cat in categories:
            for rtype in result_types:
                combined_counts[rtype] += players_counts[player][cat][rtype]
        summary_data_all = {}
        for rtype in result_types:
            count = combined_counts[rtype]
            prob = (count / total_all * 100) if total_all > 0 else 0
            summary_data_all[rtype] = f"{count} ({prob:.1f}%)"
        df_summary_all = pd.DataFrame([summary_data_all], index=["件数（確率）"])
        st.table(df_summary_all)
