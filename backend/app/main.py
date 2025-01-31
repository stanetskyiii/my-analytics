from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from .database import SessionLocal, engine
from .models import Base, Domain, PageType, Page, Query, SearchData
from .schemas import DomainOut, PageTypeOut
from .config import settings

# Создаём таблицы при первом запуске (для простоты)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Custom GSC Analytics")

# Зависимость: получение сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/domains", response_model=List[DomainOut])
def list_domains(db: Session = Depends(get_db)):
    domains = db.query(Domain).all()
    return domains


@app.get("/api/page_types", response_model=List[PageTypeOut])
def list_page_types(db: Session = Depends(get_db)):
    pts = db.query(PageType).all()
    return pts


@app.get("/api/report/main_dashboard")
def main_dashboard(
    date_from: date,
    date_to: date,
    group_by: str = "domain",
    db: Session = Depends(get_db)
):
    """
    Пример эндпоинта для главного дашборда.
    date_from, date_to - фильтр по дате
    group_by=domain  -> группируем по доменам
    group_by=page_type -> группируем по типам
    """
    # Простейший пример: считаем AVG(position), MEDIAN(position), SUM(clicks), SUM(impressions), %top10
    # Реальные SQL-запросы могут быть сложнее, здесь лишь показано "как может быть".
    from sqlalchemy import func, case, cast, Float

    # Базовый запрос
    q = (
        db.query(
            Domain.domain_name.label("domain_name"),
            PageType.name.label("page_type_name"),
            func.avg(SearchData.position).label("avg_position"),
            func.sum(SearchData.clicks).label("sum_clicks"),
            func.sum(SearchData.impressions).label("sum_impressions"),
            (func.sum(case([(SearchData.position <= 10, 1)], else_=0)) 
             / cast(func.count(SearchData.id), Float) * 100).label("percent_in_top10")
        )
        .join(Page, Page.id == SearchData.page_id)
        .join(Domain, Domain.id == Page.domain_id)
        .join(PageType, PageType.id == Page.page_type_id)
        .filter(SearchData.date >= date_from, SearchData.date <= date_to)
    )

    if group_by == "domain":
        q = q.group_by(Domain.id, PageType.id)  # можно группировать ещё и по page_type, если хотим
        # Или если нужно только домены — убираем page_type из выборки
    elif group_by == "page_type":
        q = q.group_by(PageType.id, Domain.id)
    else:
        raise HTTPException(status_code=400, detail="Invalid group_by parameter")

    rows = q.all()

    # Возвращаем как есть (список словарей)
    results = []
    for r in rows:
        results.append({
            "domain": r.domain_name,
            "page_type": r.page_type_name,
            "avg_position": float(r.avg_position or 0),
            "sum_clicks": int(r.sum_clicks or 0),
            "sum_impressions": int(r.sum_impressions or 0),
            "percent_in_top10": float(r.percent_in_top10 or 0)
        })

    return results
