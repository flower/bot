# -*- coding: utf-8 -*-

"""
Copyright (c) 2021-present flower and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from discord.ext import commands
from utils import default, perms, _io
import discord
import ast
import sys
import time

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("./config.json")

    @commands.command(name="load", hidden=True)
    @commands.check(perms.only_owner)
    async def load_cog(self, ctx, cog):
        try:
            self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"loaded `{cog}.py`")

    @commands.command(name="unload", hidden=True)
    @commands.check(perms.only_owner)
    async def unload_cog(self, ctx, cog):
        try:
            self.bot.unload_extension(f"cogs.{cog}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"unloaded `{cog}.py`")

    @commands.command(name="reload", hidden=True)
    @commands.check(perms.only_owner)
    async def reload_cog(self, ctx, cog):
        try:
            self.bot.reload_extension(f"cogs.{cog}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"reloaded `{cog}.py`")

    @commands.command(name="kill", hidden=True)
    @commands.check(perms.only_owner)
    async def kill_bot(self, ctx):
        await ctx.send("gn")
        time.sleep(1)
        sys.exit()


    @commands.command(hidden=True)
    @commands.check(perms.only_owner)
    async def dm(self, ctx, user_id: int, *, message: str):
        """dm someone for the trollz"""
        user = self.bot.get_user(user_id)
        if not user:
            return await ctx.send(f"can't find mr **{user_id}**")
        try:
            await user.send(message)
            await ctx.send(f"messaged **{user_id}**")
        except discord.Forbidden:
            await ctx.send("he don't wanna talk :neutral_face:")

    @commands.group(name="change", hidden=True)
    @commands.check(perms.only_owner)
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @change.command(name="playing")
    @commands.check(perms.only_owner)
    async def change_playing(self, ctx, *, playing: str = None):
        if self.config.status == "idle":
            status = discord.Status.idle
        elif self.config.status == "dnd":
            status = discord.Status.dnd
        else:
            status = discord.Status.online

        if self.config.playing_type == "listening":
            playing_type = 2
        elif self.config.playing_type == "watching":
            playing_type = 3
        else:
            playing_type = 0

        try:
            await self.bot.change_presence(
            activity=discord.Activity(type=playing_type, name=playing),
            status=status,
        )
            _io.change_value("./config.json", "playing", playing)
            await ctx.send(f"changed playing status to \"{playing}\"")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(default.traceback_maker(e))

    @commands.command(name="eval", hidden="True")
    @commands.check(perms.only_owner)
    async def eval_fn(self, ctx, *, cmd):
        """
        Execute code. Supports codeblocks.
        Environment-specific variables
        bot: ctx.bot
        discord: discord
        commands: commands
        ctx: ctx.
        """
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        default.insert_returns(body)

        env = {
            "bot": ctx.bot,
            "discord": discord,
            "commands": commands,
            "ctx": ctx,
            "__import__": __import__,
        }

        try:
            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = await eval(f"{fn_name}()", env)
            await ctx.send(result)
        except Exception as e:
            await ctx.send(e)

def setup(bot):
    bot.add_cog(Admin(bot))
