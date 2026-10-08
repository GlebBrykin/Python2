import prompt

from .core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .parser import parse_column_def, parse_command, parse_set, parse_where


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, ...) - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи" #noqa 501
    )
    print(
        "<command> update <имя_таблицы> set <столбец> = <значение> where ... - обновить"
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись" #noqa 501
    )
    print("<command> info <имя_таблицы> - информация о таблице")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def welcome():
    print("Первая попытка запустить проект!\n")
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def run():
    welcome()
    while True:
        try:
            user_input = prompt.string("Введите команду: ")
            if not user_input:
                continue

            args = parse_command(user_input)
            if not args:
                continue

            cmd = args[0].lower()

            if cmd == "exit":
                break
            elif cmd == "help":
                print_help()
            elif cmd == "create_table":
                if len(args) < 3:
                    print(
                        "Некорректное значение: недостаточно аргументов. Попробуйте снова." #noqa 501
                    )
                    continue
                try:
                    for col_def in args[2:]:
                        parse_column_def(col_def)
                except ValueError as e:
                    print(f"{e}. Попробуйте снова.")
                    continue
                create_table(args[1], args[2:])
            elif cmd == "drop_table":
                if len(args) != 2:
                    print(
                        "Некорректное значение: неверное количество аргументов. Попробуйте снова." #noqa 501
                    )
                    continue
                drop_table(args[1])
            elif cmd == "list_tables":
                list_tables()
            elif cmd == "insert":
                if len(args) < 5 or args[1] != "into" or args[3] != "values":
                    print(
                        "Некорректное значение: неверный синтаксис insert. Попробуйте снова." #noqa 501
                    )
                    continue
                insert(args[2], args[4:])
            elif cmd == "select":
                if len(args) < 3 or args[1] != "from":
                    print(
                        "Некорректное значение: неверный синтаксис select. Попробуйте снова." #noqa 501
                    )
                    continue
                table_name = args[2]
                if len(args) == 3:
                    select(table_name)
                elif len(args) >= 7:
                    try:
                        where_clause = parse_where(args[3:])
                        select(table_name, where_clause)
                    except ValueError as e:
                        print(f"{e}. Попробуйте снова.")
                        continue
                else:
                    print(
                        "Некорректное значение: неверный синтаксис where. Попробуйте снова." #noqa 501
                    )
            elif cmd == "update":
                if len(args) < 10:
                    print(
                        "Некорректное значение: неверный синтаксис update. Попробуйте снова." #noqa 501
                    )
                    continue
                table_name = args[1]
                try:
                    set_clause = parse_set(args[2:6])
                    where_clause = parse_where(args[6:10])
                    update(table_name, set_clause, where_clause)
                except ValueError as e:
                    print(f"{e}. Попробуйте снова.")
                    continue
            elif cmd == "delete":
                if len(args) < 7 or args[1] != "from":
                    print(
                        "Некорректное значение: неверный синтаксис delete. Попробуйте снова." #noqa 501
                    )
                    continue
                table_name = args[2]
                try:
                    where_clause = parse_where(args[3:])
                    delete(table_name, where_clause)
                except ValueError as e:
                    print(f"{e}. Попробуйте снова.")
                    continue
            elif cmd == "info":
                if len(args) != 2:
                    print(
                        "Некорректное значение: неверное количество аргументов. Попробуйте снова." #noqa 501
                    )
                    continue
                info(args[1])
            else:
                print(f"Функции {cmd} нет. Попробуйте снова.")

        except ValueError as e:
            print(f"{e}")
        except EOFError:
            break
        except KeyboardInterrupt:
            break
