import discord
from discord.ext import commands
import tokens  # Ensure you have tokens.py with your bot tokens
import asyncio
import os

intents = discord.Intents.default()
intents.typing = False
intents.presences = True
intents.members = True
intents.message_content = True

bots = []
FFMPEG_PATH = "ffmpeg"  # Path to FFmpeg, if it's not in your PATH, put the full path here.
AUDIO_DIR = "sounds/"  # Directory where all sound files are stored (e.g., sounds/sound1.mp3, sounds/sound2.mp3)

# Function to register events and commands for each bot
def register_bot_events_and_commands(bot):
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user.name}')
    
    @bot.command()
    async def raid(ctx, channel_name: str, sound_key: str):
        guild = ctx.guild
        channel = discord.utils.get(guild.voice_channels, name=channel_name)
        sound_file = os.path.join(AUDIO_DIR, f"{sound_key}.mp3")  # Build path to sound file based on the key

        if not os.path.exists(sound_file):
            await ctx.send(f'Sound file for key "{sound_key}" not found!')
            return

        if channel:
            voice_client = await channel.connect()

            # Play audio in loop
            async def play_audio_in_loop():
                while True:
                    if not voice_client.is_playing():
                        source = discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=sound_file)
                        voice_client.play(source)
                    await asyncio.sleep(1)  # Small sleep to prevent busy-waiting loop

            bot.loop.create_task(play_audio_in_loop())
            await ctx.send(f'Bot joined {channel_name} and started looping "{sound_key}" sound!')
        else:
            await ctx.send(f'Channel {channel_name} not found!')

    @bot.command()
    async def stop(ctx):
        voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.send("Bot has disconnected from the voice channel.")
        else:
            await ctx.send("Bot is not connected to any voice channel.")

# Create bot instances and register events/commands for each bot
for token in tokens.TOKENS:
    bot = commands.Bot(command_prefix='!', intents=intents)
    bots.append(bot)
    register_bot_events_and_commands(bot)

# Function to run all bots
async def run_bots():
    tasks = []
    for bot, token in zip(bots, tokens.TOKENS):
        tasks.append(bot.start(token))
    await asyncio.gather(*tasks)

# Run the bots asynchronously
asyncio.run(run_bots())
