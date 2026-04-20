import asyncio
import html
import subprocess

import psutil
from telethon import events
from telethon.errors import MessageNotModifiedError

import config
from bot import Irene
from core.start import get_start_text
from database.store import DataStore
from datetime import datetime, timedelta
from ghub.genbtn import (
    MENU_RESPONSES,
    build_start_buttons,
    build_main_menu_buttons,
    build_about_buttons,
    build_fstats_buttons,
    build_stats_back_button,
    build_server_back_button,
    build_top_users_buttons,
    build_policy_terms_buttons,
    build_policy_back_button,
)
from helpers.donate import DONATION_TEXT, get_donation_buttons
from helpers.guard import ban_check
from helpers.logger import LOGGER


async def measure_network_speed():
    try:
        def run_speedtest():
            try:
                import speedtest
                st = speedtest.Speedtest()
                st.get_best_server()
                download_mbps = st.download() / 1_000_000
                upload_mbps = st.upload() / 1_000_000
                return f"{download_mbps:.2f} Mbps", f"{upload_mbps:.2f} Mbps"
            except Exception:
                return "Error", "Error"
        dl, ul = await asyncio.to_thread(run_speedtest)
        return ("N/A", "N/A") if dl == "Error" else (dl, ul)
    except Exception:
        return "N/A", "N/A"


async def _safe_edit(event, text, parse_mode="html", buttons=None, link_preview=False):
    try:
        await event.edit(text, parse_mode=parse_mode, buttons=buttons, link_preview=link_preview)
    except MessageNotModifiedError:
        pass
    except Exception as e:
        LOGGER.error(f"_safe_edit error: {e}")
        try:
            await event.answer("Something went wrong.", alert=False)
        except Exception:
            pass


