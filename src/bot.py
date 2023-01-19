#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import discord
from discord.ext import commands
import dotenv
import os
import colorama
import time

dotenv.load_dotenv()
colorama.init(autoreset=True)
TOKEN = os.getenv('TOKEN')
bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())


# Constants
BANNED_COLOR = discord.Color.red()
PROMOTED_COLOR = discord.Color.green()
DEMOTED_COLOR = discord.Color.red()
TEAMKICK_COLOR = discord.Color.red()
TEAMACCEPT_COLOR = discord.Color.green()
TEAMDECLINE_COLOR = discord.Color.red()
BLURPLE_COLOR = discord.Color.blurple()
SUPPORTER_ROLE_ID = 1053808168397983804
BAN_LOG_TEAM_CHANNEL = 1057682406158651522
TEAM_ROLE_ID = 1053808168381190173
TEAM_UPDATES_CHANNEL = 1058088833687769149
SUGGESTIONS_CHANNEL = 1053808170423832595
HIGHTEAM_ROLE_ID = 1064567829837398036
WELCOME_CHANNEL = 1053808170423832586
TEAMLIST_CHANNEL_ID = 1053808170868412469
ROLE_EXCEPTIONS = (HIGHTEAM_ROLE_ID, TEAM_ROLE_ID, 1053808168397983808, 1053808168397983809, 1054700623301464104)


# Main code


