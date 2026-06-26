import os, time, random, json5
import tkinter as tk
from PIL import Image, ImageTk


base = os.path.dirname(__file__)
sep = "="*10

# =========================================================
# 読み込み系
# =========================================================

def load_json(filename, subdir):
    path = os.path.join(base, "data", subdir, filename)
    with open(path, encoding="utf-8") as f:
        return json5.load(f)

def load_keymap(filename):
    path = os.path.join(base, filename)
    with open(path, encoding="utf-8") as f:
        return json5.load(f)

def load_dictionaries(filename):
    path = os.path.join(base, filename)
    with open(path, encoding="utf-8") as f:
        return json5.load(f)

def load_quizdata(filename):
    path = os.path.join(base, filename)
    with open(path, encoding="utf-8") as f:
        return json5.load(f)


# =========================================================
# 一覧化・選択の共通機構
# =========================================================

def collect_all(file_list, subdir):
    items = []
    for filename in file_list:
        data = load_json(filename, subdir)
        for key, value in data.items():
            if key != "series 000" or key == "line" or key != "":
               items.append({
                    "key": key,
                    "data": value,
                    "file": filename
                })
    return items

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
        name = item["data"]["basic"]["name"]
        print(f"{num}. {name['jp']} - {name['en']}")

    print(f"\n見たい{label}を番号または名前で選んでください。（'exit'で戻る）")
    choice = input(">> ").strip()

    if choice == "exit":
        return exit

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            return items[idx]
        return None

    for item in items:
        name = item["data"]["basic"]["name"]
        if choice in (name["jp"], name["en"]):
            return item
    return None


# =========================================================
# データ表示
# =========================================================

def display_data(data, keymap):
    print("\n" + "=" * 40)

    name = data["basic"]["name"]
    print(f"  {name['jp']}  ({name['en']})")

    train_type = data.get("spec", {}).get("train type")
    if train_type:
        print(f"  - {train_type} -")
    print("=" * 40)

    sections = ["basic", "detail", "spec", "corporate"]
    section_labels = {
        "basic": "基本情報",
        "detail": "運用情報",
        "spec": "性能",
        "corporate": "コーポレート情報"
    }

    for section in sections:
        section_data = data.get(section)
        if not section_data:
            continue

        print(f"\n【{section_labels[section]}】")

        for key, value in section_data.items():
            if key == "name":
                continue
            if key == "train type":
                continue

            label = keymap.get(key, key)

            if isinstance(value, dict):
                print(f"  {label}：")
                for sub_key, sub_value in value.items():
                    sub_label = keymap.get(sub_key, sub_key)
                    print(f"    {sub_label}：{sub_value}")
            elif isinstance(value, list):
                print(f"  {label}：{'、'.join(str(v) for v in value)}")
            else:
                print(f"  {label}：{value}")

    for extra_key in ("rolling stock",):
        if extra_key in data:
            label = keymap.get(extra_key, extra_key)
            value = data[extra_key]
            print(f"\n【{label}】\n  {'、'.join(str(v) for v in value)}")

    if "notes" in data:
        print(f"\n【備考】\n  {data['notes']}")
    if "Last updated" in data:
        print(f"\n(最終更新: {data['Last updated']})\n")


    if "desc" in data:
        desc = data["desc"]
        print(f"【説明】")
        print(desc)
    if "history" in data:
        history = data["history"].split("。")
        print(f"\n【略歴】")
        for h in history:
            print(h)

    if "image" in data:
        image_path = data["image"]["path"]
        image_desc = data["image"]["desc"]
        print(image_desc)
        display_CarImage(image_path, name["jp"])

    input("\nEnterで続行>> ")

def display_CarImage(image_name, car_name):

    print(f"Escで画像を閉じる")

    root = tk.Tk()
    root.title(f"{car_name}")

    img = Image.open(f"{base}/Images/JR_West/{image_name}")

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

    def key_event(e):
        key = e.keysym
        if key == "Escape":
            root.destroy()

    root.bind("<Escape>", key_event)

    root.update()
    root.wm_attributes("-topmost", True)
    root.lift()
    root.focus_force() 

    root.mainloop()

# =========================================================
# クイズ
# =========================================================

