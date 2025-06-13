import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx, type: str = None):
        user = ctx.author
        has_mod_role = discord.utils.get(user.roles, name="Moderator") is not None

        if type is None:
            await ctx.send("Please specify one of the following: `fun`, `mod`, or `qcoins`.")
            return

        try:
            match type.lower():
                case "fun":
                    funembed = discord.Embed(title="Fun Commands", color=discord.Color.blue())
                    funembed.add_field(name="ppsize", value="Usage: !ppsize @user")
                    funembed.add_field(name="rps", value="!rps (rock|paper|scissor)")
                    funembed.add_field(name="coinflip", value="!coinflip")
                    funembed.add_field(name="meme", value="!meme")
                    funembed.set_footer(text="Fun Command Section")
                    await ctx.send(embed=funembed)

                case "mod":
                    if has_mod_role:
                        modembed = discord.Embed(title="Mod Commands", color=discord.Color.red())
                        modembed.add_field(name="clear", value="!clear <amount>")
                        modembed.add_field(name="warnings", value="!warnings @user")
                        modembed.set_footer(text="Mod Command Section")
                        await ctx.send(embed=modembed)
                    else:
                        await ctx.send("You don't have permission to view these commands.")

                case "qcoins":
                    qcoinsembed = discord.Embed(title="Qcoins Commands", color=discord.Color.gold())
                    qcoinsembed.add_field(name="coins", value="!coins @user")
                    qcoinsembed.add_field(name="qgive", value="!qgive @user <amount>")
                    qcoinsembed.add_field(name="gamble", value="!gamble <amount>")
                    qcoinsembed.add_field(name="daily", value="!daily")
                    qcoinsembed.add_field(name="leaderboard", value="!leaderboard")
                    qcoinsembed.add_field(name="shop", value="!shop")
                    qcoinsembed.add_field(name="buy", value="!buy <int>")
                    await ctx.send(embed=qcoinsembed)

                case _:
                    await ctx.send("Options are: fun, mod, qcoins.")
        except Exception as e:
            await ctx.send(f"Error occurred: {e}")
            

async def setup(bot):
            cog = Help(bot)
            await bot.add_cog(cog)