@Irene.on(events.CallbackQuery())
@ban_check
async def handle_all_callbacks(event):
    data = event.data.decode("utf-8") if isinstance(event.data, bytes) else event.data

    try:
        from modules.middleware import track
        await track(event.sender_id, event.chat_id)
    except Exception:
        pass

    try:
        if data == "back_to_start":
            sender = await event.get_sender()
            first_name = getattr(sender, "first_name", "") or ""
            last_name = getattr(sender, "last_name", "") or ""
            name = f"{first_name} {last_name}".strip() or "there"
            await _safe_edit(
                event, get_start_text(name),
                parse_mode="markdown",
                buttons=build_start_buttons(),
                link_preview=False,
            )

        elif data in ("main_menu", "back_to_main_menu"):
            await _safe_edit(
                event,
                "<b>Here are the JT GitHub Notify Bot Options: 👇</b>",
                buttons=build_main_menu_buttons(),
            )

        elif data == "about_me":
            text = (
                "<b>ℹ️ About JT GitHub Notify Bot</b>\n"
                "<b>━━━━━━━━━━━━━━━━━━━━━━</b>\n"
                "<b>Name:</b> JT GitHub Notify Bot ⚙️\n"
                "<b>Version:</b> v1.0\n\n"
                "<b>Technical Stacks:</b>\n"
                "- <b>Language:</b> Python 🐍\n"
                "- <b>Libraries:</b> Telethon, FastAPI, aiohttp 📚\n"
                "- <b>Database:</b> MongoDB 🗄\n"
                "- <b>Hosting:</b> VPS 🌐\n\n"
                "<b>About:</b> The all-in-one GitHub webhook bridge for Telegram — "
                "get instant notifications for every event on your repositories!\n\n"
                "<b>Copyright © 2025 JT. All rights reserved.</b>"
            )
            await _safe_edit(event, text, buttons=build_about_buttons())

        elif data == "donate":
            await _safe_edit(
                event, DONATION_TEXT,
                buttons=get_donation_buttons(5),
                link_preview=False,
            )

        elif data == "gh_fstats":
            text = (
                "<b>🗒 JT GitHub Notify Statistics 🔍</b>\n"
                "<b>━━━━━━━━━━━━━━━━━</b>\n"
                "Stay Updated With Real Time Insights....⚡️\n\n"
                "⊗ <b>Usage Report:</b> Full Usage Stats Of The Bot ⚙️\n"
                "⊗ <b>Top Users:</b> Top User's Leaderboard 🔥\n\n"
                "<b>━━━━━━━━━━━━━━━━━</b>\n"
                "<b>💡 Select an option:</b>\n"
            )
            await _safe_edit(event, text, buttons=build_fstats_buttons())

        elif data == "gh_stats":
            store = DataStore.get()
            now = datetime.utcnow()
            daily = await store.count_users({"is_group": False, "last_activity": {"$gte": now - timedelta(days=1)}})
            weekly = await store.count_users({"is_group": False, "last_activity": {"$gte": now - timedelta(weeks=1)}})
            monthly = await store.count_users({"is_group": False, "last_activity": {"$gte": now - timedelta(days=30)}})
            total_users = await store.count_users({"is_group": False})
            total_groups = await store.count_users({"is_group": True})
            text = (
                "<b>📊 JT GitHub Notify Bot Stats ✅</b>\n"
                "<b>━━━━━━━━━━━━━━━━</b>\n"
                f"<b>1 Day Active:</b> {daily} users\n"
                f"<b>1 Week Active:</b> {weekly} users\n"
                f"<b>1 Month Active:</b> {monthly} users\n"
                f"<b>Total Groups:</b> {total_groups}\n"
                "<b>━━━━━━━━━━━━━━━━</b>\n"
                f"<b>Total Bot Users:</b> {total_users} ✅"
            )
            await _safe_edit(event, text, buttons=build_stats_back_button())

        elif data.startswith("top_users_"):
            page = int(data.split("_")[-1])
            users_per_page = 9
            store = DataStore.get()
            all_users = await store.top_users(limit=1000)
            total_pages = max((len(all_users) + users_per_page - 1) // users_per_page, 1)
            start_idx = (page - 1) * users_per_page
            paginated = all_users[start_idx:start_idx + users_per_page]

            lines = f"<b>🏆 Top Users — Page {page}/{total_pages}:</b>\n<b>━━━━━━━━━━━━━━━</b>\n"
            for i, user in enumerate(paginated, start=start_idx + 1):
                uid = user["user_id"]
                try:
                    tg_user = await Irene.get_entity(uid)
                    first = html.escape(tg_user.first_name or "")
                    last = html.escape(getattr(tg_user, "last_name", "") or "")
                    full = f"{first} {last}".strip() or f"User {uid}"
                except Exception:
                    full = f"User {uid}"
                rank = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔸"
                lines += f"{rank} <b>{i}.</b> <a href=\"tg://user?id={uid}\">{full}</a>\n <b>└ ID:</b> <code>{uid}</code>\n\n"
            if not paginated:
                lines += "<i>No active users found.</i>\n"

            await _safe_edit(
                event, lines,
                parse_mode="html",
                buttons=build_top_users_buttons(page, total_pages),
                link_preview=False,
            )

        elif data == "gh_server":
            await event.answer("Fetching server stats...", alert=False)
            try:
                ping_out = subprocess.getoutput("ping -c 1 google.com")
                ping = ping_out.split("time=")[1].split()[0] + " ms" if "time=" in ping_out else "N/A"
            except Exception:
                ping = "N/A"

            dl, ul = await measure_network_speed()
            disk = psutil.disk_usage("/")
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)

            text = (
                "<b>⚙️ Server Status Report</b>\n"
                "<b>━━━━━━━━━━━━━━━</b>\n"
                f"<b>Ping:</b> {ping}\n"
                f"<b>Download:</b> {dl}\n"
                f"<b>Upload:</b> {ul}\n\n"
                f"<b>Disk Total:</b> {disk.total / (2**30):.2f} GB\n"
                f"<b>Disk Used:</b> {disk.used / (2**30):.2f} GB\n"
                f"<b>Disk Free:</b> {disk.free / (2**30):.2f} GB\n\n"
                f"<b>RAM Total:</b> {mem.total / (2**30):.2f} GB\n"
                f"<b>RAM Used:</b> {mem.used / (2**30):.2f} GB\n\n"
                f"<b>CPU Usage:</b> {cpu}%"
            )
            await _safe_edit(event, text, buttons=build_server_back_button())

        elif data == "policy_terms":
            text = (
                "<b>📜 Policy & Terms Menu</b>\n\n"
                "At <b>JT GitHub Notify Bot ⚙️</b>, we prioritize your privacy and security.\n\n"
                "🔹 <b>Privacy Policy</b>: How we collect, use, and protect your data.\n"
                "🔹 <b>Terms & Conditions</b>: Rules for using our services.\n\n"
                "<b>💡 Choose an option below to proceed:</b>"
            )
            await _safe_edit(event, text, buttons=build_policy_terms_buttons())

        elif data == "privacy_policy":
            text = (
                "<b>📜 Privacy Policy — JT GitHub Notify Bot ⚙️</b>\n\n"
                "<b>1. Information We Collect:</b>\n"
                "   - User ID, username for basic functionality\n"
                "   - Encrypted OAuth token, repo names, webhook IDs\n\n"
                "<b>2. How We Use Data:</b>\n"
                "   - To deliver GitHub notifications and handle commands\n"
                "   - Tokens are encrypted with AES-256-GCM before storage\n\n"
                "<b>3. Data Security:</b>\n"
                "   Webhook payloads processed in real-time, never stored permanently\n\n"
                "<b>4. Your Rights:</b>\n"
                "   Use /logout at any time to revoke your token\n\n"
                "<b>Copyright © 2025 JT. All rights reserved.</b>"
            )
            await _safe_edit(event, text, buttons=build_policy_back_button())

        elif data == "terms_conditions":
            text = (
                "<b>📜 Terms & Conditions — JT GitHub Notify Bot ⚙️</b>\n\n"
                "<b>1. Usage Guidelines:</b>\n"
                "   - Must be 13 years or older\n"
                "   - Complies with Telegram's Terms of Service\n\n"
                "<b>2. Prohibited Actions:</b>\n"
                "   - Illegal and unauthorized use strictly forbidden\n"
                "   - No spamming, abuse, or misuse\n\n"
                "<b>3. Disclaimer:</b>\n"
                "   No guarantee of uptime, accuracy, or data reliability\n\n"
                "<b>Copyright © 2025 JT. All rights reserved.</b>"
            )
            await _safe_edit(event, text, buttons=build_policy_back_button())

        elif data in ("menu_vault", "menu_archives", "menu_console", "menu_linkup", "menu_codex", "menu_insight"):
            key = data.replace("menu_", "")
            resp = MENU_RESPONSES.get(key, "<b>Menu coming soon.</b>")
            from ghub.genbtn import build_back_to_menu_button
            await _safe_edit(event, resp, buttons=build_back_to_menu_button())

        elif data == "close_panel":
            try:
                await event.delete()
            except Exception:
                pass

        elif data.startswith("c:"):
            from modules.callbacks_repo import route_repo_callback
            await route_repo_callback(event, data[2:])

        else:
            await event.answer("Unknown action.", alert=False)

    except Exception as e:
        LOGGER.exception(f"Callback handler error: {e}")
        try:
            await event.answer("An error occurred.", alert=False)
        except Exception:
            pass
