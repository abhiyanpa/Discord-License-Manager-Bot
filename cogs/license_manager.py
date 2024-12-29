import discord
from discord import app_commands
from discord.ext import commands
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from config import LICENSE_CHANNEL_ID, GENERATE_ROLE_ID
from json_storage import JsonStorage
from licensegate import LicenseGateAPI, LicenseGateError
from webhook_notifier import WebhookNotifier

class LicenseManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storage = JsonStorage()
        self.license_api = LicenseGateAPI()
        self.logger = logging.getLogger('license_manager')
        self.logger.debug("LicenseManager cog initialized")

    @app_commands.command()
    async def generate(self, interaction: discord.Interaction):
        """Generate a new CS Spawner license"""
        self.logger.debug(f"Generate command used by {interaction.user}")
        
        # Check if user has the required role
        if not any(role.id == GENERATE_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message(
                "You don't have permission to generate licenses.",
                ephemeral=True
            )
            return

        # Channel check
        if interaction.channel_id != LICENSE_CHANNEL_ID:
            await interaction.response.send_message(
                "This command can only be used in the license generation channel.",
                ephemeral=True
            )
            return

        try:
            # Check for existing license but don't fail if delete fails
            existing_license = self.storage.get_user_license(interaction.user.id)
            if existing_license:
                try:
                    await self.license_api.delete_license(existing_license[4])  # Use license_id
                except Exception as e:
                    self.logger.warning(f"Failed to delete old license: {str(e)}")
                self.storage.delete_user_license(interaction.user.id)

            # Create new license
            license_data = await self.license_api.create_license(str(interaction.user))
            self.logger.debug(f"Received license data: {license_data}")
            
            license_key = license_data.get('licenseKey')
            license_id = license_data.get('id')  # Get license ID
            if not license_key or not license_id:
                raise ValueError("Missing licenseKey or id in response")
                
            expires_at = datetime.now() + timedelta(days=90)
            self.storage.add_user_license(interaction.user.id, license_key, license_id, expires_at)

            # Send license details via DM
            try:
                embed = discord.Embed(
                    title="Your CS Spawner License",
                    color=discord.Color.green()
                )
                embed.add_field(name="License Key", value=f"```{license_key}```", inline=False)
                embed.add_field(name="Expires", value=expires_at.strftime("%Y-%m-%d"), inline=True)
                embed.set_footer(text="Keep this information private!")

                await interaction.user.send(embed=embed)
                await interaction.response.send_message(
                    "License generated successfully! Check your DMs for the details.",
                    ephemeral=True
                )

                # Send webhook notification
                webhook_embed = discord.Embed(
                    title="New License Generated",
                    color=discord.Color.blue(),
                    timestamp=datetime.now()
                )
                webhook_embed.add_field(name="User", value=interaction.user.mention, inline=False)
                webhook_embed.add_field(name="License Key", value=f"```{license_key}```", inline=False)
                await WebhookNotifier.send_webhook(
                    content="🔑 A new license has been generated",
                    embed=webhook_embed
                )

            except discord.Forbidden:
                await interaction.response.send_message(
                    "Unable to send you the license details. Please enable DMs from server members.",
                    ephemeral=True
                )
                await self.license_api.delete_license(license_key)
                self.storage.delete_user_license(interaction.user.id)

        except Exception as e:
            self.logger.error(f"Error generating license: {str(e)}")
            await interaction.response.send_message(
                "An error occurred while generating your license. Please try again later.",
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == LICENSE_CHANNEL_ID and not message.author.bot:
            if not message.content.startswith('/generate'):
                await message.delete()

async def setup(bot):
    await bot.add_cog(LicenseManager(bot))
    logging.getLogger('license_manager').debug("LicenseManager cog setup complete")
    # Removed bot.tree.sync() as it's handled in setup_hook
