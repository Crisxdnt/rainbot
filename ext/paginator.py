import discord
import asyncio


class Paginator:
    '''
    Class that paginates a list of discord.Embed objects

    Parameters
    ------------
    ctx: Context
        The context of the command.
    *embeds: list[discord.Embed] or dict.values[discord.Embed]
        A list of entries to paginate.
    **timeout: int[Optional]
        How long to wait for before the session closes
        Default: 30
    Methods
    -------
    start:
        Starts the paginator session
    stop:
        Stops the paginator session and deletes the embed.
    '''
    def __init__(self, ctx, *embeds, **kwargs):
        '''Initialises the class'''
        self.embeds = embeds

        if len(self.embeds) == 0:
            raise SyntaxError('There should be at least 1 embed object provided to the paginator')

        for i, em in enumerate(self.embeds):
            footer_text = em.footer.text or ' '
            em.set_footer(text=f'Page {i+1} of {len(self.embeds)}' + footer_text, icon_url=em.footer.icon_url)

        self.page = 0
        self.ctx = ctx
        self.timeout = kwargs.get('timeout', 30)
        self.running = False
        self.emojis = {
            u'\u23EE': 'track_previous',
            u'\u25C0': 'arrow_backward',
            u'\u23F9': 'stop_button',
            u'\u25B6': 'arrow_forward',
            u'\u23ED': 'track_next'
        }

    async def start(self):
        '''Starts the paginator session'''
        self.message = await self.ctx.send(embed=self.embeds[0])

        if len(self.embeds) == 1:
            return

        self.running = True
        for emoji in self.emojis:
            await self.message.add_reaction(emoji)
            await asyncio.sleep(0.05)
        await self._wait_for_reaction()

    async def stop(self):
        self.running = False
        try:
            await self.message.clear_reactions()
        except (discord.NotFound, discord.Forbidden):
            pass

    async def _wait_for_reaction(self):
        '''Waits for a user input reaction'''
        while self.running:
            try:
                reaction, user = await self.ctx.bot.wait_for(
                    'reaction_add',
                    check=self._reaction_check,
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                await self.stop()
            else:
                if self.running:
                    self.ctx.bot.loop.create_task(self._reaction_action(reaction))

    def _reaction_check(self, reaction, user):
        '''Checks if the reaction is from the user message and emoji is correct'''
        if not self.running:
            return True
        if user.id == self.ctx.author.id:
            if reaction.emoji in self.emojis:
                if reaction.message.id == self.message.id:
                    return True
        return False

    async def _reaction_action(self, reaction):
        '''Fires an action based on the reaction'''
        if not self.running:
            return
        to_exec = self.emojis[reaction.emoji]

        if to_exec == 'arrow_backward':
            if self.page != 0:
                self.page -= 1
        elif to_exec == 'arrow_forward':
            if self.page != len(self.embeds) - 1:
                self.page += 1
        elif to_exec == 'stop_button':
            await self.message.delete()
            return
        elif to_exec == 'track_previous':
            self.page = 0
        elif to_exec == 'track_next':
            self.page = len(self.embeds) - 1

        try:
            await self.message.edit(embed=self.embeds[self.page])
        except discord.NotFound:
            await self.stop()
        try:
            await self.message.remove_reaction(reaction.emoji, self.ctx.author)
        except discord.Forbidden:
            pass
