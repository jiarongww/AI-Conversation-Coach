from __future__ import annotations

from pathlib import Path

import gradio as gr

from app.llm.client import LLMClient
from app.rag.qa_service import RAGQAService
from app.utils.logging import setup_logging

setup_logging()

llm_client = LLMClient()
_rag_cache: dict[str, RAGQAService] = {}

STYLE_HINTS = {
    "自然": "请给出自然、顺口、适合直接发出的版本。",
    "幽默": "请给出带一点幽默感、但不过火的版本。",
    "暧昧": "请给出稍微暧昧一点、但有分寸的版本。",
    "克制": "请给出克制、稳重、不显得过度主动的版本。",
}

BEAUTY_IMAGE_PATH = Path("assets/beauty.jpg")
BG_IMAGE_PATH = Path("assets/background.jpg")


def build_css() -> str:
    if BG_IMAGE_PATH.exists():
        background_css = """
        body, .gradio-container {
            background-image:
                linear-gradient(135deg, rgba(255, 240, 245, 0.72), rgba(236, 253, 255, 0.72)),
                url("file=assets/background.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        """
    else:
        background_css = """
        body, .gradio-container {
            background:
                radial-gradient(circle at top left, #ffe4ef 0%, rgba(255,228,239,0.90) 18%, transparent 42%),
                radial-gradient(circle at top right, #dff7ff 0%, rgba(223,247,255,0.82) 18%, transparent 40%),
                linear-gradient(135deg, #fff7fb 0%, #f5fbff 100%);
            background-attachment: fixed;
        }
        """

    return f"""
    {background_css}

    :root {{
        --card-bg: rgba(255, 255, 255, 0.72);
        --card-border: rgba(255, 255, 255, 0.56);
        --text-main: #1f2937;
        --text-soft: #6b7280;
        --shadow: 0 18px 45px rgba(15, 23, 42, 0.10);
    }}

    .gradio-container {{
        max-width: 1220px !important;
        margin: 0 auto !important;
        padding-top: 18px !important;
        padding-bottom: 30px !important;
        color: var(--text-main);
    }}

    .hero-card {{
        background: linear-gradient(135deg, rgba(255,255,255,0.84), rgba(255,255,255,0.64)) !important;
        border: 1px solid rgba(255,255,255,0.68) !important;
        border-radius: 28px !important;
        box-shadow: var(--shadow) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 10px !important;
        margin-bottom: 18px !important;
    }}

    .hero-title {{
        font-size: 56px;
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: -0.03em;
        margin: 8px 0 14px 0;
        color: #1e293b;
    }}

    .hero-subtitle {{
        font-size: 16px;
        line-height: 1.9;
        color: var(--text-soft);
        margin-bottom: 12px;
    }}

    .tag-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 14px;
        margin-bottom: 14px;
    }}

    .hero-tag {{
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.80);
        border: 1px solid rgba(255,255,255,0.88);
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
        font-size: 13px;
        color: #374151;
        font-weight: 600;
    }}

    .slogan-card {{
        margin-top: 16px;
        padding: 18px 20px;
        border-radius: 22px;
        background: rgba(255,255,255,0.62);
        border: 1px solid rgba(255,255,255,0.75);
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06);
    }}

    .cute-line {{
        font-size: 18px;
        line-height: 2.0;
        color: #374151;
        margin: 0;
        font-weight: 700;
    }}

    .cute-highlight {{
        color: #ec4899;
        background: linear-gradient(90deg, rgba(244,114,182,0.14), rgba(251,207,232,0.28));
        padding: 2px 10px;
        border-radius: 999px;
        display: inline-block;
        margin: 0 2px;
        box-shadow: 0 6px 16px rgba(244,114,182,0.15);
    }}

    .hero-image-panel {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }}

    #beauty-img {{
        background: transparent !important;
        border: none !important;
    }}

    #beauty-img img {{
        background: transparent !important;
        filter: drop-shadow(0px 20px 40px rgba(0,0,0,0.18));
    }}

    .panel-card {{
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 24px !important;
        box-shadow: var(--shadow) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 18px !important;
    }}

    .main-panel {{
        min-height: 620px;
    }}

    .section-title {{
        font-size: 21px;
        font-weight: 800;
        margin-bottom: 2px;
        margin-left: 10px;
    }}

    .section-caption {{
        color: var(--text-soft);
        font-size: 14px;
        margin-bottom: 12px;
        margin-left: 10px;
    }}

    .tips-row {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin-top: 16px;
    }}

    .tip-card {{
        background: rgba(255,255,255,0.62);
        border: 1px solid rgba(255,255,255,0.72);
        border-radius: 20px;
        padding: 14px 16px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    }}

    .tip-title {{
        font-size: 14px;
        font-weight: 800;
        margin-bottom: 4px;
    }}

    .tip-body {{
        font-size: 13px;
        color: #4b5563;
        line-height: 1.8;
    }}

    button.primary {{
        border-radius: 16px !important;
    }}

    textarea, input {{
        border-radius: 16px !important;
    }}

    @media (max-width: 900px) {{
        .hero-title {{
            font-size: 40px;
        }}

        .cute-line {{
            font-size: 16px;
        }}

        .tips-row {{
            grid-template-columns: 1fr;
        }}
    }}
    """


