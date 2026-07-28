from rich.console import Console

console = Console()


def show_banner() -> None:
    console.print(
        r"""

   _____       __        __                              _
  / ___/__  __/ /_  ____/ /___  ____ ___  ____ _____    | |
  \__ \/ / / / __ \/ __  / __ \/ __ `__ \/ __ `/ __ \   | |
 ___/ / /_/ / /_/ / /_/ / /_/ / / / / / / /_/ / / / |  |_|
/____/\__,_/_.___/\__,_/\____/_/ /_/ /_/\__,_/_/ |_|  (_)

            Subdomain-Al-Sinwar v1.0
        Passive Subdomain Enumeration Framework

""",
        style="bold red",
    )