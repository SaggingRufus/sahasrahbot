import asyncio
from functools import wraps

import click
import ircmessage

from alttprbot.alttprgen.mystery import generate_random_game
# from alttprbot.alttprgen import mystery, preset, spoilers
from alttprbot.alttprgen.preset import get_preset
from alttprbot.alttprgen.spoilers import generate_spoiler_game
from alttprbot.database import (config, spoiler_races, srl_races,
                                tournament_results)
from alttprbot.exceptions import SahasrahBotException
from alttprbot.smz3gen import spoilers as smz3_spoilers
from alttprbot.tournament import league
from alttprbot.util.srl import get_race, srl_race_id

# import nest_asyncio


# patch asyncio to allow nesting so we can get the click asyncio wrapper to work correctly
# nest_asyncio.apply()

ACCESSIBLE_RACE_WARNING = ircmessage.style('WARNING: ', bold=True, fg='red') + ircmessage.style('This race is using an accessible ruleset that prohibits most sequence breaking glitches.  Please visit https://link.alttpr.com/accessible for more details!', fg='red')

def coro(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.create_task(func(*args, **kwargs))
        return

    return wrapper

@click.group()
@coro
async def cli():
    pass

    

@cli.command(name='preset')
@click.argument('preset')
@click.option('--accessible', default=False)
@click.option('--silent', default=False)
@click.option("--hints/--no-hints", default=False)
@click.pass_context
@coro
async def preset_cmd(ctx, preset, accessible, silent, hints):
    if ctx.obj['race'] is None:
        return

    await ctx.obj['client'].message(ctx.obj['target'], "Generating game, please wait.  If nothing happens after a minute, contact Synack.")
    race = await srl_races.get_srl_race_by_id(ctx.obj['race_id'])

    if race:
        raise SahasrahBotException("There is already a game generated for this room.  To cancel it, use the $cancel command.")

    if ctx.obj['race']['game']['abbrev'] == 'alttphacks':
        seed, preset_dict = await get_preset(preset, hints=hints, spoilers="off")
        goal = f"vt8 randomizer - {preset_dict['goal_name']}"
        if accessible and seed.data['spoiler']['meta']['logic'] == 'NoGlitches':
            goal = f"{goal} - accessible ruleset"
            await ctx.obj['client'].message(ctx.obj['target'], ACCESSIBLE_RACE_WARNING)
            post_start_message = ACCESSIBLE_RACE_WARNING
        code = await seed.code()
        if silent:
            await ctx.obj['client'].message(ctx.obj['target'], f"{goal} - {seed.url} - ({'/'.join(code)})")
        else:
            await ctx.obj['client'].message(ctx.obj['target'], f".setgoal {goal} - {seed.url} - ({'/'.join(code)})")
    elif ctx.obj['race']['game']['abbrev'] == 'alttpsm':
        seed, preset_dict = await get_preset(preset, randomizer='smz3')
        goal = preset_dict['goal_name']
        if silent:
            await ctx.obj['client'].message(ctx.obj['target'], f"{goal} - {preset} - {seed.url}")
        else:
            await ctx.obj['client'].message(ctx.obj['target'], f".setgoal {goal} - {preset} - {seed.url}")
    else:
        raise SahasrahBotException("This game is not yet supported.")

    await srl_races.insert_srl_race(ctx.obj['race_id'], goal, post_start_message)

@cli.command(name='mystery')
@click.argument('weightset', default='weighted')
@click.option('--accessible', default=False)
@click.option('--silent', default=False)
@click.option("--festive", default=False)
@click.pass_context
@coro
async def mystery_cmd(ctx, weightset, accessible, silent, festive):
    if ctx.obj['race'] is None:
        return

    await ctx.obj['client'].message(ctx.obj['target'], "Generating game, please wait.  If nothing happens after a minute, contact Synack.")
    race = await srl_races.get_srl_race_by_id(ctx.obj['race_id'])

    if race:
        raise SahasrahBotException("There is already a game generated for this room.  To cancel it, use the $cancel command.")

    if ctx.obj['race']['game']['abbrev'] == 'alttphacks':
        seed = await generate_random_game(
            weightset=weightset,
            tournament=True,
            spoilers="mystery",
            festive=festive
        )

        code = await seed.code()

        if festive:
            goal = f"vt8 randomizer - festive mystery {weightset} - DO NOT RECORD"
        else:
            goal = f"vt8 randomizer - mystery {weightset}"

        if accessible and seed.data['spoiler']['meta']['logic'] == 'NoGlitches':
            goal = f"{goal} - accessible ruleset"
            await ctx.obj['client'].message(ctx.obj['target'], ACCESSIBLE_RACE_WARNING)
            post_start_message = ACCESSIBLE_RACE_WARNING

        if silent:
            await ctx.obj['client'].message(ctx.obj['target'], f"{goal} - {seed.url} - ({'/'.join(code)})")
        else:
            await ctx.obj['client'].message(ctx.obj['target'], f".setgoal {goal} - {seed.url} - ({'/'.join(code)})")
    else:
        raise SahasrahBotException("This game is not yet supported.")

    await srl_races.insert_srl_race(ctx.obj['race_id'], goal, post_start_message)

@cli.command(name='spoiler')
@click.argument('preset')
@click.option('--accessible', default=False)
@click.option('--silent', default=False)
@click.option("--studytime", default=None)
@click.pass_context
@coro
async def spoiler_cmd(ctx, preset, accessible, silent, studytime):
    if ctx.obj['race'] is None:
        return

    await ctx.obj['client'].message(ctx.obj['target'], "Generating game, please wait.  If nothing happens after a minute, contact Synack.")
    race = await srl_races.get_srl_race_by_id(ctx.obj['race_id'])

    if race:
        raise SahasrahBotException("There is already a game generated for this room.  To cancel it, use the $cancel command.")

    if ctx.obj['race']['game']['abbrev'] == 'alttphacks':
        seed, preset_dict, spoiler_log_url = await generate_spoiler_game(preset)

        goal_name = preset_dict['goal_name']

        if not seed:
            return

        goal = f"vt8 randomizer - spoiler {goal_name}"
        studytime = 900 if studytime is None else studytime

        if accessible and seed.data['spoiler']['meta']['logic'] == 'NoGlitches':
            goal = f"{goal} - accessible ruleset"
            await ctx.obj['client'].message(ctx.obj['target'], ACCESSIBLE_RACE_WARNING)
            post_start_message = ACCESSIBLE_RACE_WARNING

        code = await seed.code()
        if silent:
            await ctx.obj['client'].message(ctx.obj['target'], f"{goal} - {seed.url} - ({'/'.join(code)})")
        else:
            await ctx.obj['client'].message(ctx.obj['target'], f".setgoal {goal} - {seed.url} - ({'/'.join(code)})")
        await ctx.obj['client'].message(ctx.obj['target'], f"The spoiler log for this race will be sent after the race begins in SRL.  A {studytime}s countdown timer at that time will begin.")
    elif ctx.obj['race']['game']['abbrev'] == 'alttpsm':
        seed, spoiler_log_url = await smz3_spoilers.generate_spoiler_game(preset)

        if seed is None:
            raise SahasrahBotException("That preset does not exist.  For documentation on using this bot, visit https://sahasrahbot.synack.live")

        goal = f"spoiler beat the games"
        studytime = 1500 if studytime is None else studytime
        if silent:
            await ctx.obj['client'].message(ctx.obj['target'], f"{goal} - {seed.url}")
        else:
            await ctx.obj['client'].message(ctx.obj['target'], f".setgoal {goal} - {seed.url}")
        await ctx.obj['client'].message(ctx.obj['target'], f"The spoiler log for this race will be sent after the race begins in SRL.  A {studytime}s countdown timer at that time will begin.")
    else:
        await ctx.obj['client'].message(ctx.obj['target'], "This game is not yet supported.")
        return

    await srl_races.insert_srl_race(ctx.obj['race_id'], goal, post_start_message)
    await spoiler_races.insert_spoiler_race(ctx.obj['race_id'], spoiler_log_url, studytime)

@cli.command(name='leaguerace')
@click.argument('episode_id')
@click.option('--week', default=None)
@click.pass_context
@coro
async def leaguerace_cmd(ctx, episode_id, week):
    if ctx.obj['race'] is None:
        return

    await league.process_league_race(
        target=ctx.obj['target'],
        episodeid=episode_id,
        week=week,
        client=ctx.obj['client']
    )

@cli.command(name='cancel')
@click.pass_context
@coro
async def cancel_cmd(ctx):
    # ctx.obj['festivemode'] = await config.get(0, 'FestiveMode') == "true"

    ctx.obj['race_id'] = srl_race_id(ctx.obj['target'])
    # ctx.obj['race'] = await get_race(ctx.obj['race_id'])
    
    if ctx.obj['race_id'] is None:
        return

    # srl_race = await get_race(ctx.obj['race_id'])

    await srl_races.delete_srl_race(ctx.obj['race_id'])
    await spoiler_races.delete_spoiler_race(ctx.obj['race_id'])
    await tournament_results.delete_active_touranment_race(ctx.obj['race_id'])
    await ctx.obj['client'].message(ctx.obj['target'], "Current race cancelled.")
    await ctx.obj['client'].message(ctx.obj['target'], f".setgoal new race")

@cli.command(name='rules')
@click.pass_context
@coro
async def rules_cmd(ctx):
    await ctx.obj['client'].message(ctx.obj['target'], "For the ALTTPR rules for this race, visit https://link.alttpr.com/racerules")

@cli.command(name='accessible')
@click.pass_context
@coro
async def accessible_cmd(ctx):
    await ctx.obj['client'].message(ctx.obj['target'], "For the ALTTPR accessible racing rules, visit https://link.alttpr.com/accessible")

@cli.command(name='help')
@click.pass_context
@coro
async def help_cmd(ctx):
    await ctx.obj['client'].message(ctx.obj['target'], "For documentation on using this bot, visit https://sahasrahbot.synack.live")

@cli.command(name='joinroom')
@click.argument('channel')
@click.pass_context
@coro
async def joinroom_cmd(ctx, channel):
    await ctx.obj['client'].join(channel)

@cli.command(name='vt')
@click.pass_context
@coro
async def vt_cmd(ctx):
    await ctx.obj['client'].message(ctx.obj['target'], "You summon VT, he looks around confused and curses your next game with bad RNG.")
