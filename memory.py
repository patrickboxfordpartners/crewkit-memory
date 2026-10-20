"""Studio memory CLI for the agent crew.

  memory remember [--no-cognify] <agent> <kind> "<text>"   kind: decision | finding | lesson | customer | code
  memory cognify                              rebuild the graph (after --no-cognify batches)
  memory recall "<question>"
  memory forget <dataset>
  memory improve
"""
import os
import sys

# Cognee reads its LLM config from env (LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, LLM_ENDPOINT).
# A host-level ANTHROPIC_BASE_URL gateway (e.g. inside Claude Code) can hijack litellm, so drop only
# the gateway routing vars; never the API key itself.
for var in ("ANTHROPIC_BASE_URL", "ANTHROPIC_CUSTOM_HEADERS"):
    os.environ.pop(var, None)

try:
    from dotenv import load_dotenv  # optional
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except Exception:
    pass

if not os.environ.get("LLM_API_KEY"):
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    fallback = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}.get(provider)
    if fallback and os.environ.get(fallback):
        os.environ["LLM_API_KEY"] = os.environ[fallback]
    elif provider != "ollama" and len(sys.argv) > 1 and sys.argv[1] not in ("-h", "--help"):
        sys.exit("memory: no LLM configured. Set LLM_PROVIDER and LLM_API_KEY (see .env.example / README).")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from datetime import datetime, timezone

logging.disable(logging.CRITICAL)

import cognee
from cognee.modules.search.types import SearchType

DATASET = "studio"


async def remember(agent: str, kind: str, text: str, cognify: bool = True) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"[{kind}] {stamp} by {agent}: {text}"
    await cognee.add(entry, dataset_name=DATASET)
    if cognify:
        await cognee.cognify(datasets=[DATASET])
    print(f"remembered: {entry}" + ("" if cognify else " (queued; run `memory cognify`)"))


async def cognify_all() -> None:
    await cognee.cognify(datasets=[DATASET])
    print("graph rebuilt")


async def recall(question: str) -> None:
    results = await cognee.search(question, query_type=SearchType.GRAPH_COMPLETION, datasets=[DATASET])
    if not results:
        print("no memory found")
        return
    for r in results:
        print(getattr(r, "search_result", r))


async def forget(dataset: str) -> None:
    await cognee.forget(dataset=dataset)
    print(f"forgot dataset: {dataset}")


async def improve() -> None:
    await cognee.improve(datasets=[DATASET])
    print("memory improved")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    cmd = args[0]
    no_cog = "--no-cognify" in args
    args = [a for a in args if a != "--no-cognify"]
    if cmd == "remember" and len(args) == 4:
        asyncio.run(remember(args[1], args[2], args[3], cognify=not no_cog))
    elif cmd == "cognify":
        asyncio.run(cognify_all())
    elif cmd == "recall" and len(args) == 2:
        asyncio.run(recall(args[1]))
    elif cmd == "forget" and len(args) == 2:
        asyncio.run(forget(args[1]))
    elif cmd == "improve":
        asyncio.run(improve())
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
