import os

from .constants import DATA_DIR, META_FILE, VALID_TYPES
from .decorators import cacher, confirm_action, handle_db_errors, log_time
from .utils import load_metadata, load_table_data, save_metadata, save_table_data


@handle_db_errors
def create_table(table_name, columns_defs):
    metadata = load_metadata()
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return

    columns = [{"name": "ID", "type": "int"}]
    for col_def in columns_defs:
        name, type_str = col_def.split(":", 1)
        if type_str not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {type_str}")
        columns.append({"name": name, "type": type_str})

    metadata[table_name] = {"columns": columns}
    save_metadata(META_FILE, metadata)

    cols_str = ", ".join([f"{c['name']}:{c['type']}" for c in columns])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(table_name):
    metadata = load_metadata()
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    del metadata[table_name]
    save_metadata(META_FILE, metadata)

    data_file = os.path.join(DATA_DIR, f"{table_name}.json")
    if os.path.exists(data_file):
        os.remove(data_file)

    print(f'Таблица "{table_name}" успешно удалена.')


@handle_db_errors
def list_tables():
    metadata = load_metadata()
    if not metadata:
        print("Нет созданных таблиц.")
        return
    for table in metadata.keys():
        print(f"- {table}")


@handle_db_errors
@log_time
def insert(table_name, values):
    metadata = load_metadata()
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    columns = metadata[table_name]["columns"]
    expected_cols = columns[1:]

    if len(values) != len(expected_cols):
        print(
            f"Ошибка: Ожидается {len(expected_cols)} значений, получено {len(values)}."
        )
        return

    data = load_table_data(table_name)

    max_id = 0
    for row in data:
        if row["ID"] > max_id:
            max_id = row["ID"]
    new_id = max_id + 1

    new_row = {"ID": new_id}
    for i, col in enumerate(expected_cols):
        val_str = values[i]
        if col["type"] == "int":
            new_row[col["name"]] = int(val_str)
        elif col["type"] == "bool":
            if val_str.lower() == "true":
                new_row[col["name"]] = True
            elif val_str.lower() == "false":
                new_row[col["name"]] = False
            else:
                raise ValueError(f"Некорректное булево значение: {val_str}")
        else:
            new_row[col["name"]] = str(val_str)

    data.append(new_row)
    save_table_data(table_name, data)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')


@handle_db_errors
@log_time
def select(table_name, where_clause=None):
    metadata = load_metadata()
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    columns = metadata[table_name]["columns"]

    def get_data():
        return load_table_data(table_name)

    data = cacher(f"select_{table_name}_{where_clause}", get_data)

    if where_clause:
        col, val_str = where_clause
        col_type = next((c["type"] for c in columns if c["name"] == col), None)
        if not col_type:
            raise KeyError(col)

        if col_type == "int":
            val = int(val_str)
        elif col_type == "bool":
            val = val_str.lower() == "true"
        else:
            val = str(val_str)

        data = [row for row in data if row.get(col) == val]

    if not data:
        print("Записи не найдены.")
        return

    from prettytable import PrettyTable

    table = PrettyTable()
    table.field_names = [c["name"] for c in columns]
    for row in data:
        table.add_row([row[c["name"]] for c in columns])
    print(table)


@handle_db_errors
def update(table_name, set_clause, where_clause):
    metadata = load_metadata()
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    columns = metadata[table_name]["columns"]
    data = load_table_data(table_name)

    w_col, w_val_str = where_clause
    w_col_type = next((c["type"] for c in columns if c["name"] == w_col), None)
    if not w_col_type:
        raise KeyError(w_col)

    if w_col_type == "int":
        w_val = int(w_val_str)
    elif w_col_type == "bool":
        w_val = w_val_str.lower() == "true"
    else:
        w_val = str(w_val_str)

    updated_count = 0
    for row in data:
        if row.get(w_col) == w_val:
            for s_col, s_val_str in set_clause.items():
                s_col_type = next(
                    (c["type"] for c in columns if c["name"] == s_col), None
                )
                if not s_col_type:
                    raise KeyError(s_col)
                if s_col_type == "int":
                    s_val = int(s_val_str)
                elif s_col_type == "bool":
                    s_val = s_val_str.lower() == "true"
                else:
                    s_val = str(s_val_str)
                row[s_col] = s_val
            updated_count += 1

    if updated_count > 0:
        save_table_data(table_name, data)
        print(f'Записи в таблице "{table_name}" успешно обновлены.')
    else:
        print("Записи для обновления не найдены.")


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_name, where_clause):
    metadata = load_metadata()
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    columns = metadata[table_name]["columns"]
    data = load_table_data(table_name)

    w_col, w_val_str = where_clause
    w_col_type = next((c["type"] for c in columns if c["name"] == w_col), None)
    if not w_col_type:
        raise KeyError(w_col)

    if w_col_type == "int":
        w_val = int(w_val_str)
    elif w_col_type == "bool":
        w_val = w_val_str.lower() == "true"
    else:
        w_val = str(w_val_str)

    new_data = []
    deleted_ids = []
    for row in data:
        if row.get(w_col) == w_val:
            deleted_ids.append(row["ID"])
        else:
            new_data.append(row)

    if deleted_ids:
        save_table_data(table_name, new_data)
        for did in deleted_ids:
            print(f'Запись с ID={did} успешно удалена из таблицы "{table_name}".')
    else:
        print("Записи для удаления не найдены.")


@handle_db_errors
def info(table_name):
    metadata = load_metadata()
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return

    columns = metadata[table_name]["columns"]
    data = load_table_data(table_name)

    cols_str = ", ".join([f"{c['name']}:{c['type']}" for c in columns])
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols_str}")
    print(f"Количество записей: {len(data)}")
