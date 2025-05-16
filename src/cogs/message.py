from discord.ext import commands
import discord
import os
import re
from datetime import datetime, timedelta

from cogs.defaults import default_params

class MessageCog(commands.Cog):
    '''
    Retrieve and save messages from a text channel within a date range,
    while ignoring messages from specific users and filtering out unwanted content.
    '''
    
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        # if not os.path.exists("messages"):  # Create a directory for storing messages
        #     os.makedirs("messages")

    @discord.slash_command(description="Lấy tin nhắn từ ngày X đến ngày Y", name="get_messages", **default_params)
    @discord.option("channel", type=discord.TextChannel, description="Kênh để lấy tin nhắn")
    @discord.option("start_date", type=str, description="Ngày bắt đầu (YYYY-MM-DD)")
    @discord.option("end_date", type=str, description="Ngày kết thúc (YYYY-MM-DD)")
    async def get_messages(self, ctx, channel: discord.TextChannel, start_date: str, end_date: str):
        '''Retrieve messages from a text channel within the given date range and save to a file per day'''
        try:
            # Chuyển đổi định dạng ngày
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            # Danh sách người dùng cần bỏ qua
            ignored_users = {}

            # Danh sách rỗng có sẵn 2 người để bạn thay thế sau
            allowed_users = set()

            link_pattern = re.compile(r"https?://\S+")
            custom_emoji_pattern = re.compile(r"<:\w+:\d+>")
            mention_pattern = re.compile(r"<@!?(\d+)>")  # Bắt tất cả các mention người dùng
            role_mention_pattern = re.compile(r"<@&(\d+)>")  # Bắt tất cả các mention vai trò

            current_date = start
            while current_date <= end:
                next_date = current_date + timedelta(days=1)
                file_name = f"messages/messages_{current_date.strftime('%Y-%m-%d')}.txt"

                messages = []
                user_set = set() 

                async for message in channel.history(after=current_date, before=next_date, oldest_first=True):
                    if message.author.name in ignored_users:
                        continue
                    
                    content = message.content.strip() 
                    
                    if not content or len(content) > 500:  
                        continue
                    
                    if (
                        link_pattern.search(content) or
                        custom_emoji_pattern.search(content) or  # emoji tùy chỉnh
                        mention_pattern.search(content) or  # ping
                        role_mention_pattern.search(content) or  # role
                        message.attachments  # file dinh kem
                    ):
                        continue
                    
                    # Thay thế xuống dòng thành \n
                    formatted_content = content.replace("\n", "\\n")

                    messages.append(f"[{message.author.name}]: \"{formatted_content}\"")
                    user_set.add(message.author.name)  # Ghi nhận người gửi tin

                # Chỉ lưu file nếu có ít nhất 5 tin nhắn và từ 2 người trở lên
                if len(messages) >= 5 and len(user_set) >= 2:
                    with open(file_name, "w", encoding="utf-8") as f:
                        f.write("\n".join(messages))
                
                current_date = next_date
            
            await ctx.respond("Tin nhắn đã được lưu theo ngày trong thư mục messages/")
        except ValueError:
            await ctx.respond("Ngày nhập vào không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD.")
        except Exception as err:
            print(err)
            await ctx.respond("Có lỗi xảy ra khi lấy tin nhắn.")

'''Augment inputted bot with this cog'''
def setup(bot: discord.Bot) -> None:
    bot.add_cog(MessageCog(bot))
