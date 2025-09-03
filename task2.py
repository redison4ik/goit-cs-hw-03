from __future__ import annotations
import os
from typing import List, Optional, Dict, Any

from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from bson import ObjectId


DB_NAME = "cats_db"
COLL_NAME = "cats"


def get_collection():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError(
            "Не знайдено змінної середовища MONGODB_URI з URI MongoDB Atlas.\n"
            "Приклад: setx MONGODB_URI \"mongodb+srv://user:pass@cluster/?retryWrites=true&w=majority\""
        )
    client = MongoClient(uri)
    db = client[DB_NAME]
    coll = db[COLL_NAME]
    # індекс унікальності за ім'ям кота
    coll.create_index([("name", ASCENDING)], unique=True)
    return coll


# ----------- CREATE (необов'язкова допоміжна для початкових даних) -----------
def seed_example(coll):
    """Додає приклад документа, якщо такого імені ще немає."""
    example = {
        "name": "barsik",
        "age": 3,
        "features": ["ходить в капці", "дає себе гладити", "рудий"],
    }
    try:
        coll.insert_one(example)
        print("✅ Додано приклад: barsik")
    except DuplicateKeyError:
        pass  # уже є
    except PyMongoError as e:
        print(f"Помилка при додаванні прикладу: {e}")


# ------------------------------ READ -----------------------------------------
def read_all(coll):
    print("— Усі коти —")
    try:
        for doc in coll.find({}).sort("name", ASCENDING):
            print_doc(doc)
    except PyMongoError as e:
        print(f"Помилка читання: {e}")


def read_by_name(coll, name: str):
    try:
        doc = coll.find_one({"name": name})
        if doc:
            print_doc(doc)
        else:
            print(f"Кота з ім'ям '{name}' не знайдено.")
    except PyMongoError as e:
        print(f"Помилка пошуку: {e}")


# ------------------------------ UPDATE ---------------------------------------
def update_age_by_name(coll, name: str, new_age: int):
    try:
        res = coll.update_one({"name": name}, {"$set": {"age": new_age}})
        if res.matched_count:
            print(f"✅ Оновлено вік '{name}' на {new_age}.")
        else:
            print(f"Кота з ім'ям '{name}' не знайдено.")
    except PyMongoError as e:
        print(f"Помилка оновлення: {e}")


def add_feature_by_name(coll, name: str, feature: str):
    """Додає характеристику, уникаючи дублікатів."""
    try:
        res = coll.update_one({"name": name}, {"$addToSet": {"features": feature}})
        if res.matched_count:
            if res.modified_count:
                print(f"✅ Додано характеристику '{feature}' для '{name}'.")
            else:
                print(f"Характеристика вже існує для '{name}'.")
        else:
            print(f"Кота з ім'ям '{name}' не знайдено.")
    except PyMongoError as e:
        print(f"Помилка оновлення: {e}")


# ------------------------------ DELETE ---------------------------------------
def delete_by_name(coll, name: str):
    try:
        res = coll.delete_one({"name": name})
        if res.deleted_count:
            print(f"🗑️ Видалено запис '{name}'.")
        else:
            print(f"Кота з ім'ям '{name}' не знайдено.")
    except PyMongoError as e:
        print(f"Помилка видалення: {e}")


def delete_all(coll):
    sure = input("Видалити ВСІ записи? Надрукуйте 'YES': ")
    if sure.strip().upper() != "YES":
        print("Скасовано.")
        return
    try:
        res = coll.delete_many({})
        print(f"🗑️ Видалено {res.deleted_count} запис(ів).")
    except PyMongoError as e:
        print(f"Помилка масового видалення: {e}")


# ------------------------------ HELPERS --------------------------------------
def print_doc(doc: Dict[str, Any]):
    _id = doc.get("_id")
    name = doc.get("name")
    age = doc.get("age")
    features = doc.get("features", [])
    print(f"* _id: {str(_id)} | name: {name} | age: {age} | features: {features}")


def create_cat(coll, name: str, age: int, features: List[str]):
    """Опціональна утиліта для створення запису."""
    try:
        coll.insert_one({"name": name, "age": age, "features": features})
        print(f"✅ Додано кота '{name}'.")
    except DuplicateKeyError:
        print(f"Кіт з ім'ям '{name}' вже існує.")
    except PyMongoError as e:
        print(f"Помилка створення: {e}")


# ------------------------------ CLI ------------------------------------------
def menu():
    coll = get_collection()
    # необов'язково — підкинемо приклад
    seed_example(coll)

    actions = {
        "1": lambda: read_all(coll),
        "2": lambda: read_by_name(coll, input("Ім'я кота: ").strip()),
        "3": lambda: update_age_by_name(
            coll,
            input("Ім'я кота: ").strip(),
            int(input("Новий вік (ціле число): ").strip()),
        ),
        "4": lambda: add_feature_by_name(
            coll,
            input("Ім'я кота: ").strip(),
            input("Нова характеристика: ").strip(),
        ),
        "5": lambda: delete_by_name(coll, input("Ім'я кота: ").strip()),
        "6": lambda: delete_all(coll),
        "7": lambda: create_cat(
            coll,
            input("Ім'я нового кота: ").strip(),
            int(input("Вік: ").strip()),
            [s.strip() for s in input("Характеристики через кому: ").split(",") if s.strip()],
        ),
    }

    while True:
        print(
            "\n=== Cats CRUD (MongoDB Atlas) ===\n"
            "1) Показати всі записи\n"
            "2) Знайти кота за ім'ям\n"
            "3) Оновити вік кота за ім'ям\n"
            "4) Додати характеристику коту\n"
            "5) Видалити кота за ім'ям\n"
            "6) Видалити ВСЕ\n"
            "7) Створити нового кота\n"
            "0) Вихід\n"
        )
        choice = input("Ваш вибір: ").strip()
        if choice == "0":
            print("Вихід. Гарного дня!")
            break
        action = actions.get(choice)
        if action:
            try:
                action()
            except ValueError:
                print("Некоректне число. Спробуйте ще раз.")
        else:
            print("Невідома опція. Оберіть зі списку.")


if __name__ == "__main__":
    menu()
