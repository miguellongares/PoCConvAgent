import chainlit as cl
from openai.types.responses import ResponseTextDeltaEvent
from agents import Runner, SQLiteSession

from agent import agent
from tools.ingest import ingest_file


def log_item(item):
    """Debug: print reasoning, tool calls (with arguments) and tool outputs to the container log."""
    raw = item.raw_item
    if item.type == "reasoning_item":
        parts = [s.text for s in raw.summary] + [c.text for c in (raw.content or [])]
        print(f"[REASONING] {' '.join(parts) or '(empty: model returns no reasoning text)'}", flush=True)
    elif item.type == "tool_call_item":
        print(f"[TOOL CALL] {raw.name}({raw.arguments})", flush=True)
    elif item.type == "tool_call_output_item":
        print(f"[TOOL OUTPUT] {str(item.output)[:1000]}", flush=True)
    elif item.type == "message_output_item":
        print("[ANSWER] done", flush=True)


@cl.on_chat_start
async def start():
    # no db path = in-memory session, lost when the chat ends
    cl.user_session.set("session", SQLiteSession(cl.user_session.get("id")))


@cl.on_message
async def on_message(msg: cl.Message):
    # files attached to the message are added to the document store
    for f in msg.elements:
        n = await cl.make_async(ingest_file)(f.path)
        await cl.Message(content=f"Ingested `{f.name}` ({n} chunks).").send()

    session = cl.user_session.get("session")
    result = Runner.run_streamed(agent, msg.content or "Summarize the uploaded file.", session=session)
    reply = cl.Message(content="")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            await reply.stream_token(event.data.delta)
        elif event.type == "run_item_stream_event":
            log_item(event.item)
    await reply.send()
