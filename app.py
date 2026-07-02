"""
产品级联网搜索 Agent GUI Demo
Streamlit + 现代化 UI（ChatGPT / Perplexity / Notion 风格）

运行方式：
    streamlit run app.py

说明：
    - 搜索与 LLM 整理部分使用模拟（mock）实现，方便直接运行体验完整交互流程。
    - 如需接入真实能力，替换 run_baidu_search() 与 run_agent_processing() 两个函数即可，
      UI / 状态机部分无需改动。
"""

import time
import random
from datetime import datetime

import streamlit as st

# ============================================================
# 页面基础配置
# ============================================================
st.set_page_config(
    page_title="联网搜索 Agent · Demo",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# 全局样式（现代化卡片风格）
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* 页面整体背景：浅灰白 */
    .stApp {
        background: linear-gradient(180deg, #f7f8fa 0%, #f2f3f6 100%);
    }

    /* 隐藏默认的 Streamlit 装饰元素，去掉"老旧后台"感 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    /* 卡片容器（st.container(border=True) 渲染出的外层元素） */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
        border: 1px solid rgba(15, 23, 42, 0.08) !important;
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.05);
        background: #ffffff;
    }

    /* 标题渐变色 */
    .hero-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
        background: linear-gradient(90deg, #4f46e5, #7c3aed 55%, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub {
        text-align: center;
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 0;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.1rem;
    }
    .section-caption {
        color: #9ca3af;
        font-size: 0.82rem;
        margin-bottom: 0.6rem;
    }

    /* 输入框样式 */
    .stTextInput > div > div > input {
        border-radius: 14px !important;
        border: 1.5px solid #e5e7eb !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        background: #f9fafb !important;
        transition: all 0.15s ease-in-out;
    }
    .stTextInput > div > div > input:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.12) !important;
        background: #ffffff !important;
    }

    /* 主按钮：渐变现代风格 */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        color: #ffffff;
        border: none;
        border-radius: 999px;
        padding: 0.6rem 1.6rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        box-shadow: 0 6px 16px rgba(124, 58, 237, 0.3);
        transition: all 0.15s ease-in-out;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 22px rgba(124, 58, 237, 0.38);
    }
    div[data-testid="stButton"] > button[kind="primary"]:disabled {
        background: linear-gradient(90deg, #a5a6f6, #c4b5fd);
        box-shadow: none;
        transform: none;
        color: #f5f3ff;
    }

    /* 次要按钮（示例 chips） */
    div[data-testid="stButton"] > button[kind="secondary"] {
        border-radius: 999px;
        border: 1px solid #e5e7eb;
        background: #f9fafb;
        color: #4b5563;
        font-size: 0.8rem;
        padding: 0.25rem 0.9rem;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        border-color: #a5b4fc;
        color: #4f46e5;
        background: #eef2ff;
    }

    /* 代码块（Agent 输入）圆角处理 */
    div[data-testid="stCodeBlock"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #1f2937;
    }

    /* 结果小卡片 */
    .result-card {
        border: 1px solid #eef0f3;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.65rem;
        background: #fcfcfd;
        transition: all 0.15s ease-in-out;
    }
    .result-card:hover {
        border-color: #c7d2fe;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.08);
    }
    .result-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: #1d4ed8;
        margin-bottom: 2px;
    }
    .result-url {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-bottom: 4px;
    }
    .result-snippet {
        font-size: 0.85rem;
        color: #4b5563;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 模拟能力层：真实项目中替换为百度搜索 API / Agent 调用
# ============================================================
MOCK_DOMAINS = [
    ("知乎", "zhihu.com"),
    ("百度百科", "baike.baidu.com"),
    ("CSDN", "csdn.net"),
    ("GitHub", "github.com"),
    ("维基百科", "wikipedia.org"),
    ("36氪", "36kr.com"),
    ("少数派", "sspai.com"),
]


def run_baidu_search(query: str, n: int) -> list[dict]:
    """模拟调用百度搜索接口，返回原始搜索结果列表。"""
    time.sleep(1.0)
    results = []
    for i in range(n):
        site_name, domain = random.choice(MOCK_DOMAINS)
        results.append(
            {
                "title": f"{query} —— 相关权威解读与最新进展（{site_name}）",
                "url": f"https://{domain}/article/{random.randint(10000, 99999)}",
                "snippet": (
                    f"关于「{query}」的第 {i + 1} 条结果：本文详细梳理了背景、关键结论与"
                    f"可参考的数据来源，适合作为快速了解该主题的入口内容……"
                ),
                "source": site_name,
            }
        )
    return results


def run_agent_processing(query: str, results: list[dict]) -> str:
    """模拟 LLM 对原始搜索结果进行整理，生成可直接喂给 Agent 的结构化上下文。"""
    time.sleep(1.1)
    lines = [
        "# 联网搜索上下文（已由 Agent 整理）",
        f"query: \"{query}\"",
        f"generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"source_count: {len(results)}",
        "",
        "sources:",
    ]
    for idx, r in enumerate(results, start=1):
        lines.append(f"  - id: {idx}")
        lines.append(f"    title: \"{r['title']}\"")
        lines.append(f"    url: {r['url']}")
        lines.append(f"    summary: \"{r['snippet']}\"")
    lines += [
        "",
        "instruction: >",
        "  请基于以上 sources 中的信息回答用户问题，回答时标注引用的 source id，",
        "  若信息不足请明确说明，不要编造未出现在 sources 中的内容。",
    ]
    return "\n".join(lines)


# ============================================================
# Session State 初始化
# ============================================================
defaults = {
    "is_searching": False,
    "query_text": "",
    "pending_query": "",
    "results": None,
    "agent_input": None,
    "last_query": "",
    "elapsed": 0.0,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

EXAMPLE_QUERIES = ["2026 年 AI Agent 发展趋势", "Streamlit 最佳实践", "RAG 与联网搜索结合方案"]

# ============================================================
# 顶部：标题 + 状态说明
# ============================================================
st.markdown('<div class="hero-title">🔎 联网搜索 Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">输入问题，自动联网检索并整理为 Agent 可用的结构化上下文</div>',
    unsafe_allow_html=True,
)

col_a, col_b, col_c = st.columns([1, 1, 1])
with col_b:
    st.markdown(
        '<div style="text-align:center; margin-top:0.6rem;">'
        '<span class="status-pill">🟢 搜索引擎就绪 · Agent 引擎在线</span>'
        "</div>",
        unsafe_allow_html=True,
    )

st.write("")
st.divider()

# ============================================================
# 中间：输入卡片（居中，宽度 ~60%）
# ============================================================
left_pad, center, right_pad = st.columns([1, 3, 1])
with center:
    with st.container(border=True):
        st.markdown('<div class="section-title">💬 提出你的问题</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-caption">系统会联网搜索相关资料，并交给 Agent 整理成结构化输入</div>',
            unsafe_allow_html=True,
        )

        query_col, count_col = st.columns([4, 1.2])
        with query_col:
            query_input = st.text_input(
                "搜索内容",
                key="query_text",
                placeholder="例如：2026 年大模型 Agent 的落地方向有哪些？",
                label_visibility="collapsed",
                disabled=st.session_state.is_searching,
            )
        with count_col:
            result_count = st.selectbox(
                "结果数",
                options=[3, 5, 8],
                index=1,
                label_visibility="collapsed",
                disabled=st.session_state.is_searching,
            )

        # 示例问题 chips
        chip_cols = st.columns(len(EXAMPLE_QUERIES))
        for i, eq in enumerate(EXAMPLE_QUERIES):
            with chip_cols[i]:
                if st.button(f"✨ {eq}", key=f"chip_{i}", disabled=st.session_state.is_searching):
                    st.session_state.query_text = eq
                    st.rerun()

        st.write("")
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1.3, 1])
        with btn_col2:
            search_clicked = st.button(
                "🔎 搜索中..." if st.session_state.is_searching else "🚀 开始搜索",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.is_searching,
            )

        if search_clicked and query_input.strip():
            st.session_state.pending_query = query_input.strip()
            st.session_state.is_searching = True
            st.rerun()
        elif search_clicked and not query_input.strip():
            st.warning("⚠️ 请先输入搜索内容")

