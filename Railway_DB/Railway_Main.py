import os
import time
import random
import json5
import tkinter as tk
from PIL import Image, ImageTk


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


def load_quizdata(filename="quiz_data.json5"):
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


def collect_all(subdirs):
    items = []
    file_infos = collect_json5_files(subdirs)

    for file_info in file_infos:
        filename = file_info["file"]
        subdir = file_info["subdir"]

        data = load_json(filename, subdir)

        for key, value in data.items():
            if key == "":
                continue

            items.append({
                "key": key,
                "data": value,
                "file": filename,
                "subdir": subdir
            })

    return items


def get_label(key, keymap):
    return keymap.get(key, key)


def format_empty(value):
    if value is None:
        return "なし"
    if value == "":
        return "未入力"
    return value


def get_item_name(data):
    name = data.get("basic", {}).get("name", {})

    if isinstance(name, dict):
        jp = name.get("jp", "名称不明")
        en = name.get("en", "")
        return jp, en

    return str(name), ""


def filter_by_tags(items, tags):
    if not tags:
        return items

    filtered = []

    for item in items:
        category = item["data"].get("detail", {}).get("category", [])

        if all(tag in category for tag in tags):
            filtered.append(item)

    return filtered


def select_from_list(items, label="名前"):
    print(f"\n----- {label}一覧 -----")

    for num, item in enumerate(items, start=1):
        jp_name, en_name = get_item_name(item["data"])
        print(f"{num}. {jp_name} - {en_name}")

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
        jp_name, en_name = get_item_name(item["data"])

        if choice in (jp_name, en_name):
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


def display_data(data, keymap):
    print("\n" + sep)

    jp_name, en_name = get_item_name(data)
    print(f"  {jp_name} ({en_name})")

    train_type = data.get("spec", {}).get("train type")
    if train_type:
        print(f"  - {train_type} -")

    print(sep)

    section_order = [
        "basic",
        "detail",
        "spec",
        "corporate"
    ]

    for section_key in section_order:
        section_data = data.get(section_key)

        if not section_data:
            continue

        print(f"\n【{get_label(section_key, keymap)}】")

        for key, value in section_data.items():
            if key in ("name", "train type"):
                continue

            display_value(key, value, keymap, indent=1)

    if "rolling stock" in data:
        print(f"\n【{get_label('rolling stock', keymap)}】")
        for item in data["rolling stock"]:
            print(f"  ・{item}")

    if "notes" in data:
        print(f"\n【{get_label('notes', keymap)}】")
        print(f"  {data['notes']}")

    if "desc" in data:
        print(f"\n【{get_label('desc', keymap)}】")
        print(data["desc"])

    if "history" in data:
        print(f"\n【{get_label('history', keymap)}】")
        histories = str(data["history"]).split("。")
        for history in histories:
            if history.strip():
                print(f"  ・{history}。")

    if "Last updated" in data:
        print(f"\n({get_label('Last updated', keymap)}: {data['Last updated']})")

    if "image" in data:
        image_path = data["image"].get("path", "")
        image_desc = data["image"].get("desc", "")

        if image_desc:
            print(f"\n{image_desc}")

        if image_path:
            display_image(image_path, jp_name)

    input("\nEnterで続行 > ")


def display_image(image_name, title):
    image_path = find_image_path(image_name)

    if image_path is None:
        print("画像が見つかりませんでした。")
        return

    print("\nEscで画像を閉じます。")

    root = tk.Tk()
    root.title(title)

    img = Image.open(image_path)

    max_width = 500
    max_height = 400
    scale = min(max_width / img.width, max_height / img.height)

    if scale < 1:
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        img = img.resize((new_width, new_height))

    photo = ImageTk.PhotoImage(img)

    root.geometry(f"{img.width}x{img.height}")
    label = tk.Label(root, image=photo)
    label.pack()

    def key_event(event):
        if event.keysym == "Escape":
            root.destroy()

    root.bind("<Escape>", key_event)

    root.update()
    root.wm_attributes("-topmost", True)
    root.lift()
    root.focus_force()

    root.mainloop()


