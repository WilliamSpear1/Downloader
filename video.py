import re

class Video:
    def setLink(self, value):
            self._link = value

    def getLink(self):
            return self._link

    def setTitle(self, value):
        self._title = self.getUrl(value)

    def getTitle(self):
        return self._title

    def getUrl(self, value):
        reg_str = re.sub(r"\s", "", value)
        text = reg_str.split('-')
        title = text[1].strip()
        names = ",".join(text[2:]).strip()
        return "[" + names.strip() + "]" + title