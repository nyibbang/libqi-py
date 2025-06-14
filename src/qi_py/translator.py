__all__ = ["defaultTranslator", "tr"]

from .logging import warning

TRANSLATOR = None


def defaultTranslator(name: str):
    global TRANSLATOR
    if TRANSLATOR:
        return TRANSLATOR
    TRANSLATOR = Translator(name)
    return TRANSLATOR


def tr(msg, domain=None, locale=None):
    global TRANSLATOR
    if not TRANSLATOR:
        warning(
            "translator",
            "The default translator has not been initialized, translation is disabled",
        )
        return msg
    return TRANSLATOR.translate(msg, domain=domain, locale=locale)


class Translator:
    def __init__(self, name):
        if len(name) == 0:
            warning("translator", "Translator has empty name")
        self.name = name

    def translate(self, msg, context=None, domain=None, locale=None):
        """Translate a message from a domain to a locale."""
        # TODO
        return msg

    def setCurrentLocale(self, locale):
        """Set the locale."""
        # TODO
        pass

    def setDefaultDomain(self, domain):
        """Set the domain."""
        # TODO
        pass

    def addDomain(self, domain):
        """Add a new domain."""
        # TODO
        pass
