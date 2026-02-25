"""
Executive AI Intelligence Dashboard
Snowflake Streamlit × Cortex AI — Natural Language Data Explorer
"""

import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime

# Snowflake imports (available in Streamlit in Snowflake environment)
try:
    from snowflake.snowpark.context import get_active_session
    from snowflake.cortex import Complete
    SNOWFLAKE_ENV = True
except ImportError:
    SNOWFLAKE_ENV = False

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Executive AI Dashboard",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Root Variables ── */
:root {
    --bg-base:        #0a0e1a;
    --bg-surface:     #111827;
    --bg-card:        #161d2e;
    --bg-card-hover:  #1e2740;
    --border:         rgba(99,120,255,0.18);
    --border-bright:  rgba(99,120,255,0.45);
    --accent-blue:    #6378ff;
    --accent-cyan:    #22d3ee;
    --accent-violet:  #a78bfa;
    --accent-green:   #34d399;
    --accent-amber:   #fbbf24;
    --text-primary:   #f0f4ff;
    --text-secondary: #8892b0;
    --text-muted:     #4a5568;
    --glow-blue:      0 0 32px rgba(99,120,255,0.35);
    --glow-cyan:      0 0 32px rgba(34,211,238,0.30);
    --radius-lg:      16px;
    --radius-xl:      24px;
}

/* ── Base ── */
html, body, .stApp {
    background-color: var(--bg-base) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem !important; max-width: 100% !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-surface); }
::-webkit-scrollbar-thumb { background: var(--accent-blue); border-radius: 3px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1424 0%, #0a0e1a 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* ── Text elements ── */
h1, h2, h3, h4, h5, h6 { font-family: 'Space Grotesk', sans-serif; color: var(--text-primary) !important; }
p, span, label, div { color: var(--text-primary); }

/* ── Text area ── */
.stTextArea textarea {
    background: var(--bg-card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    padding: 16px 20px !important;
    transition: border-color 0.25s, box-shadow 0.25s;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: var(--glow-blue) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: var(--text-muted) !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-blue) 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 14px 36px !important;
    width: 100% !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 24px rgba(99,120,255,0.4) !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(99,120,255,0.6) !important;
    background: linear-gradient(135deg, #7b8fff 0%, #9b6cf6 100%) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: var(--bg-card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}
.stSelectbox > div > div:hover {
    border-color: var(--accent-blue) !important;
}

/* ── Dataframe / Table ── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
}
.stDataFrame [data-testid="stDataFrameResizable"] {
    background: var(--bg-card) !important;
}

/* ── Metric ── */
[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px 24px !important;
    transition: border-color 0.25s, transform 0.2s;
}
[data-testid="stMetric"]:hover {
    border-color: var(--border-bright);
    transform: translateY(-2px);
}
[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: var(--accent-cyan) !important;
}
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; font-size: 13px !important; }
[data-testid="stMetricDelta"] { font-size: 13px !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent-blue) !important; }

/* ── Alert / Info ── */
.stAlert {
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border) !important;
}

