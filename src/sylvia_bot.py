import discord
from discord import ApplicationContext
from utils.service.g4f_worker import G4FAIWorker
from utils.service.files_worker import FileWorker
from cogs.cogs import setup_cogs
import re

from discord.ext import commands


class SylviaBot(discord.Bot):

    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.ai_worker = G4FAIWorker()
        self.file_worker = FileWorker()
        self.asking_save = False
        # -
        self.saving_member_name = ""
        self.saving_member_global_name = ""
        # -
        self.memory = []
        setup_cogs(self)

    async def on_ready(self):
        print(f'⚡ Đã đăng nhập với quyền của {self.user}!')

    async def on_application_command(self, ctx: discord.ApplicationContext):
        if(ctx.author.bot):
            return
        print(f"Lệnh {ctx.command} được gọi bởi {ctx.author}")

    async def on_message(self, message):
        # if(message.guild.id != 1059304552962199663):
        #     return
        member = message.guild.get_member(message.author.id)
        if message.author.bot:
            return
        if message.content.strip() == "":
            return
        # -
        member_id = member.id
        member_name = member.name
        member_global_name = member.global_name
        # -
        if (self.asking_save == False) and not (self.file_worker.get_details(member_name)) :
            self.asking_save = True
            self.saving_member_name = f"{member_name}"
            self.saving_member_global_name = f"{member_global_name}"
            await message.channel.send(content = f"```Có vẻ như đây là lần đầu em gặp {member_global_name}, em có nên lưu người này vào bộ dữ liệu của em không?```")
        
        if(self.asking_save == True and member_id == 863589246525636640):
            text_from_kaakou = message.content.lower()
            if(("co" or "có") in text_from_kaakou):
                self.asking_save = False
                if(self.file_worker.new_details(f"{self.saving_member_name}",f"{self.saving_member_global_name}")):
                    await message.channel.send(f"Đã lưu người dùng {self.saving_member_global_name} vào bộ dữ liệu!")
                    self.saving_member_name = ""
                    self.saving_member_global_name = ""
                else:
                    print("Có lỗi")
                return

        print(f'Message from {message.author}: {message.content}')
        self.add_memory(message.content, member_name)

        response = self.ai_worker.get_chat_response(message.content, member_name, self.memory)
        # response = self.ai_worker.summary_input(message.content)
        # response = self.ai_worker.gen_personality_prompt()
        # response = self.ai_worker.guess_related(message.content, self.memory)
        
        self.add_memory(response)

        print(f'Sending response: {response}')

        # await self.play_text_from_other_file(response, member.voice.channel)
        
        await message.channel.send(content=f"```{response}```")

    def add_memory(self, message: str, member_name: str = "Sylvia"):
        message = f"[{member_name}]: {message.strip()}"
        if len(self.memory) >= 30:
            self.memory.pop(0)
        self.memory.append(message)
    
    async def play_text_from_other_file(self, text: str, channel: discord.VoiceChannel):
        text = clean_text(text)
        voice_cog = self.get_cog("VoiceCog")
        speed = min(1.35 + (len(text) / 100) * 0.25, 1.75)

        if voice_cog:
            # if not connect any voice channel yet
            if(not voice_cog._check_connected()):
                await voice_cog.auto_join_vc(channel)
            await voice_cog.tts_and_play(text, speed)

def clean_text(text: str) -> str:
    return re.sub(r'(\*\*?|"|\')', '', text)






