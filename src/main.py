"""Bootstrap only (ENG-10): the entry point that index.html calls once the page has loaded."""

from org.transcrypt.stubs.browser import document

from core.math.rng import create_rng, random_in


def main() -> None:
    rng = create_rng(42)
    document.title = "Stratoblaster " + str(int(random_in(rng, 0, 100)))