/* ── Tab ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent-blue), #8b5cf6) !important;
    color: white !important;
}

/* ── Code block ── */
.stCodeBlock {
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPER COMPONENTS
# ─────────────────────────────────────────────

def header_html():
    """Render top navigation bar."""
    now = datetime.now().strftime("%Y年%m月%d日  %H:%M")
    st.markdown(f"""
    <div style="
        display:flex; align-items:center; justify-content:space-between;
        padding: 22px 8px 18px;
        border-bottom: 1px solid rgba(99,120,255,0.18);
        margin-bottom: 28px;
    ">
        <!-- Logo -->
        <div style="display:flex; align-items:center; gap:14px;">
            <div style="
                width:44px; height:44px; border-radius:12px;
                background: linear-gradient(135deg,#6378ff,#22d3ee);
                display:flex; align-items:center; justify-content:center;
                font-size:22px; box-shadow:0 0 24px rgba(99,120,255,0.5);
            ">◆</div>
            <div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:20px;font-weight:700;
                    background:linear-gradient(90deg,#f0f4ff,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    Executive AI Dashboard
                </div>
                <div style="font-size:11px;color:#8892b0;margin-top:1px;letter-spacing:1.5px;text-transform:uppercase;">
                    Powered by Snowflake Cortex
                </div>
            </div>
        </div>
        <!-- Right info -->
        <div style="display:flex;align-items:center;gap:24px;">
            <div style="text-align:right;">
                <div style="font-size:12px;color:#8892b0;">Last updated</div>
                <div style="font-size:13px;font-weight:600;color:#f0f4ff;">{now}</div>
            </div>
            <div style="
                width:36px;height:36px;border-radius:50%;
                background:linear-gradient(135deg,#6378ff,#a78bfa);
                display:flex;align-items:center;justify-content:center;
                font-size:15px;font-weight:700;color:white;
                box-shadow:0 0 16px rgba(99,120,255,0.4);
            ">E</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def glass_card(content_fn, title="", icon="", glow_color="blue"):
    """Render a glassmorphism card container."""
    glow_map = {
        "blue":   "rgba(99,120,255,0.25)",
        "cyan":   "rgba(34,211,238,0.20)",
        "violet": "rgba(167,139,250,0.22)",
        "green":  "rgba(52,211,153,0.20)",
        "amber":  "rgba(251,191,36,0.20)",
    }
    glow = glow_map.get(glow_color, glow_map["blue"])
    header = ""
    if title:
        header = f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
            <span style="font-size:18px;">{icon}</span>
            <span style="font-family:'Space Grotesk',sans-serif;font-size:15px;
                font-weight:600;color:#f0f4ff;letter-spacing:0.3px;">{title}</span>
        </div>
        """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg,rgba(22,29,46,0.95),rgba(17,24,39,0.90));
        border: 1px solid rgba(99,120,255,0.22);
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px {glow}, inset 0 1px 0 rgba(255,255,255,0.05);
        backdrop-filter: blur(20px);
    ">{header}</div>
    """, unsafe_allow_html=True)


def query_bubble(text: str, role: str = "user"):
    """Render a chat-style message bubble."""
    if role == "user":
        bubble_style = """
            background: linear-gradient(135deg,rgba(99,120,255,0.25),rgba(139,92,246,0.20));
            border: 1px solid rgba(99,120,255,0.35);
            margin-left: auto; margin-right: 0; text-align: left;
        """
        icon = "👤"
        label = "あなたの質問"
        label_align = "right"
    else:
        bubble_style = """
            background: linear-gradient(135deg,rgba(34,211,238,0.15),rgba(52,211,153,0.10));
            border: 1px solid rgba(34,211,238,0.30);
            margin-left: 0; margin-right: auto; text-align: left;
        """
        icon = "◆"
        label = "Cortex AI"
        label_align = "left"

    st.markdown(f"""
    <div style="
        {bubble_style}
        border-radius: 18px; padding: 16px 22px; margin: 8px 0;
        max-width: 88%; font-size: 14px; line-height: 1.7;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    ">
        <div style="font-size:11px;color:#8892b0;margin-bottom:8px;
            text-align:{label_align};letter-spacing:1px;text-transform:uppercase;">
            {icon} {label}
        </div>
        <div style="color:#f0f4ff;">{text}</div>
    </div>
    """, unsafe_allow_html=True)


def kpi_row(metrics: list[dict]):
    """Render a KPI card row. metrics = [{label, value, delta, icon, color}]"""
    cols = st.columns(len(metrics))
    color_map = {
        "blue":   "#6378ff",
        "cyan":   "#22d3ee",
        "violet": "#a78bfa",
        "green":  "#34d399",
        "amber":  "#fbbf24",
    }
    for col, m in zip(cols, metrics):
        with col:
            c = color_map.get(m.get("color", "blue"), "#6378ff")
            delta_html = ""
            if "delta" in m:
                import re as _re
                _num = _re.sub(r'[^0-9.\-]', '', str(m["delta"]).replace("+", ""))
                sign = "▲" if (float(_num) >= 0 if _num else True) else "▼"
                d_color = "#34d399" if sign == "▲" else "#f87171"
                delta_html = f'<span style="font-size:12px;color:{d_color};">{sign} {m["delta"]}</span>'
            st.markdown(f"""
            <div style="
                background:linear-gradient(135deg,rgba(22,29,46,0.95),rgba(17,24,39,0.90));
                border:1px solid rgba(99,120,255,0.20); border-radius:18px;
                padding:22px 24px; transition:all 0.2s;
                box-shadow:0 4px 24px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.04);
            ">
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;">
                    <span style="font-size:22px;">{m.get('icon','📊')}</span>
                    <div style="width:8px;height:8px;border-radius:50%;background:{c};
                        box-shadow:0 0 10px {c};"></div>
                </div>
                <div style="font-size:11px;color:#8892b0;letter-spacing:1px;
                    text-transform:uppercase;margin-bottom:8px;">{m['label']}</div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;
                    font-weight:700;color:{c};margin-bottom:6px;">{m['value']}</div>
                {delta_html}
            </div>
            """, unsafe_allow_html=True)


def thinking_animation():
    """Animated thinking indicator."""
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding:16px 20px;
        background:rgba(22,29,46,0.8);border:1px solid rgba(99,120,255,0.25);
        border-radius:16px;margin:12px 0;">
        <div style="display:flex;gap:6px;align-items:center;">
            <div style="width:8px;height:8px;border-radius:50%;background:#6378ff;
                animation:pulse 1s infinite 0s;"></div>
            <div style="width:8px;height:8px;border-radius:50%;background:#a78bfa;
                animation:pulse 1s infinite 0.2s;"></div>
            <div style="width:8px;height:8px;border-radius:50%;background:#22d3ee;
                animation:pulse 1s infinite 0.4s;"></div>
        </div>
        <span style="color:#8892b0;font-size:13px;">Cortex AI が分析中...</span>
    </div>
    <style>
    @keyframes pulse {
        0%,100%{opacity:0.3;transform:scale(0.8);}
        50%{opacity:1;transform:scale(1.2);}
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SNOWFLAKE / CORTEX BACKEND
# ─────────────────────────────────────────────

def get_session():
    """Return Snowflake session (SiS environment)."""
    if SNOWFLAKE_ENV:
        return get_active_session()
    return None


def run_cortex_complete(prompt: str, model: str = "mistral-large2") -> str:
    """
    Call Snowflake Cortex COMPLETE to interpret the user query,
    generate SQL, and return a natural language explanation.
    """
    if not SNOWFLAKE_ENV:
        return None
    try:
        session = get_session()
        result = Complete(model, prompt, session=session)
        return result
    except Exception as e:
        return f"[Cortex Error] {e}"


def execute_query(sql: str) -> pd.DataFrame:
    """Execute SQL query and return DataFrame."""
    if not SNOWFLAKE_ENV:
        return pd.DataFrame()
    try:
        session = get_session()
        return session.sql(sql).to_pandas()
    except Exception as e:
        st.error(f"クエリエラー: {e}")
        return pd.DataFrame()


def cortex_nl_to_sql(
    user_question: str,
    schema_context: str,
    model: str = "mistral-large2",
) -> dict:
    """
    Use Cortex COMPLETE to convert a natural language question to SQL.
    Returns {"sql": "...", "explanation": "..."}
    """
    system_msg = f"""あなたはSnowflakeのデータアナリストです。
