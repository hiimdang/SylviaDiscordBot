def setup_cogs(bot):

    cogs_list = [
        'voice',
        'message'
    ]

    for cog in cogs_list:
        bot.load_extension(f'cogs.{cog}')
        print(f"{cog} đã được load.")