# DispatchBot
Python Dispatch Bot

## Setup

Install the python discord module and dependencies

```bash
pip install discord.py
pip install audioop-lts
```

Create api token
https://discord.com/developers/applications

Add your API token to the secrets_file.py
```python
# Discord API token
token = "averylongtokenfromthewebsitebetweenquotes"
```

Initialize bot
`!initialize oxymobot`

Add message and channel ID to secrets (no quotes)
```python
# Discord channel ID
channelID = 12345

# Discord message ID
messageID = 12345
```

Start bot
`!start oxymobot`

## Customization

Change title
```python
# Create embed
embed = discord.Embed(
    color=discord.Color.orange(),
    title="FTO / Eggie availability"
)    
```

Change Icon
```python
# Set icons
self.icon_0 = "🎓"
self.icon_1 = "🐣"
```

Change columns
```python
# Set titles
self.title_0 = "FTO (available)"
self.title_1 = "Eggie (waiting)"
```
