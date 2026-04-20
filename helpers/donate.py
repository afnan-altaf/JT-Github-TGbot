from helpers.buttons import SmartButtons

DONATION_TEXT = (
    "<b>❤️ Support JT GitHub Notify Bot</b>\n\n"
    "If you enjoy using this bot, consider supporting its development!\n\n"
    "Your contributions help keep the servers running and enable new features.\n\n"
    "Thank you for your support! 🙏"
)


def get_donation_buttons(amount: int = 5):
    sb = SmartButtons()
    sb.button(text="⬅️ Back", callback_data="about_me")
    return sb.build_menu(b_cols=1)
