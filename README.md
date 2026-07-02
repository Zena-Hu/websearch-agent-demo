# 🔎 联网搜索 Agent · Demo

一个使用 Streamlit 构建的产品级联网搜索 Agent GUI 演示，UI 参考 ChatGPT / Perplexity / Notion 风格。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`。

## 部署到 Streamlit Community Cloud

见仓库根目录部署说明，或参考 [Streamlit Community Cloud 文档](https://docs.streamlit.io/deploy/streamlit-community-cloud)。

部署后即可获得形如 `https://<app-name>.streamlit.app` 的公网链接，直接分享给同事访问。

## 说明

- 搜索与 LLM 整理部分当前为模拟（mock）实现，便于直接体验完整交互流程。
- 如需接入真实能力，替换 `app.py` 中的 `run_baidu_search()` 与 `run_agent_processing()` 两个函数即可。
