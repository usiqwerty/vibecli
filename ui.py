from colorama import Fore, Style

__logo = r"""
██    ██ ██ ██████  ███████        ██████  ██████  ██████  ███████ 
██    ██ ██ ██   ██ ██            ██      ██    ██ ██   ██ ██      
██    ██ ██ ██████  █████   █████ ██      ██    ██ ██   ██ █████   
 ██  ██  ██ ██   ██ ██            ██      ██    ██ ██   ██ ██      
  ████   ██ ██████  ███████        ██████  ██████  ██████  ███████ 
"""[1:]

logo = ""

colors = [Fore.RED, Fore.RED, Fore.YELLOW, Fore.YELLOW, Fore.YELLOW]
for line, col in zip(__logo.split('\n'), colors):
    if not line:
        continue
    logo += col + line + '\n'
logo += Style.RESET_ALL