以下のスキーマ情報を参考に、ユーザーの質問に答えるSQLクエリを生成してください。

【スキーマ情報】
{schema_context}

【ルール】
- Snowflake SQL 構文を使用してください
- 結果は必ず JSON 形式で返してください
- フォーマット: {{"sql": "<SQLクエリ>", "explanation": "<日本語での説明>"}}
- SQLのみを返し、マークダウンのコードブロックは不要です
"""
    full_prompt = f"{system_msg}\n\n【ユーザーの質問】\n{user_question}"
    raw = run_cortex_complete(full_prompt, model)
    if raw is None:
        return {"sql": None, "explanation": None, "raw": None}
    try:
        # Extract JSON from response
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return data
    except Exception:
        pass
    return {"sql": None, "explanation": raw, "raw": raw}


def cortex_summarize(df: pd.DataFrame, question: str, model: str = "mistral-large2") -> str:
    """Use Cortex to generate a business-friendly summary of the result."""
    if not SNOWFLAKE_ENV or df.empty:
        return None
    sample = df.head(20).to_string(index=False)
    prompt = f"""以下のデータは「{question}」という質問への回答です。
経営幹部向けに、重要な洞察を3〜5点、日本語で簡潔にまとめてください。
マークダウンの箇条書き形式で回答してください。

【データ】
{sample}
"""
    return run_cortex_complete(prompt, model)


# ─────────────────────────────────────────────
# DEMO / MOCK DATA (for non-Snowflake environments)
# ─────────────────────────────────────────────

DEMO_SCHEMAS = {
    "売上データマート": """
