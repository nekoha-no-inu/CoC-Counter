import streamlit as st
import pandas as pd
import re
from collections import defaultdict

st.title("ログ集計アプリ（CoC6版）")

# テキスト入力
st.write("7版用：https://conutercoc7py-amnd7qebfctz5s6atkuapps.streamlit.app/")
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
import ast
import operator

# 安全な演算のみ許可する辞書
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

# A: 【】の直前の数字または数式
pre_skill_part = line[:match_skill.start()]
# 末尾にある「数値や式」を抽出（例: "CCB<=7*5" → "7*5"）
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
