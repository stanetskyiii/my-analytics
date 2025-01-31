from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, index=True)
    domain_name = Column(String, unique=True, index=True)

    pages = relationship("Page", back_populates="domain")


class PageType(Base):
    __tablename__ = "page_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    pages = relationship("Page", back_populates="page_type")


class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    page_url = Column(String, index=True)
    page_type_id = Column(Integer, ForeignKey("page_types.id"))

    domain = relationship("Domain", back_populates="pages")
    page_type = relationship("PageType", back_populates="pages")
    search_data = relationship("SearchData", back_populates="page")


class Query(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(String, index=True)

    search_data = relationship("SearchData", back_populates="query")


class SearchData(Base):
    __tablename__ = "search_data"
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"))
    query_id = Column(Integer, ForeignKey("queries.id"))
    date = Column(Date, index=True)

    device = Column(String, index=True)
    country = Column(String, index=True)
    clicks = Column(Integer)
    impressions = Column(Integer)
    ctr = Column(Float)
    position = Column(Float)

    page = relationship("Page", back_populates="search_data")
    query = relationship("Query", back_populates="search_data")