TABLE: DM_SALES
  SALE_DATE DATE          -- 売上日
  PRODUCT_NAME VARCHAR    -- 商品名
  CATEGORY VARCHAR        -- カテゴリ
  REGION VARCHAR          -- 地域
  SALES_AMOUNT NUMBER     -- 売上金額
  QUANTITY NUMBER         -- 販売数量
  PROFIT NUMBER           -- 利益
  SALES_REP VARCHAR       -- 担当者
""",
    "顧客データマート": """
TABLE: DM_CUSTOMER
  CUSTOMER_ID VARCHAR     -- 顧客ID
  CUSTOMER_NAME VARCHAR   -- 顧客名
  SEGMENT VARCHAR         -- セグメント（VIP/一般/新規）
  REGION VARCHAR          -- 地域
  TOTAL_PURCHASE NUMBER   -- 累計購入額
  LAST_PURCHASE_DATE DATE -- 最終購入日
  CHURN_RISK VARCHAR      -- 離脱リスク（高/中/低）
""",
    "在庫データマート": """
TABLE: DM_INVENTORY
  PRODUCT_ID VARCHAR      -- 商品ID
  PRODUCT_NAME VARCHAR    -- 商品名
  CATEGORY VARCHAR        -- カテゴリ
  STOCK_QTY NUMBER        -- 在庫数
  REORDER_POINT NUMBER    -- 発注点
  SUPPLIER VARCHAR        -- サプライヤー
  LAST_UPDATED TIMESTAMP  -- 最終更新日時
""",
    "人事データマート": """
TABLE: DM_HR
  EMPLOYEE_ID VARCHAR     -- 社員ID
  DEPARTMENT VARCHAR      -- 部署
  POSITION VARCHAR        -- 役職
  HIRE_DATE DATE          -- 入社日
  SALARY NUMBER           -- 給与
  PERFORMANCE_SCORE NUMBER -- 評価スコア(1-5)
  REGION VARCHAR          -- 勤務地
""",
}

DEMO_KPI = [
    {"label": "今月売上",    "value": "¥2.4B",  "delta": "+12.3%", "icon": "💰", "color": "cyan"},
    {"label": "アクティブ顧客", "value": "18,420", "delta": "+4.1%",  "icon": "👥", "color": "violet"},
    {"label": "粗利率",      "value": "38.7%",   "delta": "-0.8%",  "icon": "📈", "color": "green"},
    {"label": "在庫回転率",  "value": "6.2x",    "delta": "+0.5x",  "icon": "🔄", "color": "amber"},
]

DEMO_RESPONSES = {
    "default": {
        "explanation": "ご質問を分析しました。Snowflake Cortex が SQL を生成し、データマートから情報を取得します。",
        "df": pd.DataFrame({
            "月": ["2024-10", "2024-11", "2024-12", "2025-01", "2025-02"],
            "売上金額": [210000000, 195000000, 280000000, 175000000, 240000000],
            "前月比(%)": ["+5.2", "-7.1", "+43.6", "-37.5", "+37.1"],
            "利益率(%)": [37.2, 36.8, 41.3, 35.9, 38.7],
        }),
        "summary": """- **12月の売上が最高値**を記録（¥280M）、年末商戦が寄与
