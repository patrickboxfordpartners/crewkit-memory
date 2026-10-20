"""Round-trip test: write studio memories, cognify, search them back."""
import asyncio
import cognee
import logging

logging.basicConfig(level=logging.WARNING)


async def main() -> None:
    # WRITE phase - memories an agent would log during real work
    memories = [
        "Customer lexis uses Clerk for authentication, Neon PostgreSQL for data, "
        "and Vercel functions for its API. Supabase was fully removed in commit 08114e5 "
        "and must never be reintroduced.",
        "Review finding 2026-10-20: Snyk flagged a Critical esbuild issue (insecure download "
        "protocol, fixed in esbuild 0.28.1) and a High ReDoS in picomatch with no patch. "
        "Both were introduced via vite@8.3.4 through tailwindcss.",
        "Lesson learned: lexis api handlers must use VercelRequest/VercelResponse Node-style "
        "signatures and .js extensions on relative imports for the Vercel ESM runtime.",
        "Studio policy: Premium tier orders require Snyk test and snyk code test to pass "
        "before any work item can move to Done, and founder approval before deploy.",
    ]
    for m in memories:
        await cognee.add(m)
    print("added", len(memories), "memories")

    await cognee.cognify()
    print("cognified")

    # RECALL phase - what a different agent in a different session would do
    results = await cognee.search("What did the review find about esbuild and picomatch?")
    print("--- search 1 (snyk findings) ---")
    for r in results[:3]:
        print(" ", str(r)[:150])

    results = await cognee.search("What database and auth does lexis use?")
    print("--- search 2 (stack facts) ---")
    for r in results[:3]:
        print(" ", str(r)[:150])


if __name__ == "__main__":
    asyncio.run(main())
