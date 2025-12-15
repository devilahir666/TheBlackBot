import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path
import os, math
from pyrogram.raw.all import layer
from pyrogram.errors import BadRequest, Unauthorized

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from pyrogram import Client, idle 
from pyromod import listen
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from Script import script 
from datetime import date, datetime 
from aiohttp import web # aiohttp import karna zaroori hai
# from plugins import web_server  # <--- यह लाइन हटा दी गई है
# bot login info
from bot import TheBlackBot
from util.keepalive import ping_server
from bot.clients import initialize_clients
from datetime import datetime
from pytz import timezone

# Web Server Function jo Render ko 'alive' rakhega
async def web_server():
    # Render ke Health Check request ko handle karne ke liye simple response
    async def handle(request):
        return web.Response(text="TheBlackBot Service is Alive!")

    app = web.Application()
    app.router.add_get('/', handle)
    # App ko return karen taaki TCPSite ise chala sake
    return app


ppath = "plugins/*.py"
files = glob.glob(ppath)
# TheBlackBot.start() # <-- यह लाइन यहाँ से हटा दी गई है
loop = asyncio.get_event_loop()
PORT = os.environ.get("PORT", "8080")

async def start():
    print('\n')
    print('Initalizing Your Bot')
    
    # **फिक्स 1: TheBlackBot को अब async context के अंदर शुरू करें**
    try:
        await TheBlackBot.start() 
    except Exception as e:
        logging.error(f"Failed to start Pyrogram client: {e}")
        return # अगर क्लाइंट शुरू नहीं होता, तो यहीं रुक जाएं
        
    bot_info = await TheBlackBot.get_me()
    TheBlackBot.username = bot_info.username
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("The Black Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    await Media.ensure_indexes()
    me = await TheBlackBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    TheBlackBot.username = '@' + me.username
    logging.info(LOG_STR)
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    
    # Log Channel Message
    try:
        await TheBlackBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    except (BadRequest, Unauthorized) as e:
        logging.error(f"Failed to send startup message to LOG_CHANNEL: {e}")

    # **फिक्स 2: Web Server Logic को सीधे यहीं शुरू करें**
    try:
        app = web.AppRunner(await web_server()) # सीधे web_server() फ़ंक्शन को कॉल करें
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, int(PORT)).start() 
        logging.info("Web Server Started on port %s", PORT)
    except Exception as e:
        logging.error(f"Failed to start web server: {e}")
        
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Is Stop Sweety 🚏')
        
# Credit @TheBlackXYZ.
# Please Don't remove credit.
# TheBlackXYZBotz Forever !
# Thanks You For Help Us In This Amazing Creativity 
# Thanks You For Giving Me Credit @TheBlackXYZBotz
# For Any ERROR Please Contact Me -> Telegram ->@TheBlackXYZBotz & Insta @TheBlackXYZ
# Please Love & Support 💗💗🙏
