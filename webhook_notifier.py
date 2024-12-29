import aiohttp
import discord
import logging
from config import WEBHOOK_URL

logger = logging.getLogger('webhook_notifier')

class WebhookNotifier:
    @staticmethod
    async def send_webhook(content, embed=None):
        try:
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
                
                if embed:
                    await webhook.send(content=content, embed=embed)
                else:
                    await webhook.send(content=content)
        except Exception as e:
            logger.error(f"Webhook send error: {e}")
