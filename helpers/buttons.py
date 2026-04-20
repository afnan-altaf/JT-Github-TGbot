from telethon.tl.types import KeyboardButtonCallback, KeyboardButtonUrl
from telethon.tl.types import ReplyInlineMarkup, KeyboardButtonRow


class SmartButtons:
    def __init__(self):
        self._header: list = []
        self._body: list = []
        self._footer: list = []

    def button(self, text: str, callback_data: str = None, url: str = None, position: str = "body"):
        if url:
            btn = KeyboardButtonUrl(text=text, url=url)
        else:
            btn = KeyboardButtonCallback(text=text, data=callback_data.encode())

        if position == "header":
            self._header.append(btn)
        elif position == "footer":
            self._footer.append(btn)
        else:
            self._body.append(btn)

    def _chunk(self, lst, cols):
        return [lst[i:i + cols] for i in range(0, len(lst), cols)]

    def build_menu(self, b_cols: int = 2, f_cols: int = 2, h_cols: int = 1):
        rows = []
        for chunk in self._chunk(self._header, h_cols):
            rows.append(KeyboardButtonRow(buttons=chunk))
        for chunk in self._chunk(self._body, b_cols):
            rows.append(KeyboardButtonRow(buttons=chunk))
        for chunk in self._chunk(self._footer, f_cols):
            rows.append(KeyboardButtonRow(buttons=chunk))
        return ReplyInlineMarkup(rows=rows) if rows else None