- **2月は回復傾向**で前月比+37.1%、施策の効果が出ている
- **利益率は38〜41%台**で安定推移、コスト管理が奏功
- **1月の落ち込み（-37.5%）**は季節要因が主因と推察
- 通期目標達成に向け **Q1の底上げ施策** が重要課題
""",
        "sql": "SELECT SALE_DATE, SUM(SALES_AMOUNT) FROM DM_SALES GROUP BY 1 ORDER BY 1;",
    }
}

EXAMPLE_QUESTIONS = [
    "今月の売上トップ10商品を教えて",
    "地域別の売上と前年同月比を分析して",
    "離脱リスクが高いVIP顧客をリストアップして",
    "在庫不足が懸念される商品を優先順位付きで表示して",
    "部門別の採用コストと離職率のトレンドを見せて",
    "粗利率が下がっているカテゴリとその原因を分析して",
]


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        # Logo section
        st.markdown("""
        <div style="padding:16px 0 24px;">
            <div style="
                background:linear-gradient(135deg,#6378ff,#22d3ee);
                border-radius:14px;padding:16px;margin-bottom:20px;
                box-shadow:0 0 28px rgba(99,120,255,0.4);
                text-align:center;
            ">
                <div style="font-size:32px;margin-bottom:6px;">◆</div>
                <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;
                    font-size:14px;letter-spacing:1px;">AI INTELLIGENCE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:11px;color:#4a5568;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;">データソース</div>', unsafe_allow_html=True)
        selected_dm = st.selectbox(
            "データマート選択",
            list(DEMO_SCHEMAS.keys()),
            label_visibility="collapsed",
        )

        st.markdown('<div style="font-size:11px;color:#4a5568;letter-spacing:1.5px;text-transform:uppercase;margin:20px 0 12px;">AI モデル</div>', unsafe_allow_html=True)
        selected_model = st.selectbox(
            "Cortex モデル",
            ["mistral-large2", "llama3.1-70b", "snowflake-arctic", "claude-3-5-sonnet"],
            label_visibility="collapsed",
        )

        st.markdown('<div style="font-size:11px;color:#4a5568;letter-spacing:1.5px;text-transform:uppercase;margin:20px 0 12px;">表示オプション</div>', unsafe_allow_html=True)
        show_sql = st.toggle("生成SQLを表示", value=False)
        show_summary = st.toggle("AIサマリー", value=True)
        show_chart = st.toggle("グラフ表示", value=True)

        st.markdown("---")

        # Connection status
        status_color = "#34d399" if SNOWFLAKE_ENV else "#fbbf24"
        status_text  = "Snowflake 接続中" if SNOWFLAKE_ENV else "デモモード"
        status_icon  = "●" if SNOWFLAKE_ENV else "◎"
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:14px 16px;
            background:rgba(22,29,46,0.8);border:1px solid rgba(99,120,255,0.18);
            border-radius:12px;">
            <span style="color:{status_color};font-size:14px;">{status_icon}</span>
            <div>
                <div style="font-size:12px;font-weight:600;color:#f0f4ff;">{status_text}</div>
                <div style="font-size:10px;color:#8892b0;">Cortex AI Ready</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div style="font-size:11px;color:#4a5568;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;">クエリ履歴</div>', unsafe_allow_html=True)

        history = st.session_state.get("query_history", [])
        if not history:
            st.markdown('<div style="font-size:13px;color:#4a5568;padding:8px;">履歴なし</div>', unsafe_allow_html=True)
        for i, h in enumerate(reversed(history[-5:])):
            st.markdown(f"""
            <div style="padding:10px 12px;background:rgba(99,120,255,0.08);
                border-left:2px solid #6378ff;border-radius:0 8px 8px 0;
                margin-bottom:8px;font-size:12px;color:#8892b0;
                cursor:pointer;line-height:1.5;">
                {h[:42]}{'…' if len(h)>42 else ''}
            </div>
            """, unsafe_allow_html=True)

        return selected_dm, selected_model, show_sql, show_summary, show_chart


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    # Session state
    if "query_history" not in st.session_state:
        st.session_state.query_history = []
    if "results" not in st.session_state:
        st.session_state.results = []

    # Auto-load demo result via ?demo=1 URL param (for screenshots / demos)
    params = st.query_params
    if params.get("demo") == "1" and not st.session_state.query_history:
        demo = DEMO_RESPONSES["default"]
        demo_q = "今月の売上トップ10商品を地域別に教えてください"
        st.session_state.query_history.append(demo_q)
        st.session_state.results.append({
            "question": demo_q,
            "sql": demo["sql"],
            "df": demo["df"],
            "summary": demo["summary"],
        })
        st.session_state["_demo_trigger"] = demo_q

    # Sidebar
    selected_dm, selected_model, show_sql, show_summary, show_chart = render_sidebar()

    # Header
    header_html()

    # ── KPI Row ──
    kpi_row(DEMO_KPI)

    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)

    # ── Main tabs ──
    tab_query, tab_schema, tab_history = st.tabs(["🔍  AI クエリ", "📐  スキーマ確認", "📋  履歴"])

    # ─ Tab 1: Query ─
    with tab_query:
        col_left, col_right = st.columns([1.1, 0.9], gap="large")

        with col_left:
            st.markdown("""
            <div style="margin-bottom:20px;">
                <div style="font-family:'Space Grotesk',sans-serif;font-size:22px;
                    font-weight:700;margin-bottom:8px;
                    background:linear-gradient(90deg,#f0f4ff,#a78bfa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                    自然言語でデータを探索
                </div>
                <div style="font-size:14px;color:#8892b0;line-height:1.6;">
                    質問を入力すると Cortex AI が SQL を自動生成し、
                    データマートから情報を取得・分析します。
                </div>
            </div>
            """, unsafe_allow_html=True)

            user_input = st.text_area(
                "質問を入力",
                placeholder="例：今月の売上トップ10商品を地域別に教えてください",
                height=120,
                label_visibility="collapsed",
            )

            # Example chip buttons
            st.markdown('<div style="font-size:11px;color:#4a5568;letter-spacing:1px;text-transform:uppercase;margin:14px 0 8px;">💡 質問例</div>', unsafe_allow_html=True)
            chip_cols = st.columns(2)
            for i, ex in enumerate(EXAMPLE_QUESTIONS[:4]):
                with chip_cols[i % 2]:
                    if st.button(ex, key=f"chip_{i}", help=ex):
                        st.session_state["prefill"] = ex
                        st.rerun()

            if "prefill" in st.session_state:
                user_input = st.session_state.pop("prefill")

            submit = st.button("◆  Cortex AI に聞く", key="submit_btn")

        with col_right:
            st.markdown("""
            <div style="
                background:linear-gradient(135deg,rgba(22,29,46,0.8),rgba(17,24,39,0.7));
                border:1px solid rgba(99,120,255,0.20); border-radius:20px;
                padding:24px; height:100%;
                box-shadow:0 8px 32px rgba(0,0,0,0.3);
            ">
                <div style="font-size:11px;color:#4a5568;letter-spacing:1.5px;
                    text-transform:uppercase;margin-bottom:16px;">アーキテクチャ</div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div style="display:flex;flex-direction:column;gap:10px;">
            """ + "".join([
                f"""<div style="display:flex;align-items:center;gap:14px;
                    padding:12px 16px;border-radius:12px;
                    background:rgba({bg},0.15);border:1px solid rgba({bg},0.25);">
                    <span style="font-size:18px;">{icon}</span>
                    <div>
                        <div style="font-size:13px;font-weight:600;color:#f0f4ff;">{title}</div>
                        <div style="font-size:11px;color:#8892b0;">{desc}</div>
                    </div>
                </div>"""
                for icon, title, desc, bg in [
                    ("💬", "自然言語入力",      "テキストボックスへ質問を入力",    "99,120,255"),
                    ("🧠", "Cortex AI 解析",    f"モデル: {selected_model}",       "167,139,250"),
                    ("⚡", "SQL 自動生成",       "スキーマを考慮したクエリ生成",    "34,211,238"),
                    ("🗄️", "データマート取得",   f"{selected_dm}",                 "52,211,153"),
                    ("📊", "インサイト表示",     "グラフ・テーブル・AI要約",        "251,191,36"),
                ]
            ]) + """</div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Auto-trigger for demo mode
        auto_q = st.session_state.pop("_demo_trigger", None)
        if auto_q:
            submit = True
            user_input = auto_q

        # ── Process query ──
        if submit and user_input.strip():
            st.session_state.query_history.append(user_input.strip())
            st.markdown("---")

            # User bubble
            query_bubble(user_input.strip(), role="user")

            # Thinking animation placeholder
            thinking_placeholder = st.empty()
            with thinking_placeholder:
                thinking_animation()

            time.sleep(0.8)  # Simulate processing

            # Call Cortex or use demo data
            schema_ctx = DEMO_SCHEMAS.get(selected_dm, "")
            if SNOWFLAKE_ENV:
                result_meta = cortex_nl_to_sql(user_input, schema_ctx, selected_model)
                sql = result_meta.get("sql")
                explanation = result_meta.get("explanation", "")
                df = execute_query(sql) if sql else pd.DataFrame()
                summary = cortex_summarize(df, user_input, selected_model) if show_summary else None
            else:
                # Demo mode
                demo = DEMO_RESPONSES["default"]
                sql = demo["sql"]
                explanation = demo["explanation"]
                df = demo["df"]
                summary = demo["summary"] if show_summary else None

            thinking_placeholder.empty()

            # AI response bubble
            query_bubble(explanation or "データを取得しました。", role="assistant")

            # Store result
            st.session_state.results.append({
                "question": user_input,
                "sql": sql,
                "df": df,
                "summary": summary,
            })

            # ── Results display ──
            st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
            res_tabs = st.tabs(["📊 データ", "📝 AI サマリー", "💻 SQL"])

            with res_tabs[0]:
                if df is not None and not df.empty:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;justify-content:space-between;
                        margin-bottom:14px;">
                        <div style="font-size:13px;color:#8892b0;">
                            <span style="color:#34d399;font-weight:600;">{len(df)}</span> 件取得
                        </div>
                        <div style="font-size:11px;color:#4a5568;">
                            {selected_dm} より
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.dataframe(df, use_container_width=True, hide_index=True)

                    if show_chart and len(df) > 1:
                        numeric_cols = df.select_dtypes(include='number').columns.tolist()
                        str_cols     = df.select_dtypes(include='object').columns.tolist()
                        if numeric_cols:
                            st.markdown("<div style='margin-top:20px;font-size:11px;color:#4a5568;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;'>グラフ</div>", unsafe_allow_html=True)
                            chart_df = df.set_index(str_cols[0]) if str_cols else df
                            st.bar_chart(chart_df[numeric_cols[0]], color="#6378ff", use_container_width=True)
                else:
                    st.info("データが取得できませんでした。質問を言い換えてみてください。")

            with res_tabs[1]:
                if summary:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,rgba(34,211,238,0.10),rgba(52,211,153,0.07));
                        border:1px solid rgba(34,211,238,0.25);border-radius:16px;padding:24px;">
                        <div style="font-size:11px;color:#22d3ee;letter-spacing:1.5px;
                            text-transform:uppercase;margin-bottom:16px;">◆ Cortex AI インサイト</div>
                    """, unsafe_allow_html=True)
                    st.markdown(summary)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("AIサマリーはサイドバーでオンにできます。")

            with res_tabs[2]:
                if sql and show_sql:
                    st.code(sql, language="sql")
                elif sql:
                    st.info("SQLの表示はサイドバーで「生成SQLを表示」をオンにしてください。")
                else:
                    st.info("SQL が生成されませんでした。")

        elif submit:
            st.warning("質問を入力してください。")

    # ─ Tab 2: Schema ─
    with tab_schema:
        st.markdown(f"""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:600;
            margin-bottom:20px;color:#f0f4ff;">
            📐 {selected_dm} — スキーマ定義
        </div>
        """, unsafe_allow_html=True)
        schema_text = DEMO_SCHEMAS.get(selected_dm, "スキーマ情報がありません")
        st.code(schema_text, language="sql")

        if SNOWFLAKE_ENV:
            st.markdown("---")
            st.markdown('<div style="font-size:12px;color:#8892b0;">Snowflake から実際のスキーマを取得するには INFORMATION_SCHEMA を参照してください。</div>', unsafe_allow_html=True)

    # ─ Tab 3: History ─
    with tab_history:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:600;
            margin-bottom:20px;color:#f0f4ff;">📋 クエリ履歴</div>
        """, unsafe_allow_html=True)
        history = st.session_state.get("query_history", [])
        if not history:
            st.info("まだ質問がありません。AIクエリタブで質問してみましょう。")
        else:
            for i, q in enumerate(reversed(history)):
                st.markdown(f"""
                <div style="display:flex;align-items:flex-start;gap:14px;
                    padding:16px 20px;margin-bottom:10px;
                    background:rgba(22,29,46,0.8);
                    border:1px solid rgba(99,120,255,0.18);border-radius:14px;">
                    <div style="min-width:28px;height:28px;border-radius:8px;
                        background:linear-gradient(135deg,#6378ff,#a78bfa);
                        display:flex;align-items:center;justify-content:center;
                        font-size:12px;font-weight:700;color:white;">{len(history)-i}</div>
                    <div style="font-size:14px;color:#f0f4ff;line-height:1.5;">{q}</div>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🗑️  履歴をクリア"):
                st.session_state.query_history = []
                st.session_state.results = []
                st.rerun()

    # ── Footer ──
    st.markdown("""
    <div style="margin-top:48px;padding-top:24px;
        border-top:1px solid rgba(99,120,255,0.12);
        display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:12px;color:#4a5568;">
            © 2025 Executive AI Dashboard — Powered by
            <span style="color:#6378ff;font-weight:600;">Snowflake Cortex</span>
        </div>
        <div style="display:flex;gap:16px;">
            <span style="font-size:11px;color:#4a5568;padding:4px 12px;
                border:1px solid rgba(99,120,255,0.15);border-radius:20px;">
                Streamlit in Snowflake
            </span>
            <span style="font-size:11px;color:#4a5568;padding:4px 12px;
                border:1px solid rgba(99,120,255,0.15);border-radius:20px;">
                Cortex AI
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
