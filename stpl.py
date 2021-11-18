#!/usr/bin/env python3

import os
import yaml
import shlex

ACTIONS_FILEPATH = os.path.dirname(os.path.realpath(__file__)) + "/actions.yml"

def load_actions():
    return yaml.safe_load(open(ACTIONS_FILEPATH))

def save_actions(actions):
    yaml.safe_dump(actions, open(ACTIONS_FILEPATH, "w"))

def evaluate(string: str):
    string = string.strip()
    if string[0] == "!":
        os.system(string[1:])
        return

    global actions
    parts = shlex.split(string)

    if len(parts) == 0:
        return

    action = parts[0]

    if action[0] == ":":
        command = action[1:]

        if command == "e":
            os.system(f"{environ.get('EDITOR')} {ACTIONS_FILEPATH}")
            actions = load_actions()
        elif command == "r":
            actions = load_actions()
        elif command == "w":
            save_actions(actions)
        elif command == "cd":
            if len(parts) < 2:
                print("Usage:")
                print("  :cd [DIR]")
            else:
                os.chdir(parts[1])
                print(f"pwd is `{os.getcwd()}'")
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
        os.system(f"{prefix}{action}() {{ {'; '.join(actions[action])}; }}; {prefix}{string}")
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