def get_rag_service(persist_dir: str) -> RAGQAService:
    if persist_dir not in _rag_cache:
        _rag_cache[persist_dir] = RAGQAService(
            persist_dir=persist_dir,
            mode="dating_reply",
        )
    return _rag_cache[persist_dir]


def build_user_query(message: str, style: str, multi_output: bool) -> str:
    message = message.strip()
    style_hint = STYLE_HINTS.get(style, STYLE_HINTS["自然"])

    if multi_output:
        return f"""
女生发来的话：{message}

请你扮演高情商聊天回复助手。目标是帮用户生成一条自然、有分寸、不油腻、适合真实聊天场景直接发送的回复。

要求：
- 优先自然、真诚、轻松。
- 不要过度自我感动。
- 不要查户口式追问。
- 不要太油、太土、太用力。
- 不要输出解释过程。
- 尽量口语化，像真人会发的话。
- 回复长度适中，不要太长。

风格要求：
{style_hint}

请严格按照以下格式输出：

### 情绪判断
用 1 个短词概括，例如：试探 / 冷淡 / 有兴趣 / 撒娇 / 关心 / 吐槽 / 闲聊

### 主回复
给出 1 条最推荐、最适合直接发送的回复

### 备选回复
再给出 2 条不同表达，但也适合直接发送的版本

### 避雷提醒
用 1 句话提醒这类场景最容易踩的坑
""".strip()

    return f"""
女生发来的话：{message}

请你扮演高情商聊天回复助手。目标是帮用户生成一条自然、有分寸、不油腻、适合真实聊天场景直接发送的回复。

要求：
- 优先自然、真诚、轻松。
- 不要过度自我感动。
- 不要查户口式追问。
- 不要太油、太土、太用力。
- 不要输出解释过程。
- 尽量口语化，像真人会发的话。
- 回复长度适中，不要太长。

风格要求：
{style_hint}

请只输出 1 条最推荐的回复，不要加标题，不要解释。
""".strip()


def build_rag_augmented_query(question: str, contexts: list[str]) -> str:
    if not contexts:
        return question

    context_blocks = []
    for i, text in enumerate(contexts[:3], start=1):
        content = text.strip()
        if not content:
            continue
        context_blocks.append(f"[参考资料 {i}]\n{content}")

    if not context_blocks:
        return question

    return (
        "请优先参考以下知识库内容来回答。如果参考资料与常识冲突，优先保持回复自然、礼貌、有分寸，并尽量遵循参考资料中的风格建议。\n\n"
        + "\n\n".join(context_blocks)
        + "\n\n[用户请求]\n"
        + question
    )


