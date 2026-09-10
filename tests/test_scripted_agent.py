import asyncio
from blobhell.agents import AgentAction, Observation, ScriptedAgent

def test_scripted_agent_loop():
    agent = ScriptedAgent([AgentAction("tool", "shell", {"argv": ["true"]}), AgentAction("finish", message="PASS")])
    async def go():
        await agent.start({}); a = await agent.step(Observation("task")); b = await agent.step(Observation("tool_result")); await agent.finalize(); return a, b
    first, second = asyncio.run(go())
    assert first.tool == "shell" and second.message == "PASS" and agent.finalized

