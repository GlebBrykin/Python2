import shlex


def parse_command(user_input):
    clean_input = user_input.replace("(", " ").replace(")", " ").replace(",", " ")
    try:
        return shlex.split(clean_input)
    except ValueError:
        raise ValueError(f"Некорректное значение: {user_input}. Попробуйте снова.")


def parse_column_def(col_def):
    if ":" not in col_def:
        raise ValueError(f"Некорректный формат столбца: {col_def}")
    name, type_str = col_def.split(":", 1)
    return name.strip(), type_str.strip()


def parse_where(args):
    if len(args) < 4 or args[0] != "where" or args[2] != "=":
        raise ValueError("Некорректный синтаксис where")
    return args[1], args[3]


def parse_set(args):
    if len(args) < 4 or args[0] != "set" or args[2] != "=":
        raise ValueError("Некорректный синтаксис set")
    return {args[1]: args[3]}