# ============================================================
# 执行搜索 + Agent 处理（two-run 状态机，确保按钮 loading 状态可见）
# ============================================================
if st.session_state.is_searching:
    q = st.session_state.pending_query
    t0 = time.time()
    with st.container():
        _, mid, _ = st.columns([1, 3, 1])
        with mid:
            with st.status(f"🔍 正在调用百度搜索「{q}」...", expanded=True) as status:
                st.write("🌐 正在连接搜索引擎并获取网页结果...")
                results = run_baidu_search(q, result_count)
                st.write(f"✅ 已获取 {len(results)} 条原始结果")

                status.update(label="🤖 正在调用 Agent 整理搜索结果...", state="running")
                st.write("🧠 正在将结果压缩为结构化上下文...")
                agent_input = run_agent_processing(q, results)
                st.write("✅ Agent 整理完成")

                status.update(label="✅ 搜索与整理已完成", state="complete", expanded=False)

    st.session_state.results = results
    st.session_state.agent_input = agent_input
    st.session_state.last_query = q
    st.session_state.elapsed = round(time.time() - t0, 2)
    st.session_state.is_searching = False
    st.rerun()

# ============================================================
# 下方：结果区域（左右分栏）
# ============================================================
if st.session_state.results:
    st.write("")
    st.divider()

    meta_col1, meta_col2, meta_col3 = st.columns([2, 1, 1])
    with meta_col1:
        st.markdown(f"##### 📌 查询：`{st.session_state.last_query}`")
    with meta_col2:
        st.caption(f"⏱ 耗时 {st.session_state.elapsed}s")
    with meta_col3:
        st.caption(f"📄 共 {len(st.session_state.results)} 条结果")

    st.write("")
    result_left, result_right = st.columns(2)

    # ---- 左侧：原始搜索结果 ----
    with result_left:
        with st.container(border=True):
            st.markdown('<div class="section-title">📚 原始搜索结果</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-caption">来自联网搜索引擎的原始网页摘要</div>',
                unsafe_allow_html=True,
            )
            for r in st.session_state.results:
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-title">🔗 {r['title']}</div>
                        <div class="result-url">{r['url']} · {r['source']}</div>
                        <div class="result-snippet">{r['snippet']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ---- 右侧：LLM 整理后的 Agent 输入 ----
    with result_right:
        with st.container(border=True):
            st.markdown('<div class="section-title">🤖 Agent 输入（已整理）</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-caption">LLM 将上方结果压缩为结构化上下文，可直接作为 Agent 的输入</div>',
                unsafe_allow_html=True,
            )
            st.code(st.session_state.agent_input, language="yaml")
else:
    st.write("")
    st.divider()
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(
            '<div style="text-align:center; color:#9ca3af; padding: 1.5rem 0;">'
            "🕊️ 还没有搜索记录，输入问题并点击「开始搜索」试试看"
            "</div>",
            unsafe_allow_html=True,
        )
