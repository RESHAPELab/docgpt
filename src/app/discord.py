import logging

import discord
from dependency_injector.wiring import Provide, inject
from langchain.text_splitter import MarkdownTextSplitter

from src.core.containers import Settings
from src.port.assistant import AssistantPort

__all__ = ("BOT",)

BOT = discord.Bot(auto_sync_commands=True)
NEW_THREAD_NAME = "New Thread"
MAX_MESSAGE_LEN = 2000


@BOT.event
async def on_ready():
    log = logging.getLogger(__name__)
    user = BOT.user
    if user is None:
        raise Exception("User not logged")
    log.debug(f"Logged in as {user} (ID: {user.id})")


@BOT.event
@inject
async def on_thread_delete(
    thread: discord.Thread,
    *,
    assistant: AssistantPort = Provide[Settings.assistant.chat],
):
    if not (thread.owner and BOT.user):
        return

    if thread.owner.id == BOT.user.id:
        assistant.clear_history(str(thread.id))


@BOT.command(description="Sends help request")
async def help_me(ctx: discord.ApplicationContext):
    try:
        channel = ctx.channel
        if channel is None:
            raise ValueError("Channel not found")
        if not isinstance(channel, discord.TextChannel):
            raise ValueError("Command origin not from a text channel")

        thread = await channel.create_thread(
            name=NEW_THREAD_NAME,
            type=discord.ChannelType.private_thread,
        )
        await thread.edit(invitable=False)
        await thread.add_user(ctx.author)

        await thread.send("May I help you?")
        await ctx.respond("Private thread create!")
    except (Exception,) as e:
        await ctx.respond(f"Error: {e}")


@BOT.command(description="Clear threads")
@inject
async def clear_my_threads(ctx: discord.ApplicationContext):
    try:
        if not isinstance(ctx.channel, discord.TextChannel):
            raise ValueError("Channel must be a text channel")

        await ctx.respond(f"Ok!")

        delete_count = 0
        for thread in ctx.channel.threads:
            members = await thread.fetch_members()
            member_ids = [m.id for m in members]
            if ctx.author.id in member_ids:
                await thread.delete()
                delete_count += 1
    except (Exception,) as e:
        await ctx.respond(f"Error: {e}")


@BOT.event
@inject
async def on_message(
    message: discord.Message,
    *,
    assistant: AssistantPort = Provide[Settings.assistant.chat],
):
    user = BOT.user
    channel = message.channel

    if (
        message.author == user
        or message.type != discord.MessageType.default
        or not isinstance(channel, discord.Thread)
    ):
        return

    # Note: for some reason message comes empty from "message" var
    user_message = await channel.fetch_message(message.id)
    message_content = user_message.clean_content

    response = assistant.prompt(message_content, session_id=str(channel.id))
    response_chunks = MarkdownTextSplitter(
        chunk_size=MAX_MESSAGE_LEN,
        chunk_overlap=0,
        strip_whitespace=False,
        keep_separator=True,
        add_start_index=True,
    ).split_text(response)

    for reply in response_chunks:
        await user_message.reply(reply)

    if channel.name.lower() == NEW_THREAD_NAME.lower():
        title = assistant.prompt(
            f"""Create a short raw string title for this history: 
            
            - question:
            {message_content}
            
            - answer:
            {response}
            
            title:"""
        )
        await channel.edit(name=title)
