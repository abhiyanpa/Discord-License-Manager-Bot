import discord
from discord.ext import commands
import logging
import asyncio
import sys
from config import TOKEN, LICENSE_CHANNEL_ID, check_config

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('bot')

class LicenseBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='/', intents=intents)

    async def setup_hook(self):
        logger.debug("Setting up bot hooks and commands...")
        await self.load_extension('cogs.license_manager')
        logger.debug("Syncing command tree...")
        await self.tree.sync()
        logger.debug("Command tree sync complete")

    async def on_ready(self):
        logging.info(f'Logged in as {self.user.name} ({self.user.id})')
        # Removed channel purge functionality

bot = LicenseBot()

async def startup_checks():
    try:
        logger.debug("Starting configuration check...")
        check_config()
        logger.debug("Configuration validated successfully")
        
        logger.debug("Testing storage connection...")
        from json_storage import JsonStorage
        storage = JsonStorage()
        storage.test_connection()
        logger.debug("Storage connection successful")
        
        return True
    except Exception as e:
        logger.error(f"Startup check failed: {str(e)}", exc_info=True)
        return False

async def main():
    try:
        if not await startup_checks():
            logger.error("Startup checks failed. Exiting...")
            sys.exit(1)

        async with bot:
            await bot.start(TOKEN)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)
