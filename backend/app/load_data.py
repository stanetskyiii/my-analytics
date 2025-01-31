import os
import json
from datetime import datetime
import sys

from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Domain, PageType, Page, Query, SearchData, Base
from .classification import classify_url

# Пример: пусть `assets` лежит рядом
# Путь к папке, где лежат все данные (52 домена /год /месяц /день.json)
DATA_FOLDER = os.path.abspath("C:\Users\Андрей\Desktop\ALVADI\ПРОЕКТ МОНИТОРИНГА ПОЗИЦИЙ ПО ТИПАМ СТРАНИЦ\ПОЛНЫЕ ДАННЫЕ\output")

# Путь к файлу с брендами
BRANDS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "brands.txt"))

def load_brands(brands_file):
    brands = set()
    if os.path.exists(brands_file):
        with open(brands_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    brands.add(line.lower())
    else:
        print(f"WARNING: brands file not found: {brands_file}")
    return brands

def get_or_create_domain(db: Session, domain_name: str):
    dom = db.query(Domain).filter_by(domain_name=domain_name).first()
    if not dom:
        dom = Domain(domain_name=domain_name)
        db.add(dom)
        db.commit()
        db.refresh(dom)
    return dom

def get_or_create_page_type(db: Session, type_name: str):
    pt = db.query(PageType).filter_by(name=type_name).first()
    if not pt:
        pt = PageType(name=type_name)
        db.add(pt)
        db.commit()
        db.refresh(pt)
    return pt

def get_or_create_page(db: Session, domain_id: int, url: str, page_type_id: int):
    pg = db.query(Page).filter_by(domain_id=domain_id, page_url=url).first()
    if not pg:
        pg = Page(domain_id=domain_id, page_url=url, page_type_id=page_type_id)
        db.add(pg)
        db.commit()
        db.refresh(pg)
    else:
        # Обновим тип, если вдруг поменялся
        if pg.page_type_id != page_type_id:
            pg.page_type_id = page_type_id
            db.commit()
    return pg

def get_or_create_query(db: Session, query_text: str):
    qr = db.query(Query).filter_by(query_text=query_text).first()
    if not qr:
        qr = Query(query_text=query_text)
        db.add(qr)
        db.commit()
        db.refresh(qr)
    return qr

def main():
    db = SessionLocal()
    Base.metadata.create_all(bind=db.bind)

    # 1) Загружаем brands
    brands = load_brands(BRANDS_FILE)
    print(f"Loaded {len(brands)} brands from {BRANDS_FILE}")

    # 2) Обходим папки доменов
    if not os.path.isdir(DATA_FOLDER):
        print(f"DATA_FOLDER doesn't exist: {DATA_FOLDER}")
        sys.exit(1)

    for domain_dir in os.listdir(DATA_FOLDER):
        domain_path = os.path.join(DATA_FOLDER, domain_dir)
        if not os.path.isdir(domain_path):
            continue

        # domain_dir = что-то типа "alvadi.al" (без протокола)
        domain_obj = get_or_create_domain(db, domain_dir)

        for year_folder in os.listdir(domain_path):
            year_path = os.path.join(domain_path, year_folder)
            if not os.path.isdir(year_path):
                continue

            for month_folder in os.listdir(year_path):
                month_path = os.path.join(year_path, month_folder)
                if not os.path.isdir(month_path):
                    continue

                for file_name in os.listdir(month_path):
                    if not file_name.endswith(".json"):
                        continue
                    file_path = os.path.join(month_path, file_name)

                    day_str = file_name.replace(".json", "")
                    date_str = f"{year_folder}-{month_folder}-{day_str}"
                    try:
                        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except:
                        print("Ошибка парсинга даты:", date_str)
                        continue

                    with open(file_path, "r", encoding="utf-8") as f:
                        try:
                            data_list = json.load(f)
                        except:
                            print("Ошибка чтения JSON:", file_path)
                            continue

                    for item in data_list:
                        query_text = item.get("query", "").strip()
                        page_url = item.get("page", "").strip()
                        device = item.get("device", "").strip()
                        country = item.get("country", "").strip()
                        clicks = item.get("clicks", 0)
                        impressions = item.get("impressions", 0)
                        ctr = item.get("ctr", 0.0)
                        position = item.get("position", 0.0)

                        # Классифицируем
                        page_type_name = classify_url(page_url, brands)
                        pt = get_or_create_page_type(db, page_type_name)

                        pg = get_or_create_page(db, domain_obj.id, page_url, pt.id)
                        qr = get_or_create_query(db, query_text)

                        sd = SearchData(
                            page_id=pg.id,
                            query_id=qr.id,
                            date=parsed_date,
                            device=device,
                            country=country,
                            clicks=clicks,
                            impressions=impressions,
                            ctr=ctr,
                            position=position
                        )
                        db.add(sd)

                    db.commit()
                    print(f"Импортировано {len(data_list)} записей из {file_path}")

    db.close()
    print("Загрузка данных завершена!")

if __name__ == "__main__":
    main()
