"""Studio memory CLI for the agent crew.

  memory remember <agent> <kind> "<text>"   kind: decision | finding | lesson | customer | code
  memory recall "<question>"
  memory forget <dataset>
  memory improve
"""
import os
import sys

# The Claude Code host routes Anthropic through a gateway; litellm must not inherit it.
for var in ("ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL", "ANTHROPIC_CUSTOM_HEADERS"):
    os.environ.pop(var, None)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
from datetime import datetime, timezone

logging.disable(logging.CRITICAL)

import cognee
from cognee.modules.search.types import SearchType

DATASET = "studio"


async def remember(agent: str, kind: str, text: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"[{kind}] {stamp} by {agent}: {text}"
    await cognee.add(entry, dataset_name=DATASET)
    await cognee.cognify(datasets=[DATASET])
    print(f"remembered: {entry}")


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
    if cmd == "remember" and len(args) == 4:
        asyncio.run(remember(args[1], args[2], args[3]))
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
