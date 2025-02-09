##################################################
# This bot lists the people that reacted to a    #
# specific message. It also logs the timestamps  #
# when reactions were added and removed in a     #
# CSV file.                                      #
##################################################

import discord
from datetime import datetime
import sqlite3
from csv import writer

# Import secrets
import secrets_file

# This example requires the 'message_content' intent.
# This example requires the 'server_members' intent.

class discordBot(discord.Client):

    ##################################################
    #           Set some initial variables           #
    ##################################################
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set channel and message ID
        self.channel_id = channel_id
        self.message_id = message_id

        # Set icons
        self.icon_0 = "🎓"
        self.icon_1 = "🐣"

        # Set titles
        self.title_0 = "FTO (available)"
        self.title_1 = "Eggie (waiting)"

        # Set available spaces
        self.available_0 = 8
        self.available_1 = 8

    # On ready
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')


    ##################################################
    #     Set initial message and add reactions      #
    ##################################################
    async def on_message(self, message):
        # Ignore own messages
        if( 
            message.author.id == self.user.id and 
            not message.content.startswith('Initializing')
        ):
            return

        # Create initial message
        if message.content.startswith('!initialize oxymobot'):
            await message.channel.send(f'Initializing!')

        # Update "Initializing!" message with message information
        if(
            message.author.id == self.user.id and 
            message.content.startswith('Initializing')
        ):
            init_update = f"Author: {message.author.name}\nChannel ID: {message.channel.id}\nMessage ID: {message.id}\nUpdate the secrets file with message and channel and message ID, then \"!start oxymobot\""
            await message.edit(content=init_update)

        # Update info message with reactable embed
        if message.content.startswith('!start oxymobot'):

            # Get message to update
            u_channel = client.get_channel(self.channel_id)
            u_message = await u_channel.fetch_message(self.message_id)

            # Add reactions
            await u_message.clear_reactions()
            await u_message.add_reaction(self.icon_0)
            await u_message.add_reaction(self.icon_1)


    ##################################################
    #  Function to format/ update the embed message  #
    ##################################################
    async def format_message(self, payload):
    
        # Get all users that reacted      
        reactions = {}
        u_channel = client.get_channel(self.channel_id)
        u_message = await u_channel.fetch_message(self.message_id)
        for reaction in u_message.reactions:
            async for user in reaction.users():
                # Make sure key exists
                if reaction.emoji not in reactions:
                    reactions[reaction.emoji] = []
                # Add reaction to list
                reactions[reaction.emoji].append(user.id)
                
        # Create embed
        embed = discord.Embed(
            color=discord.Color.orange(),
            title="FTO / Eggie availability"
        )    

        # Set embed footer
        embed.set_footer(text=f"React with {self.icon_0} or {self.icon_1}") 

        # Set log users
        log_users = []

        # Format list 1
        mention_list_0 = ""
        
        # Add reactions that arent the bot
        if self.icon_0 in reactions:
            for user in reactions[self.icon_0]:
                if user != self.user.id:
                    username = client.get_user(user)
                    mention_list_0 += f"{username.mention}\n"
                    log_users.append(username.id)

        # Make sure the list is at least the proper length
        list_length = mention_list_0.count("\n")
        while list_length < self.available_0:
            mention_list_0 += "-\n"
            list_length += 1

        # Format list 2
        mention_list_1 = ""
        
        # Add reactions that arent the bot
        if self.icon_1 in reactions:
            for user in reactions[self.icon_1]:
                if user != self.user.id:
                    username = client.get_user(user)
                    mention_list_1 += f"{username.mention}\n"
                    log_users.append(username.id)

        # Make sure the list is at least the proper length
        list_length = mention_list_1.count("\n")
        while list_length < self.available_1:
            mention_list_1 += "-\n"
            list_length += 1

        # Add field at fixed locations
        embed.insert_field_at(0, name=self.title_0, value=mention_list_0)
        embed.insert_field_at(1, name=self.title_1, value=mention_list_1)           

        # Update message (add embed and remove normal text)
        await u_message.edit(embed=embed, content="")

        # Update logs
        await self.update_logs(payload.guild_id, log_users)

    ##################################################
    #          Function to update database           #
    ##################################################

    # Get server ID
    async def update_logs(self, guild_id, log_users):

        # Remove duplicates from list
        log_users = list(dict.fromkeys(log_users))

        # Get guild (server)
        guild = await client.fetch_guild(guild_id)

        # Get timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Logged in users
        logged_in = []

        # Get users
        for member in log_users:
            # Get member object
            member_object = await guild.fetch_member(member)

            # Add name to list
            logged_in.append(member_object.display_name)

        # Open database connection
        conn = sqlite3.connect('discord_bot.db')

        # Create database cursor
        c = conn.cursor()

        # Get all lines without "end"
        c.execute("SELECT * FROM timetable WHERE end IS NULL")
        db_results = c.fetchall()

        # If any results
        if len(db_results) > 0:

            # For each result, check if in list
            for item in db_results:

                # If in list, remove from list
                if item[0] in logged_in:
                    logged_in.remove(item[0])

                # else if not in list, update database with end timestamp and add line to logfile
                else:
                    # Update database
                    c.execute("UPDATE timetable SET end = ? WHERE name = ? AND start = ?",(timestamp, item[0], item[1]))

                    # Update logfile
                    with open('discord_bot.csv','a', newline='') as csv_file:
                        row_content = [item[0], item[1], timestamp]
                        csv_writer = writer(csv_file)
                        csv_writer.writerow(row_content)
                        # fd.write(f"{item[0]}, {item[1]}, {timestamp}")

        # If any lines left in list (people logged in, but not in database)
        if len(logged_in) > 0:

            # For each line in list create database entry with start timestamp
            for item in logged_in:
                # Query
                c.execute("INSERT INTO timetable (name, start) VALUES (?, ?)",(item, timestamp))

                # Commit
                conn.commit()

        # Close database connection
        conn.close()


    ##################################################
    #          If someone adds a reaction            #
    ##################################################
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.message_id:
            return

        # Call update function
        await self.format_message(payload)

    ##################################################
    #         If someone removes a reaction          #
    ##################################################
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != self.message_id:
            return
        
        # Call update function
        await self.format_message(payload)
        
##################################################
#                 Start the bot                  #
##################################################
intents = discord.Intents.default()
intents.message_content = True    
intents.members = True

# Run 
channel_id = secrets_file.channelID
message_id = secrets_file.messageID
client = discordBot(intents=intents)
client.run(secrets_file.token)
