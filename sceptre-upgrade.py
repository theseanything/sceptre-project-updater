
import re
import os
import argparse

resolver_names = {
    "stack_output": "stack_output",
    "stack_output_external": "stack_output_external",
    "environment_variable": "environment_variable",
    "file_contents": "file_contents",
    "file_path": "file_contents"
}

hook_names = {
    "bash": "bash",
    "asg_scheduled_actions": "asg_scheduled_actions"
}


def generate_resolver_substitutor(old_name, new_name):
    old_syntax_pattern = re.compile(":\s*" + old_name + ":\s*", re.MULTILINE)
    new_syntax_string = ": !" + new_name + " "
    return lambda text: old_syntax_pattern.sub(new_syntax_string, text)


def generate_hook_substitutor(old_name, new_name):
    old_syntax_pattern = re.compile("-\s*" + old_name + ":\s*", re.MULTILINE)
    new_syntax_string = "- !" + new_name + " "
    return lambda text: old_syntax_pattern.sub(new_syntax_string, text)


def replace_in_path(path):
    resolver_subs = [generate_resolver_substitutor(old_name, new_name)
                     for old_name, new_name in resolver_names.items()]
    hook_subs = [generate_hook_substitutor(old_name, new_name)
                 for old_name, new_name in hook_names.items()]
    for root, _, files in os.walk(path):
        for name in files:
            filepath = os.path.join(root, name)
            print "Updating file: " + filepath
            with open(filepath, 'r') as f:
                text = f.read()

            for sub in resolver_subs:
                text = sub(text)
            for sub in hook_subs:
                text = sub(text)

            with open(filepath, 'w') as f:
                f.write(text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='This tool to update Sceptre config to new syntax.')
    parser.add_argument(
        '-d', '--dir', help='Sceptre project filepath', type=str, required=True
    )
    args = parser.parse_args()
    replace_in_path(args.dir)
