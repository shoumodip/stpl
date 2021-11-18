#!/usr/bin/env python3

from os import system, environ
from yaml import safe_load, safe_dump
from shlex import split

ACTIONS_FILEPATH = "actions.yml"

def load_actions():
    return safe_load(open(ACTIONS_FILEPATH))

def save_actions(actions):
    safe_dump(actions, open(ACTIONS_FILEPATH, "w"))

def evaluate(string: str):
    string = string.strip()
    if string[0] == "!":
        system(string[1:])
        return

    global actions
    parts = split(string)

    if len(parts) == 0:
        return

    action = parts[0]

    if action[0] == ":":
        command = action[1:]

        if command == "e":
            system(f"{environ.get('EDITOR')} {ACTIONS_FILEPATH}")
            actions = load_actions()
        elif command == "r":
            actions = load_actions()
        elif command == "w":
            save_actions(actions)
        elif command == "dump":
            print(actions)
        elif command == "c":
            if len(parts) < 3:
                print("Usage:")
                print("  :c ACTION [EXEC]")
            elif parts[1][0] == ":":
                print(f"Error: cannot create an action starting with a `:'")
            else:
                if parts[1] in actions:
                    print(f"Warning: overwriting existing action `{parts[1]}'")
                actions[parts[1]] = " ".join(parts[2:]).split(";")
        elif command == "d":
            if len(parts) < 2:
                print("Usage:")
                print("  d CMD")
            else:
                if parts[1][0] == ":":
                    print(f"Error: cannot delete an action starting with `:'")
                elif parts[1] in actions:
                    actions.pop(parts[1], None)
                else:
                    print(f"Error: action `{parts[1]}' does not exist")
        elif command == "h":
            assert False, "Not Implemented"
        else:
            print(f"Error: command `{command}' does not exist")
    elif action in actions:
        prefix = f"codi_action{len(actions)}"
        system(f"{prefix}{action}() {{ {'; '.join(actions[action])}; }}; {prefix}{string}")
    else:
        print(f"Error: action `{action}' does not exist")

if __name__ == "__main__":
    actions = load_actions()
    while True:
        try:
            command = input("> ")
        except KeyboardInterrupt:
            exit(0)
        except EOFError:
            exit(0)

        evaluate(command)