class bannedInput(discord.ui.Modal, title='Trage Hier den gebannten Spieler ein!'):
    def __init__(self):
        super().__init__(timeout=None)

    Nickname = discord.ui.TextInput(
        label="Nickname des gebannten Spielers", placeholder="Ex: ~r~fl0w", max_length=32, style=discord.TextStyle.short, required=True)
    steam = discord.ui.TextInput(label="Steam Link des gebannten Spielers",
                                 placeholder="Ex: https://steamcommunity.com/id/rfl0ww", max_length=64, style=discord.TextStyle.short, required=False)
    maßnahme = discord.ui.TextInput(label="Maßnahme die du getroffen hast",
                                    placeholder="Ex: 3 Tage Bann", max_length=32, style=discord.TextStyle.short, required=True)
    grund = discord.ui.TextInput(
        label="Grund für den Bann", placeholder="Ex: Teamkilling", max_length=64, style=discord.TextStyle.short, required=True)
    notiz = discord.ui.TextInput(
        label="Notiz", placeholder="Ex: Mehrfach schon auffällig", max_length=64, style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        banchannel = bot.get_channel(BAN_LOG_TEAM_CHANNEL)
        embed = discord.Embed(title="Spieler wurde gebannt!",
                              description="Hier die Informationen zum gebannten Spieler!", color=BANNED_COLOR)
        embed.add_field(name="Nickname",
                        value="Nicht angegeben" if self.Nickname.value == "" else self.Nickname.value, inline=False)
        embed.add_field(name="Steam Link",
                        value="Nicht angegeben" if self.steam.value == "" else self.steam.value, inline=False)
        embed.add_field(name="Maßnahme",
                        value="Nicht angegeben" if self.maßnahme.value == "" else self.maßnahme.value, inline=False)
        embed.add_field(
            name="Grund", value="Nicht angegeben" if self.grund.value == "" else self.grund.value, inline=False)
        embed.add_field(
            name="Notiz", value="Nicht angegeben" if self.notiz.value == "" else self.notiz.value, inline=False)
        embed.set_footer(text=f"Eingetragen von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
        await banchannel.send(embed=embed)
        await interaction.response.send_message("Spieler wurde erfolgreich eingetragen!", ephemeral=True)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print('Bot is ready!')
    # print some stats about the bot with nice color formatting using colorama
    print(colorama.Fore.CYAN + f'Logged in as {colorama.Fore.BLUE}{bot.user}{colorama.Fore.CYAN} (ID: {colorama.Fore.BLUE}{bot.user.id}{colorama.Fore.CYAN})')
    print(colorama.Fore.CYAN + f'Connected to {colorama.Fore.BLUE}{len(bot.guilds)}{colorama.Fore.CYAN} guilds:')
    print(colorama.Fore.CYAN + f'Connected to {colorama.Fore.BLUE}{len(set(bot.get_all_members()))}{colorama.Fore.CYAN} users')
    print(colorama.Fore.CYAN + f'Connected to Discord API Version {colorama.Fore.BLUE}{discord.__version__}')
    print(colorama.Fore.CYAN + f'Serving {colorama.Fore.BLUE}{len(await bot.tree.fetch_commands())}{colorama.Fore.CYAN} commands')


@bot.tree.command(name='banned', description="Einen gebannten spieler eintragen!")
async def banned(interaction: discord.Interaction):

    if interaction.guild.get_role(TEAM_ROLE_ID) not in interaction.user.roles:
        await interaction.response.send_message("Du hast keine Berechtigung diesen Command auszuführen!", ephemeral=True)
    await interaction.response.send_modal(bannedInput())


@bot.tree.command(name='promote', description="Ein Teammitglied befördern!")
async def promote(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not await bot.is_owner(interaction.user):
        return await interaction.response.send_message("Du hast keine Berechtigung diesen Command auszuführen!", ephemeral=True)

    highest_role = discord.utils.find(lambda role: role in interaction.guild.roles,
                                      reversed(member.roles))
    highteam_role = interaction.guild.get_role(HIGHTEAM_ROLE_ID)

    # check if role is higher than his highest role
    if role.position < highest_role.position:
        embed = discord.Embed(title="Fehler", description="Du kannst keine Rolle befördern die höher ist als die höchste Rolle des Spielers!",
                              color=BANNED_COLOR)
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    self_promote_embed = discord.Embed(title=f"{member.name} wurde befördert!",
                                       description=f"{member.mention} wurde erfolgreich von {highest_role.mention} zu {role.mention} befördert!",
                                       color=PROMOTED_COLOR)
    self_promote_embed.set_thumbnail(url=member.avatar)
    self_promote_embed.set_footer(text=f"Befördert von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    self_promote_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)

    channel_promote_embed = discord.Embed(title=f"{member.name} wurde befördert!",
                                          description=f"{member.mention} wurde von {highest_role.mention} zu {role.mention} befördert!",
                                          color=PROMOTED_COLOR)
    channel_promote_embed.set_thumbnail(url=member.avatar)
    channel_promote_embed.set_footer(text=f"Befördert von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    channel_promote_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)

    await member.remove_roles(highest_role)
    await member.add_roles(role)
    if role.position >= highteam_role.position:
        await member.add_roles(highteam_role)
    await bot.get_channel(TEAM_UPDATES_CHANNEL).send(embed=channel_promote_embed)
    await interaction.response.send_message(embed=self_promote_embed, ephemeral=True)


@bot.tree.command(name='demote', description="Ein Teammitglied degradieren!")
async def demote(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not await bot.is_owner(interaction.user):
        return await interaction.response.send_message("Du hast keine Berechtigung diesen Command auszuführen!", ephemeral=True)

    highest_role = discord.utils.find(lambda role: role in interaction.guild.roles,
                                      reversed(member.roles))
    highteam_role = interaction.guild.get_role(HIGHTEAM_ROLE_ID)

    if role.position > highest_role.position:
        embed = discord.Embed(title="Fehler", description="Du kannst keine Rolle degradieren die niedriger ist als die gewünschte Rolle",
                              color=BANNED_COLOR)
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    self_demote_embed = discord.Embed(title=f"{member.name} wurde degradiert!",
                                      description=f"{member.mention} wurde erfolgreich von {highest_role.mention} zu {role.mention} degradiert!",
                                      color=DEMOTED_COLOR)
    self_demote_embed.set_thumbnail(url=member.avatar)
    self_demote_embed.set_footer(text=f"Degradiert von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    self_demote_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)

    channel_demote_embed = discord.Embed(title=f"{member.name} wurde degradiert!",
                                         description=f"{member.mention} wurde von {highest_role.mention} zu {role.mention} degradiert!",
                                         color=DEMOTED_COLOR)
    channel_demote_embed.set_thumbnail(url=member.avatar)
    channel_demote_embed.set_footer(text=f"Degradiert von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    channel_demote_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)

    await member.remove_roles(highest_role)
    await member.add_roles(role)
    if role.position < highteam_role.position:
        await member.remove_roles(highteam_role)
    await bot.get_channel(TEAM_UPDATES_CHANNEL).send(embed=channel_demote_embed)
    await interaction.response.send_message(embed=self_demote_embed, ephemeral=True)


@bot.tree.command(name='teamkick', description="Ein Teammitglied aus dem Team kicken!")
async def teamkick(interaction: discord.Interaction, member: discord.Member):
    if not await bot.is_owner(interaction.user):
        return await interaction.response.send_message("Du hast keine Berechtigung diesen Command auszuführen!", ephemeral=True)
    # if member == interaction.user:
    #    embed = discord.Embed(title="Fehler", description="Du kannst dich nicht selbst kicken!", color=BANNED_COLOR)
    #    return await interaction.response.send_message(embed=embed, ephemeral=True)
    if interaction.guild.get_role(TEAM_ROLE_ID) not in member.roles:
        return await interaction.response.send_message("Dieser Spieler ist nicht im Team!", ephemeral=True)
    embed = discord.Embed(title=f"{member.name} wurde aus dem Team entlassen!",
                          description=f"Wir danken {member.mention} für seinen / ihren Beitrag und wünschen ihm alles Gute für die Zukunft.",
                          color=TEAMKICK_COLOR)
    embed.set_thumbnail(url=member.avatar)
    embed.set_footer(text=f"Entlassen von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
    self_embed = discord.Embed(title="Erfolgreich entlassen!",
                               description=f"{member.mention} wurde erfolgreich aus dem Team entlassen!",
                               color=TEAMKICK_COLOR)
    self_embed.set_thumbnail(url=member.avatar)
    self_embed.set_footer(text=f"Entlassen von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    self_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
    await bot.get_channel(TEAM_UPDATES_CHANNEL).send(embed=embed)

    await member.remove_roles(interaction.guild.get_role(TEAM_ROLE_ID))
    # remove all roles over team role
    for role in member.roles:
        if role.position > interaction.guild.get_role(TEAM_ROLE_ID).position:
            await member.remove_roles(role)

    await interaction.response.send_message(embed=self_embed, ephemeral=True)


@bot.tree.command(name="annehmen", description="Ein Bewerbung annehmen!")
async def annehmen(interaction: discord.Interaction, member: discord.Member):
    if not await bot.is_owner(interaction.user):
        return await interaction.response.send_message("Du hast keine Berechtigung diesen Command auszuführen!", ephemeral=True)

    if interaction.guild.get_role(TEAM_ROLE_ID) in member.roles:
        return await interaction.response.send_message("Dieser Spieler ist bereits im Team!", ephemeral=True)

    embed = discord.Embed(title=f"{member.name} wurde in das Team aufgenommen!",
                          description=f"Herzlich Willkommen {member.mention} im Team!",
                          color=TEAMACCEPT_COLOR)
    embed.set_thumbnail(url=member.avatar)
    embed.set_footer(text=f"Angenommen von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
    await bot.get_channel(TEAM_UPDATES_CHANNEL).send(embed=embed)

    channel_embed = discord.Embed(title="Angenommen!",
                                  description=f"Vielen Dank für deine Bewerbung {member.mention}!\nDu wurdest in das Team aufgenommen!",
                                  color=TEAMACCEPT_COLOR)
    channel_embed.set_thumbnail(url=member.avatar)
    channel_embed.set_footer(text=f"Angenommen von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    channel_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
    await interaction.channel.send(embed=channel_embed)

    self_embed = discord.Embed(title="Erfolgreich aufgenommen!",
                               description=f"{member.mention} wurde erfolgreich in das Team aufgenommen!",
                               color=TEAMACCEPT_COLOR)
    self_embed.set_thumbnail(url=member.avatar)
    self_embed.set_footer(text=f"Angenommen Entlassen von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    self_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)

    await member.add_roles(interaction.guild.get_role(TEAM_ROLE_ID))
    await member.add_roles(interaction.guild.get_role(SUPPORTER_ROLE_ID))

    await interaction.response.send_message(embed=self_embed, ephemeral=True)


@bot.tree.command(name="ablehnen", description="Ein Bewerbung ablehnen!")
async def ablehnen(interaction: discord.Interaction, member: discord.Member):
    if not await bot.is_owner(interaction.user):
        return await interaction.response.send_message("Du hast keine Berechtigung diesen Command auszuführen!", ephemeral=True)

    if interaction.guild.get_role(TEAM_ROLE_ID) in member.roles:
        return await interaction.response.send_message("Dieser Spieler ist bereits im Team!", ephemeral=True)

    embed = discord.Embed(title=f"{member.name} wurde leider nicht in das Team aufgenommen!",
                          description=f"{member.mention} konnte leider nicht in das Team aufgenommen werden, wir wünschen trotzdem viel Spaß auf dem Server!",
                          color=TEAMDECLINE_COLOR)
    embed.set_thumbnail(url=member.avatar)
    embed.set_footer(text=f"Abgelehnt von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
    await bot.get_channel(TEAM_UPDATES_CHANNEL).send(embed=embed)

    channel_embed = discord.Embed(title="Abgelehnt!",
                                  description=f"Vielen Dank für die Interesse an einem Platz im Team {member.mention}!\nLeider wurde deine Bewerbung abgelehnt!",
                                  color=TEAMDECLINE_COLOR)
    channel_embed.set_thumbnail(url=member.avatar)
    channel_embed.set_footer(text=f"Abgelehnt von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    channel_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
    await interaction.channel.send(embed=channel_embed)

    self_embed = discord.Embed(title="Erfolgreich abgelehnt!",
                               description=f"{member.mention} wurde erfolgreich abgelehnt!",
                               color=TEAMDECLINE_COLOR)
    self_embed.set_thumbnail(url=member.avatar)
    self_embed.set_footer(text=f"Abgelehnt von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    self_embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)

    await interaction.response.send_message(embed=self_embed, ephemeral=True)


@bot.tree.command(name="commandinfo", description="Informationen über einen command!")
async def commandinfo(interaction: discord.Interaction, command: str, description: str):
    if not await bot.is_owner(interaction.user):
        return await interaction.response.send_message("Du hast keine Berechtigung diesen Command auszuführen!", ephemeral=True)
    embed = discord.Embed(title=f"Command: {command}",
                          description=f"Beschreibung: {description}",
                          color=BLURPLE_COLOR)
    embed.set_footer(text=f"Gesendet von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)
    await interaction.response.send_message("Sent!", ephemeral=True)
    await interaction.channel.send(embed=embed)


@bot.tree.command(name="announce", description="Eine Ankündigung machen!")
async def announce(interaction: discord.Interaction, message: str):
    if not await bot.is_owner(interaction.user):
        return await interaction.response.send_message("Du hast keine Berechtigung diesen Command auszuführen!", ephemeral=True)
    embed = discord.Embed(title=f"Ankündigung:\n\n{message}\n_ _",
                          description="_ _",
                          color=BLURPLE_COLOR)
    embed.set_footer(text=f"Angekündigt von {interaction.user.name}#{interaction.user.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}", icon_url=interaction.user.avatar)
    embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon)

    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Sent!", ephemeral=True)


@bot.tree.command(name="update", description="Bot updaten!")
async def git_pull(interaction: discord.Interaction):
    if not await bot.is_owner(interaction.user):
        return await interaction.response.send_message("Du hast keine Berechtigung diesen Command auszuführen!", ephemeral=True)
    os.system("git stash")
    os.system("git pull")
    gitpulldone = discord.Embed(
        title="Bot is restarting!")
    os.system("pm2 restart 10")
    return await interaction.response.send_message(embed=gitpulldone, ephemeral=True)


@bot.event
async def on_message(message: discord.Message):
    if message.channel != bot.get_channel(SUGGESTIONS_CHANNEL) or message.author.bot:
        return
    embed = discord.Embed(title=f"Neuer Vorschlag von {message.author.name}#{message.author.discriminator}",
                          description=f"**{message.content}**", color=BLURPLE_COLOR)
    embed.set_author(name=message.guild.name, icon_url=message.guild.icon)
    embed.set_footer(text=f"Vorschlag von {message.author.name}#{message.author.discriminator} • {time.strftime('%d/%m/%Y %H:%M')}",
                     icon_url=message.author.avatar)
    await message.delete()
    msg = await message.channel.send(embed=embed)
    await msg.add_reaction("⬆️")
    await msg.add_reaction("⬇️")


# Welcomer
@bot.event
async def on_member_join(member: discord.Member):
    welcome_embed = discord.Embed(title=f"Willkommen auf dem MysteryNetwork {member.name}!", description=f"Das Serverteam wünscht einen guten Aufenthalt!", color=BLURPLE_COLOR)

    view = discord.ui.View()
    regelchannel_button = discord.ui.Button("[📜] | Regeln", style=discord.ButtonStyle.link, url="https://discord.com/channels/1053808168381190164/1053808170423832588")
    infochannel_button = discord.ui.Button("[🚀] | Infos", style=discord.ButtonStyle.link, url="https://discord.com/channels/1053808168381190164/1053808170423832590")
    ankündigungenchannel_button = discord.ui.Button("[📢] | Ankündigungen", style=discord.ButtonStyle.link, url="https://discord.com/channels/1053808168381190164/1055149846803251290")
    leakschannel_button = discord.ui.Button("[🔥] | Leaks", style=discord.ButtonStyle.link, url="https://discord.com/channels/1053808168381190164/1061375465446707200")
    view.add_item(regelchannel_button)
    view.add_item(infochannel_button)
    view.add_item(ankündigungenchannel_button)
    view.add_item(leakschannel_button)

    await member.guild.get_channel(WELCOME_CHANNEL).send(embed=welcome_embed, view=view)


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    ishighteam = False

    team_role = after.guild.get_role(TEAM_ROLE_ID)
    highteam_role = after.guild.get_role(HIGHTEAM_ROLE_ID)

    # get all roles over the team role and exclude the highteam role

    roles = [role for role in after.guild.roles if role.position > team_role.position and role.id not in ROLE_EXCEPTIONS]
    roles = roles.reverse()
    print(roles)
    if not roles:
        return
    if not any(role in after.roles for role in roles):
        return

    # get teamlist channel
    teamlist_channel = after.guild.get_channel(TEAMLIST_CHANNEL_ID)
    # delete all messages in the channel
    await teamlist_channel.purge()

    firstembed = discord.Embed(title=f"Teammitglieder:", description=f"_ _", color=BLURPLE_COLOR)
    await teamlist_channel.send(embed=firstembed)

    # list all staff members using embeds
    for role in roles:
        ishighteam = True if role.position > highteam_role.position else False
        roleembed = discord.Embed(title=re.sub(r".*\| ", "", role.name) + ':', description=f"**Highteam: {'Ja' if ishighteam else 'Nein'}**", color=BLURPLE_COLOR)
        roleembed.set_footer(text=time.strftime('%d/%m/%Y %H:%M'))
        roleembed.set_author(name=after.guild.name, icon_url=after.guild.icon)
        for member in role.members:
            highest_role = discord.utils.find(lambda role: role in roles,
                                              reversed(member.roles))
            roleembed.add_field(name=f"{member.name}#{member.discriminator}", value=member.mention, inline=False) if highest_role == role else None
            await teamlist_channel.send(embed=roleembed)


if __name__ == '__main__':
    bot.run(TOKEN)