def find_image_path(image_name):
    images_base = os.path.join(base, "Images")

    if not os.path.exists(images_base):
        return None

    direct_path = os.path.join(images_base, image_name)
    if os.path.exists(direct_path):
        return direct_path

    for root, dirs, files in os.walk(images_base):
        for filename in files:
            if filename == image_name:
                return os.path.join(root, filename)

    return None


def quiz_judgement(input_answer, answer):
    if isinstance(answer, list):
        return input_answer in answer

    return input_answer == answer


def quiz(data):
    correct = 0
    incorrect = 0
    quiz_list = data[:]
    random.shuffle(quiz_list)

    print("\nクイズです。")
    input("Enterで続行 > ")

    for quiz_item in quiz_list:
        question = quiz_item["question"]
        answer = quiz_item["answer"]

        print(f"\n問題: {question}")
        input_answer = input(">> ").strip()

        if quiz_judgement(input_answer, answer):
            correct += 1
            print("正解!!")
        else:
            incorrect += 1
            print("不正解..")
            print(f"答え: {answer}")

    print("\n終了！！")
    time.sleep(1)
    print(f"問題数: {correct + incorrect}  正解数: {correct}  不正解数: {incorrect}")
    input("Enterで続行 > ")


def display_other():
    other_dict = {
        "フィルタ定義": "フィルタに使うカテゴリの意味を確認できます。"
    }

    print("\nその他です。")
    for num, item in enumerate(other_dict.items(), start=1):
        key, value = item
        print(f"{num}. {key} - {value}")

    choice = input(">> ").strip()

    if choice == "1":
        display_category_define()


def display_category_define():
    category_define = {
        "JR": "国鉄の分割民営化によって生まれた鉄道会社",
        "私鉄": "JRと第三セクター以外の鉄道会社",
        "第三セクター": "地方自治体などが出資して設立された法人によって運営される鉄道会社",
        "在来線": "新幹線以外の鉄道路線",
        "新幹線": "日本の高速鉄道路線",
        "北海道": "北海道地方",
        "東北": "東北地方",
        "関東": "関東地方",
        "中部": "中部地方",
        "近畿": "近畿地方",
        "中国": "中国地方",
        "四国": "四国地方",
        "九州": "九州地方",
    }

    print("\n----- フィルタ定義 -----")
    for key, value in category_define.items():
        print(f"{key}: {value}")

    input("\nEnterで続行 > ")


def main():
    dictionaries = load_dictionaries()
    keymap = load_keymap()
    quiz_data = load_quizdata()

    print("\n===== 鉄道DB =====")
    print("ここでは車両・路線・会社の情報閲覧とクイズができます。")
    input("Enterで続行 > ")

    while True:
        print("\nどちらか選んでください")
        print("1. 情報閲覧")
        print("2. クイズ")
        print("3. その他")
        print("4. 終了")

        choice_mode = input("1 or 2 or 3 or 4 >> ").strip()

        if choice_mode == "1":
            print("\n見たい情報は？")
            print("1. 車両")
            print("2. 路線")
            print("3. 会社")

            choice_info = input(">> ").strip()

            if choice_info == "1":
                all_items = collect_all(dictionaries.get("rolling_stock_dirs", []))
                label = "車両"

            elif choice_info == "2":
                all_items = collect_all(dictionaries.get("line_dirs", []))
                label = "路線"

            elif choice_info == "3":
                all_items = collect_all(dictionaries.get("company_dirs", []))
                label = "会社"

            else:
                print("1~3で選択してください。")
                continue

            if not all_items:
                print("データが見つかりませんでした。")
                continue

            print("\n絞り込みますか？ (y/n)")
            choice_filter = input(">> ").strip()

            if choice_filter == "y":
                print("カテゴリを半角スペース区切りで入力してください。例: JR 西日本")
                tags = input(">> ").strip().split()
                all_items = filter_by_tags(all_items, tags)

            if not all_items:
                print("該当するデータがありませんでした。")
                continue

            selected = select_from_list(all_items, label=label)

            if selected == "exit":
                continue

            if selected is None:
                print(f"指定された{label}は存在しないか、入力が正しくありません。")
                continue

            display_data(selected["data"], keymap)

        elif choice_mode == "2":
            quiz(quiz_data)

        elif choice_mode == "3":
            display_other()

        elif choice_mode == "4":
            break

        else:
            print("存在しないモードです。")


if __name__ == "__main__":
    main()