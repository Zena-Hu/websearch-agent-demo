# agent.py
# 统一入口：query -> need_search -> 加载 prompt.txt -> tools.web_search（真实搜索 + LLM 融合调用）-> 结构化结果

from pathlib import Path

import tools

PROMPT_PATH = Path(__file__).parent / "prompt.txt"

SEARCH_KEYWORDS = [
    "汇率", "价格", "最新", "今天", "现在", "当前", "年",
    "是否", "新闻", "规定", "合规", "正确", "verify",
]


def need_search(query: str) -> bool:
    return any(k in query for k in SEARCH_KEYWORDS)


def load_system_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"未找到系统 Prompt 文件: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


def run_agent(query: str) -> dict:
    """
    query -> need_search() -> load prompt.txt -> tools.web_search()（真实 LLM 调用）-> 结构化结果

    百度千帆 AI 搜索接口本身就是"搜索 + LLM"融合调用（ernie-4.5-turbo-128k + 实时检索），
    因此这里始终会发起一次真实调用以保证每个 query 都能拿到真实回答；
    need_search() 的判断结果作为可解释性元数据一并返回，用于 GUI 展示"系统是否判断该问题
    具有实时性 / 需要联网核实"，而不是决定是否发起调用的开关。
    """
    should_search = need_search(query)
    system_prompt = load_system_prompt()

    try:
        result = tools.web_search(query, system_prompt=system_prompt)
    except tools.WebSearchError as exc:
        return {
            "query": query,
            "need_search": should_search,
            "system_prompt": system_prompt,
            "success": False,
            "error": str(exc),
            "answer": None,
            "references": [],
            "raw": None,
        }

    return {
        "query": query,
        "need_search": should_search,
        "system_prompt": system_prompt,
        "success": True,
        "error": None,
        "answer": result["content"],
        "references": result["references"],
        "raw": result["raw"],
    }
