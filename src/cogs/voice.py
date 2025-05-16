from discord.ext import commands
import discord
import asyncio
import uuid
import os
from gtts import gTTS
import uuid
import subprocess

from cogs.defaults import default_params
# from cogs.defaults import default_ffmpeg_path

class NotInVCException(Exception):
    pass

class VoiceCog(commands.Cog):
    '''
    Add VC functionality for bots
    '''

    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.vc = None

        self.current_song = None
        
    # @commands.Cog.listener()
    # async def on_application_command(self, ctx: discord.ApplicationContext):
    #     print(f"Lệnh {ctx.command} được gọi bởi {ctx.author}")

    def _check_connected(self) -> bool:
        '''Return whether bot is connected to a vc'''
        return self.vc is not None and self.vc.is_connected()
    
    def _check_playing(self) -> bool:
        '''Return whether bot is playing audio in vc'''
        return self.vc.is_playing()
    
    def _stop_playing(self) -> None:
        '''Stop playing audio in vc'''
        self.vc.stop()
    
    def _remove_path(self, file_path: str) ->None:
        try:
                os.remove(file_path)  # Xóa file sau khi phát xong
        except Exception as e:
            print(f"Lỗi khi xóa file: {e}")
    
    def _play_sound(self, speed = 1.25, pitch = 1 , file_path: str = None) -> None:
        '''Play sound from file path in VC'''
        self.current_song = file_path
        # source = discord.FFmpegPCMAudio(source=file_path, options=f"-filter:a 'atempo={speed}'")
        source = discord.FFmpegPCMAudio(
            source=file_path,
            options=f"-af rubberband=pitch={pitch},atempo={speed}"
        )
        def after_playing(error):
            if error:
                print(f"Lỗi khi phát audio: {error}")
            self._remove_path(file_path)

        self.vc.play(source, after=after_playing)

    async def _disconnect_client_if_connected(self) -> bool:
        '''Disconnect bot from vc if in one and return whether bot performed a dc or not'''
        if self._check_connected():
            await self.vc.disconnect()
            return True
        else:
            return False
    
    async def auto_join_vc(self, channel: discord.VoiceChannel) -> None:
        try:
            self.vc = await channel.connect()
        except Exception as err:
            print(err)

    def _delete_current_song(self) -> None:
        '''Delete the current song file if it exists'''
        if self._check_playing():
            if self.current_song and os.path.exists(self.current_song):
                try:
                    os.remove(self.current_song)  # Xóa file nhạc
                    self.current_song = None
                except Exception as e:
                    print(f"Lỗi khi xóa file nhạc: {e}")
            return True
        else:
            return False

    @discord.slash_command(description="Join a voice channel.", name="join_vc", **default_params)
    @discord.option("channel", type=discord.channel.VoiceChannel)
    async def join_vc(self, ctx, channel: discord.VoiceChannel) -> None:
        '''Join bot to specified vc'''
        try:
            await self._disconnect_client_if_connected() # bot cannot connect if it is already in a vc
            self.vc = await channel.connect()
            await ctx.respond(f"Đã tham gia {channel}!")
        except discord.ClientException as err:
            print(err)
            await ctx.respond(f"Chuyển sang channel {channel} không thành công. Thử lại...")
            return
        except asyncio.TimeoutError as err:
            print(err)
            await ctx.respond(f"Request join {channel} quá hạn. Thử lại...")
            return
        except Exception as err:
            print(err)
            await ctx.respond(f"Lỗi khi join {channel}...")
            return

    @discord.slash_command(description="Thoát voicechannel hiện tại.", name="leave_vc", **default_params)
    async def leave_vc(self, ctx) -> None:
        '''Disconnect bot from current vc'''
        try:
            if not await self._disconnect_client_if_connected():
                raise NotInVCException()
            await ctx.respond(f"Đã thoát VC")
        except NotInVCException as err:
            print(err)
            await ctx.respond(f"Không ở trong một VC..")
            return
        except Exception as err:
            print(err)
            await ctx.respond(f"Có lỗi khi cố gắng thoát VC hiện tại...")
            return
    
    async def tts_and_play(self, text: str, speed=1.25):
        '''Chuyển văn bản thành giọng nói và phát trong VC'''
        try:
            if not self._check_connected():
                raise NotInVCException()

            while self._check_playing():
                await asyncio.sleep(0.5)

            recordings_dir = "recordings"
            os.makedirs(recordings_dir, exist_ok=True)

            file_name = f"tts_{uuid.uuid4().hex}.mp3"
            file_path = os.path.join(recordings_dir, file_name)

            tts = gTTS(text, lang="vi")
            tts.save(file_path)
            
            self._play_sound(speed= speed, pitch=1.20, file_path= file_path)

        except NotInVCException:
            pass  
        except Exception as err:
            print(err)

    async def play_music_from_url(self, url: str, speed = 1, pitch = 1) -> None:
        try:
            if not self._check_connected():
                raise NotInVCException()

            while self._check_playing():
                await asyncio.sleep(0.5)

            recordings_dir = "recordings"
            os.makedirs(recordings_dir, exist_ok=True)

            file_name = f"music_{uuid.uuid4().hex}.mp3"
            file_path = os.path.join(recordings_dir, file_name)

            command = ['yt-dlp', '--no-playlist', '--no-warnings', '-f', '140', '--audio-format', 'mp3', '-o', file_path, url]
            subprocess.run(command, check=True)

            if os.path.exists(file_path):
                self._play_sound(speed= speed, pitch= pitch, file_path= file_path)
            else:
                print(f"Không thể tải nhạc từ URL: {url}")

        except NotInVCException:
            print("Bot chưa có trong VC")
        except Exception as err:
            print(f"Có lỗi xảy ra khi cố gắng phát nhạc từ URL: {url}")
            print(err)

    @discord.slash_command(description="Bỏ qua bài hát hiện tại", name="skip_music", **default_params)
    async def skip_music(self, ctx) -> None:
        '''Bỏ qua bài hát đang phát hiện tại'''
        self._stop_playing()
        if(self._delete_current_song()):
            await ctx.respond("Đã bỏ qua bài hát hiện tại!")
        else:
            await ctx.respond("Không có bài hát nào đang phát để bỏ qua.")

    @discord.slash_command(description="Phát nhạc từ URL", name="play_music", **default_params)
    async def play_music(self, ctx, url: str) -> None:
        '''Phát nhạc từ link YouTube hoặc SoundCloud'''
        await self.play_music_from_url(url)
    
    @discord.slash_command(description="Phát văn bản dưới dạng giọng nói.", name="tts", **default_params)
    async def tts(self, ctx, text: str = "Thành bê đê lỏ") -> None:
        await self.tts_and_play(text)

    async def _record_callback(self, sink: discord.sinks.Sink) -> None:
        audio_data = sink.get_all_audio()
        for buffer_ind in range(len(audio_data)):
            with open(f"recordings/{buffer_ind}.mp3", "wb") as f:
                f.write(audio_data[buffer_ind].getbuffer())
        
    @discord.slash_command(description="Tiến hành ghi âm VC", name="record_start", **default_params)
    async def record_start(self, ctx) -> None:
        '''Start recording audio per user in current vc'''
        try:
            if not self._check_connected():
                raise NotInVCException()
            sink = discord.sinks.MP3Sink()
            self.vc.start_recording(sink, self._record_callback, sync_start=True)
            await ctx.respond(f"Tiến hành ghi âm!")
        except NotInVCException as err:
            print(err)
            await ctx.respond(f"Sylvia chưa ở trong VC.")
            return
        except discord.sinks.RecordingException as err:
            print(err)
            await ctx.respond(f"Đã ghi âm...")
        except Exception as err:
            print(err)
            await ctx.respond(f"Lỗi khi ghi âm...")
            return
        
    @discord.slash_command(description="Dừng ghi âm VC", name="record_stop", **default_params)
    async def record_stop(self, ctx) -> None:
        '''Stop recording audio in current vc'''
        try:
            if not self._check_connected():
                raise NotInVCException()
            self.vc.stop_recording()
            await ctx.respond(f"Đã dừng ghi âm!")
        except NotInVCException as err:
            print(err)
            await ctx.respond(f"Chưa ở trong VC!")
            return
        except discord.sinks.RecordingException as err:
            print(err)
            await ctx.respond(f"Còn chưa ghi âm được.")
            return
        except Exception as err:
            print(err)
            await ctx.respond(f"Có lỗi xảy ra khi cố ghi âm")
            return

'''Augment inputted bot with this cog'''
def setup(bot: discord.Bot) -> None:
    bot.add_cog(VoiceCog(bot))