def chat_once(
    message: str,
    use_rag: bool,
    style: str,
    multi_output: bool,
):
    persist_dir = "./storage/dating_reply"

    if not message or not message.strip():
        yield "请先输入一句对方发来的话。"
        return

    query = build_user_query(message, style, multi_output)

    try:
        if use_rag:
            if not Path(persist_dir).exists():
                yield (
                    "RAG 索引目录不存在。\n\n"
                    f"当前路径：`{persist_dir}`\n\n"
                    "请先运行：\n"
                    "`python -m scripts.build_index --docs-dir ./data/docs --persist-dir ./storage/dating_reply`"
                )
                return

            rag_service = get_rag_service(persist_dir)
            contexts = rag_service.retrieve(query)
            augmented_query = build_rag_augmented_query(query, contexts)

            partial = ""
            for chunk in llm_client.stream_chat(augmented_query, mode="dating_reply"):
                partial += chunk
                yield partial
            return

        partial = ""
        for chunk in llm_client.stream_chat(query, mode="dating_reply"):
            partial += chunk
            yield partial

    except Exception as e:
        yield f"运行失败：{type(e).__name__}: {e}"


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="AI Conversation Coach") as demo:
        with gr.Row(elem_classes=["hero-card"]):
            with gr.Column(scale=7):
                gr.HTML(
                    """
<div class="hero-title">AI Conversation Coach</div>
<div class="hero-subtitle">
  致力于教你从“钢铁直男”化身“聊天圣手”，<br>
  一个基于 Qwen + RAG + Prompt Engineering 的高情商回复生成系统。
</div>

<div class="tag-row">
  <span class="hero-tag">高情商回复生成</span>
  <span class="hero-tag">Qwen API</span>
  <span class="hero-tag">RAG 知识检索</span>
  <span class="hero-tag">多风格输出</span>
</div>

<div class="slogan-card">
  <p class="cute-line">
    无论前端还是后端，都不如你对她的
    <span class="cute-highlight">“诡计多端”</span>
    。
  </p>
</div>
"""
                )

            with gr.Column(scale=3, elem_classes=["hero-image-panel"]):
                if BEAUTY_IMAGE_PATH.exists():
                    gr.Image(
                        value=str(BEAUTY_IMAGE_PATH),
                        show_label=False,
                        interactive=False,
                        height=300,
                        elem_id="beauty-img",
                    )
                else:
                    gr.HTML(
                        """
<div style="color:#6b7280; text-align:center; padding:24px;">
  把图片放到 <code>assets/beauty.jpg</code><br>
  右上角就会自动显示。
</div>
"""
                    )

        with gr.Row():
            with gr.Column(scale=3, elem_classes=["panel-card", "main-panel"]):
                gr.Markdown(
                    """
<div class="section-title">输入区</div>
<div class="section-caption">把对方发来的原话贴进来，系统会给你更自然、更高情商的建议。</div>
"""
                )

                message = gr.Textbox(
                    label="对方发来的话",
                    placeholder="例如：你怎么还没睡 / 你是不是对所有女生都这么会说话 / 我今天心情有点不好",
                    lines=7,
                )

                style = gr.Dropdown(
                    choices=["自然", "幽默", "暧昧", "克制"],
                    value="自然",
                    label="回复风格",
                )

                with gr.Row():
                    use_rag = gr.Checkbox(value=True, label="启用 RAG 知识库")
                    multi_output = gr.Checkbox(value=True, label="输出情绪判断和备选回复")

                with gr.Row():
                    submit_btn = gr.Button("生成回复", variant="primary")
                    clear_btn = gr.Button("清空")

            with gr.Column(scale=4, elem_classes=["panel-card", "main-panel"]):
                gr.Markdown(
                    """
<div class="section-title">生成结果</div>
<div class="section-caption">建议优先看“主回复”，再从备选回复里挑更符合你本人说话习惯的版本。</div>
"""
                )
                answer = gr.Markdown(label="生成结果")

        gr.Examples(
            examples=[
                ["你怎么还没睡"],
                ["你是不是对所有女生都这么好"],
                ["我今天心情有点不好"],
                ["你最近怎么回我这么慢"],
                ["我刚到家"],
                ["今天好累啊"],
            ],
            inputs=[message],
        )

        gr.HTML(
            """
<div class="tips-row">
  <div class="tip-card">
    <div class="tip-title">自然版</div>
    <div class="tip-body">适合大多数真实聊天场景，优先顺口、像人话、不装。</div>
  </div>
  <div class="tip-card">
    <div class="tip-title">幽默版</div>
    <div class="tip-body">适合熟一点、有来回互动的场景，重点是轻松，不是硬抖机灵。</div>
  </div>
  <div class="tip-card">
    <div class="tip-title">暧昧版</div>
    <div class="tip-body">适合对方明显有互动意愿时小幅推进，记住“有分寸”比“有杀伤力”更重要。</div>
  </div>
</div>
"""
        )

        submit_btn.click(
            fn=chat_once,
            inputs=[message, use_rag, style, multi_output],
            outputs=[answer],
        )

        message.submit(
            fn=chat_once,
            inputs=[message, use_rag, style, multi_output],
            outputs=[answer],
        )

        clear_btn.click(
            fn=lambda: ("", ""),
            inputs=None,
            outputs=[message, answer],
        )

    return demo


if __name__ == "__main__":
    demo = build_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        css=build_css(),
        theme=gr.themes.Soft(),
    )
