import os
import json5


base = os.path.dirname(__file__)
sep = "=" * 40


def load_json(filename, subdir):
    path = os.path.join(base, "data", subdir, filename)
    with open(path, encoding="utf-8") as f:
        return json5.load(f)


def load_keymap(filename="keymap.json5"):
    path = os.path.join(base, filename)
    with open(path, encoding="utf-8") as f:
        return json5.load(f)


def load_dictionaries(filename="dictionaries.json5"):
    path = os.path.join(base, filename)
    with open(path, encoding="utf-8") as f:
        return json5.load(f)


def collect_json5_files(subdirs):
    files = []

    for subdir in subdirs:
        folder_path = os.path.join(base, "data", subdir)

        if not os.path.exists(folder_path):
            continue

        for filename in os.listdir(folder_path):
            if filename.endswith(".json5"):
                files.append({
                    "file": filename,
                    "subdir": subdir
                })

    return files


def get_label(key, keymap):
    return keymap.get(key, key)


def format_empty(value):
    if value is None:
        return "なし"
    if value == "":
        return "未入力"
    return value


def get_country_name(data):
    name = data.get("basic", {}).get("country name", {})

    if isinstance(name, dict):
        jp = name.get("jp", "名称不明")
        en = name.get("en", "")
        return jp, en

    return str(name), ""


def collect_countries(dictionaries):
    items = []
    file_infos = collect_json5_files(dictionaries.get("country_dirs", []))

    for file_info in file_infos:
        filename = file_info["file"]
        subdir = file_info["subdir"]

        data = load_json(filename, subdir)
        jp_name, en_name = get_country_name(data)

        items.append({
            "key": filename,
            "file": filename,
            "subdir": subdir,
            "name": {
                "jp": jp_name,
                "en": en_name
            },
            "data": data
        })

    return items


def select_from_list(items, label="国家"):
    print(f"\n----- {label}一覧 -----")

    for num, item in enumerate(items, start=1):
        name = item["name"]
        print(f"{num}. {name['jp']} - {name['en']}")

    print(f"\n見たい{label}を番号か名前で選んでください。'exit'で戻ります。")
    choice = input(">> ").strip()

    if choice == "exit":
        return "exit"

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            return items[idx]
        return None

    for item in items:
        name = item["name"]
        if choice in (name["jp"], name["en"]):
            return item

    return None


def display_value(key, value, keymap, indent=0):
    space = "  " * indent
    label = get_label(key, keymap)

    if isinstance(value, dict):
        print(f"{space}{label}:")
        for sub_key, sub_value in value.items():
            display_value(sub_key, sub_value, keymap, indent + 1)

    elif isinstance(value, list):
        print(f"{space}{label}:")

        if not value:
            print(f"{space}  なし")
            return

        for item in value:
            if isinstance(item, dict):
                for sub_key, sub_value in item.items():
                    display_value(sub_key, sub_value, keymap, indent + 1)
                print()
            else:
                print(f"{space}  ・{format_empty(item)}")

    else:
        print(f"{space}{label}: {format_empty(value)}")


def display_international(data, keymap):
    international = data.get("international", {})

    if not international:
        return

    print(f"\n【{get_label('international', keymap)}】")

    section_order = [
        "organizations",
        "regional organizations",
        "military alliances",
    ]

    for section_key in section_order:
        items = international.get(section_key, [])

        if not items:
            continue

        section_label = get_label(section_key, keymap)
        print(f"  {section_label}")

        for item in items:
            name = item.get("name", {})
            jp_name = name.get("jp", "")
            en_name = name.get("en", "")
            abb = item.get("abb", "")

            text = f"    ・{jp_name}"

            if en_name:
                text += f" - {en_name}"

            if abb:
                text += f" / {abb}"

            print(text)

        print()


def display_data(data, keymap):
    print("\n" + sep)

    jp_name, en_name = get_country_name(data)
    print(f"  {jp_name} ({en_name})")
    print(sep)

    section_order = [
        "basic",
        "detail",
        "government",
        "economy",
        "military",
    ]

    for section_key in section_order:
        section_data = data.get(section_key)

        if not section_data:
            continue

        print(f"\n【{get_label(section_key, keymap)}】")

        for key, value in section_data.items():
            display_value(key, value, keymap, indent=1)

    display_international(data, keymap)

    if "Last updated" in data:
        print(f"\n({get_label('Last updated', keymap)}: {data['Last updated']})")

    input("\nEnterで続行 > ")


def main():
    dictionaries = load_dictionaries()
    keymap = load_keymap()

    print("\n===== 国家DB =====")
    print("ここでは国家情報を閲覧できます。")
    input("Enterで続行 > ")

    while True:
        countries = collect_countries(dictionaries)

        print("\nどちらか選んでください")
        print("1. 国家情報閲覧")
        print("2. 終了")

        choice_mode = input("1 or 2 >> ").strip()

        if choice_mode == "1":
            if not countries:
                print("国家データが見つかりませんでした。")
                continue

            selected = select_from_list(countries, label="国家")

            if selected == "exit":
                continue

            if selected is None:
                print("指定された国家は存在しないか、入力が正しくありません。")
                continue

            display_data(selected["data"], keymap)

        elif choice_mode == "2":
            break

        else:
            print("存在しないモードです。")


if __name__ == "__main__":
    main()