def quiz_judgement(input_a, a):
    if isinstance(a, list):
        return input_a in a
    return input_a == a

def quiz(data):
    correct = 0
    incorrect = 0
    random.shuffle(data)

    print(f"\nクイズです。")
    input(f"Enterで続行>> ")

    for d in data:
        q = d["question"]
        a = d["answer"]

        print(f"\n問題：{q}")
        input_a = input(f">> ")

        if quiz_judgement(input_a, a):
            correct += 1
            print("正解!!")
        else:
            incorrect += 1
            print("不正解..")

    print(f"\n終了！！！")
    time.sleep(1)
    print(f"問題数：{correct + incorrect}  正解数：{correct}  不正解：{incorrect}")
    input(f"Enterで続行>> ")


# =========================================================
# その他
# =========================================================

def display_other():

    other_dict = {
        "フィルタ定義": "フィルタの定義などを確認できます",
        # "": ""
    }

    print(f"その他です。いろいろな情報が確認できます。\n")
    time.sleep(1)
    n = 1
    for k, v in other_dict.items():
        print(f"{n}. {k} - {v}")
        n += 1
    userinput = input(f">> ")

    if userinput == "1":
        print(f"フィルタ定義が選択されました。\n")
        time.sleep(1)

        print(sep)
        display_category_define()

def display_category_define():
    cat_define = {
        ## company
        "JR": "国鉄分割民営化によって生まれた鉄道会社",
        "私鉄": "JRと三セク以外の鉄道会社",
        "三セク": "地方自治体が中心となって出資し設立された法人によって運営される鉄道会社",

        ## line
        "在来線": "新幹線路線以外の鉄道路線",
        "新幹線": "日本の幹線鉄道である新幹線路線",

        ## region
        "北海道": "北海道地方",
        "東北": "東北地方",
        "関東": "関東地方",
        "中部": "中部地方",
        "近畿": "近畿地方",
        "中国": "中国地方",
        "四国": "四国地方",
        "九州": "九州地方　沖縄県も含める",
        "東海": "東海地方",
        "北陸": "北陸地方",
        "関西": "関西地方",
    }
    for k, v in cat_define.items():
        print(f"{k} : {v}")
    print(sep)


# =========================================================
# メイン処理
# =========================================================

def main():
    dictionaries = load_dictionaries("dictionaries.json5")
    quiz_data = load_quizdata("quiz_data.json5")
    key_map = load_keymap("keymap.json5")

    print(f"\n===== 鉄道DB ===== \nここでは車輌や路線、会社の情報の閲覧やこれに関するクイズができます。ぜひ見ていって下さい")
    input("Enterで続行>> ")

    while True:

        print(f"\nどちらか選んで下さい。 1.情報閲覧  2.クイズ  3.その他")
        choice_mode = input(f"1 or 2 or 3>> ").strip()

        ##  情報閲覧
        if choice_mode == "1":

            print(f"\n見たい情報は？ 1.車両  2.路線  3.会社")
            choice_info = input(f">> ").strip()

            if choice_info == "1":
                all_items = collect_all(dictionaries["rolling_stock_files"], "cars")    
                label = "車両"

            elif choice_info == "2":
                all_items = collect_all(dictionaries["line_files"], "lines")
                label = "路線"

            elif choice_info == "3":
                all_items = collect_all(dictionaries["company_files"], "companies")
                label = "会社"

            else:
                print(f"1~3で選択して下さい。")
                continue


            print(f"\n絞り込みますか？(y/n)")
            choice_filter = input(">> ").strip()

            if choice_filter == "y":
                print("カテゴリを半角スペース区切りで入力してください（例: JR 西日本）")
                tags = input(">> ").strip().split()
                all_items = filter_by_tags(all_items, tags)

            if not all_items:
                print("該当するデータがありませんでした。")
                continue

            selected = select_from_list(all_items, label=label)

            if selected is None:
                print(f"指定された{label}は存在しないか収録されていません。")
                continue
            elif selected is exit:
                continue

            display_data(selected["data"], key_map)

        ##  クイズ
        elif choice_mode == "2":
            quiz(quiz_data)

        ##  その他
        elif choice_mode == "3":
            display_other()

        ##  その他
        else:
            print(f"存在しないモードです。")
            continue

if __name__ == "__main__":
    main()