from datetime import date
from discord.ext import commands

from functions.todo_list import get_list, add_item, mark_complete

class ToDoList(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self._last_member = None

    @commands.command(name='addtodo',
                      help='- add an item to the list. example: $addtodo buy milk')
    async def add(self, ctx, *, 
                  item: str=commands.parameter(description='- item to be added')):
        add_item(ctx.message.author.name, item)
        await ctx.send('Item added')

    @commands.command(name='todolist',
                      help='- shows a users todo list. example: $todolist billjohn')
    async def list(self, ctx, *,
                   user: str=commands.parameter(description='- discord username')):
        try:
            await ctx.send(get_list(user))

        except Exception as e:
            await ctx.send(e)
        
    @commands.command(name='complete',
                      help='- complete an item on the list. example: $complete')
    async def complete(self, ctx):
        try:
            data = get_list(ctx.message.author.name)
            await ctx.send(data + 'Which item have you completed? (enter index)')

            response = await self.bot.wait_for('message',
                                               check=lambda message:message.author == ctx.author and message.channel.id == ctx.channel.id,
                                               timeout=20.0)
            
            mark_complete(ctx.message.author.name, int(response.content)-1)
            
            await ctx.send('nice')

        except Exception as e:
            await ctx.send(e)
    
    
async def setup(bot):
    await bot.add_cog(ToDoList(bot))
