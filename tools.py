import os

import requests
from dotenv import load_dotenv

load_dotenv()

# ===== API KEY（从环境变量读取，不再硬编码） =====
API_KEY = os.environ.get("BAIDU_QIANFAN_API_KEY")

# ===== 百度千帆 AI 搜索接口 =====
URL = "https://qianfan.baidubce.com/v2/ai_search/chat/completions"


class WebSearchError(Exception):
    """百度千帆 AI 搜索/LLM 调用失败或返回结构不符合预期时抛出。"""


def web_search(query: str, system_prompt: str | None = None) -> dict:
    """
    调用百度千帆 AI 搜索接口（搜索 + LLM 融合调用）。
    system_prompt 通过顶层 system 字段发送（该接口的 messages 数组要求长度为奇数，
    即只能是 user/assistant 交替、不接受把 system 塞进 messages 里）。
    """
    if not API_KEY:
        raise WebSearchError(
            "未配置 BAIDU_QIANFAN_API_KEY 环境变量，无法调用真实搜索/LLM接口。"
            "本地请在 .env 中设置，Streamlit Cloud 请在 App Settings → Secrets 中配置。"
        )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [{"role": "user", "content": query}],
        "model": "ernie-4.5-turbo-128k",
        "search_source": "baidu_search_v2",
        "search_mode": "auto",
        "max_completion_tokens": 2000,
        "stream": False,
        "response_format": {
            "type": "text"
        }
    }
    if system_prompt:
        payload["system"] = system_prompt

    try:
        # 带 search_source 的融合调用（检索 + 生成 2000 tokens）实测耗时可达 40s+，超时留足余量
        res = requests.post(URL, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
    except requests.HTTPError as exc:
        raise WebSearchError(f"调用百度千帆 API 失败（HTTP {res.status_code}）: {res.text}") from exc
    except requests.RequestException as exc:
        raise WebSearchError(f"调用百度千帆 API 失败: {exc}") from exc

    data = res.json()
    return parse_result(data)


# ===== 把百度返回结果解析为统一格式 =====
def parse_result(data: dict) -> dict:
    if not isinstance(data, dict):
        raise WebSearchError(f"搜索接口返回了非预期的数据类型: {type(data)}")

    if "choices" not in data and "code" in data:
        raise WebSearchError(
            f"搜索接口返回错误: code={data.get('code')} message={data.get('message')} "
            f"detail={data.get('detail')}"
        )

    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise WebSearchError(f"搜索接口返回结构不符合预期，无法提取 content 字段: {exc}") from exc

    return {
        "type": "web_search_result",
        "content": content,
        "references": data.get("references", []),
        "raw": data,
    }
