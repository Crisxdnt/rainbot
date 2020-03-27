import random
from discord.ext.commands import check


def get_perm_level(member, guild_info):
    # User is not in server
    if not getattr(member, 'guild_permissions', None):
        return (0, None)

    if member.guild_permissions.administrator:
        perm_level = 15
        highest_role = 'Administrator'
    else:
        perm_level = 0
        highest_role = None

        for i in reversed(member.roles):
            if str(i.id) in guild_info.get('perm_levels', {}).keys():
                if guild_info['perm_levels'][str(i.id)] > perm_level:
                    perm_level = guild_info['perm_levels'][str(i.id)]
                    highest_role = i

    return (perm_level, highest_role)


def lower(argument):
    return str(argument).lower()


def owner():
    def predicate(ctx):
        return ctx.author.id in [180314310298304512, 281821029490229251, 369848495546433537]
    return check(predicate)


def random_color():
    return random.randint(0, 0xfffff)
