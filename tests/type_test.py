# Simple poc for mypy type checking error:

the_type = dict[
    str, dict[str, str]
]  # {"repo": repo, "app": {"name": name, "version": version}}


#                vvvvvvvvvvvvvvvvvv: Mypy error: Dict entry 0 has incompatible type "str": "str"; expected "str": "dict[str, str]")
rap: the_type = {"repo": "the repo", "app": {"name": "the app", "version": "1.1.1"}}

print(rap)

# Output:
# {"repo": "the repo", "app": {"name": "the app", "version": "1.1.1"}}
