from __future__ import annotations


def safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return "quit"


def print_block(text: str) -> None:
    print(text)
