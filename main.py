from app.llm.client import LLMClient


if __name__ == "__main__":
    client = LLMClient()
    print(client.chat("你好，帮我做个自我介绍。"))
