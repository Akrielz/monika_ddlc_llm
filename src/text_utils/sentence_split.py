import re
from typing import List


class SentenceSplitter:
    def __init__(self):
        self.alphabets = "([A-Za-z])"
        self.prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        self.suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        self.starters = ("(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|"
                         "Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)")
        self.acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        self.websites = "[.](com|net|org|io|gov|edu|me)"
        self.digits = "([0-9])"
        self.multiple_dots = r'\.{2,}'

    def __call__(self, text: str) -> List[str]:
        """
        Split the text into sentences.

        If the text contains substrings "<prd>" or "<stop>", they would lead
        to incorrect splitting because they are used as markers for splitting.

        Arguments
        ---------
        text : str
            The text to split into sentences.

        Returns
        -------
        list[str]
            The list of sentences.
        """

        text = " " + text + "  "
        text = text.replace("\n", " ")
        text = re.sub(self.prefixes, "\\1<prd>", text)
        text = re.sub(self.websites, "<prd>\\1", text)
        text = re.sub(self.digits + "[.]" + self.digits, "\\1<prd>\\2", text)
        text = re.sub(self.multiple_dots, lambda match: "<prd>" * len(match.group(0)) + "<stop>", text)
        if "Ph.D" in text:
            text = text.replace("Ph.D.", "Ph<prd>D<prd>")
        text = re.sub("\s" + self.alphabets + "[.] ", " \\1<prd> ", text)
        text = re.sub(self.acronyms + " " + self.starters, "\\1<stop> \\2", text)
        text = re.sub(self.alphabets + "[.]" + self.alphabets + "[.]" + self.alphabets + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
        text = re.sub(self.alphabets + "[.]" + self.alphabets + "[.]", "\\1<prd>\\2<prd>", text)
        text = re.sub(" " + self.suffixes + "[.] " + self.starters, " \\1<stop> \\2", text)
        text = re.sub(" " + self.suffixes + "[.]", " \\1<prd>", text)
        text = re.sub(" " + self.alphabets + "[.]", " \\1<prd>", text)
        if "”" in text:
            text = text.replace(".”", "”.")
        if "\"" in text:
            text = text.replace(".\"", "\".")
        if "!" in text:
            text = text.replace("!\"", "\"!")
        if "?" in text:
            text = text.replace("?\"", "\"?")
        text = text.replace(".", ".<stop>")
        text = text.replace("?", "?<stop>")
        text = text.replace("!", "!<stop>")
        text = text.replace("<prd>", ".")
        sentences = text.split("<stop>")
        sentences = [s.strip() for s in sentences]
        if sentences and not sentences[-1]: sentences = sentences[:-1]
        return sentences
