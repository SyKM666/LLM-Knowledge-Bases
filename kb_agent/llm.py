"""LLM provider abstraction — supports multiple backends via environment config.

Configuration (environment variables):
    KB_LLM_PROVIDER  — "claude-cli" | "openai" | "anthropic" | "deepseek" | "qwen"
                        | "zhipu" | "moonshot" | "doubao" | "silicon"
                        (default: "claude-cli")
    KB_LLM_MODEL     — model name, e.g. "gpt-4o", "deepseek-chat", "qwen-plus" …
    KB_LLM_BASE_URL  — custom API base URL (for Ollama, vLLM, etc.)
    KB_LLM_API_KEY   — API key (also reads OPENAI_API_KEY / ANTHROPIC_API_KEY / DEEPSEEK_API_KEY
                        / DASHSCOPE_API_KEY / ZHIPUAI_API_KEY / MOONSHOT_API_KEY
                        / ARK_API_KEY / SILICON_API_KEY as fallback)
"""

import os
import subprocess


def _get_config():
    return {
        "provider": os.environ.get("KB_LLM_PROVIDER", "claude-cli"),
        "model": os.environ.get("KB_LLM_MODEL", ""),
        "base_url": os.environ.get("KB_LLM_BASE_URL", ""),
        "api_key": os.environ.get("KB_LLM_API_KEY", ""),
    }


# ── Providers ──────────────────────────────────────────────────────────


def _call_claude_cli(system: str, prompt: str) -> str:
    cmd = ["claude", "--print", "--system-prompt", system, prompt]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI error:\n{result.stderr}")
    return result.stdout.strip()


def _call_openai_compat(system: str, prompt: str, cfg: dict) -> str:
    """OpenAI-compatible API (OpenAI, Ollama, vLLM, LiteLLM, etc.)."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "openai package required for this provider. "
            "Install it with: pip install openai"
        )

    api_key = cfg["api_key"] or os.environ.get("OPENAI_API_KEY", "")
    base_url = cfg["base_url"] or None
    model = cfg["model"] or "gpt-4o"

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content.strip()


def _call_anthropic(system: str, prompt: str, cfg: dict) -> str:
    """Native Anthropic API."""
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "anthropic package required for this provider. "
            "Install it with: pip install anthropic"
        )

    api_key = cfg["api_key"] or os.environ.get("ANTHROPIC_API_KEY", "")
    model = cfg["model"] or "claude-sonnet-4-20250514"

    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


# ── Provider presets (OpenAI-compatible Chinese LLM services) ─────────

_PRESETS: dict[str, dict[str, str]] = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "env_key": "DASHSCOPE_API_KEY",
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "model": "glm-4-plus",
        "env_key": "ZHIPUAI_API_KEY",
    },
    "moonshot": {
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-auto",
        "env_key": "MOONSHOT_API_KEY",
    },
    "doubao": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-1.5-pro-32k-250115",
        "env_key": "ARK_API_KEY",
    },
    "silicon": {
        "base_url": "https://api.siliconflow.cn/v1",
        "model": "deepseek-ai/DeepSeek-V3",
        "env_key": "SILICON_API_KEY",
    },
}


# ── Public interface ───────────────────────────────────────────────────

_PROVIDERS = {
    "claude-cli": lambda s, p, _: _call_claude_cli(s, p),
    "openai": _call_openai_compat,
    "anthropic": _call_anthropic,
}


def call_llm(system: str, prompt: str) -> str:
    """Call the configured LLM provider with a system prompt and user prompt."""
    cfg = _get_config()
    provider = cfg["provider"]

    # Resolve preset aliases → openai-compatible with pre-filled defaults
    if provider in _PRESETS:
        preset = _PRESETS[provider]
        cfg["base_url"] = cfg["base_url"] or preset["base_url"]
        cfg["model"] = cfg["model"] or preset["model"]
        cfg["api_key"] = cfg["api_key"] or os.environ.get(preset["env_key"], "")
        provider = "openai"  # all presets use OpenAI-compatible API

    fn = _PROVIDERS.get(provider)
    if fn is None:
        all_names = list(_PROVIDERS) + list(_PRESETS)
        raise ValueError(
            f"Unknown provider '{cfg['provider']}'. "
            f"Supported: {', '.join(all_names)}"
        )
    return fn(system, prompt, cfg)


def call_llm_with_context(system: str, context_docs: list[str], question: str) -> str:
    """LLM call with multiple context documents prepended to the prompt."""
    context_block = "\n\n---\n\n".join(context_docs)
    prompt = (
        f"<context>\n{context_block}\n</context>\n\n"
        f"<question>\n{question}\n</question>"
    )
    return call_llm(system, prompt)
