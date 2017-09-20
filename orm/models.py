import datetime
from sqlalchemy import or_, Column, Integer, String, Float, Boolean, DateTime, Table, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base

# initialize DeclarativeBase for the models
Base = declarative_base()

#id -> integer
#title -> string
#type -> string
#reference -> string
#fc_affiliate_key -> string
#created_at -> datetime
#updated_at -> datetime

class ComplaintCase(Base):

    __tablename__ = 'complaint_cases'
    id=Column(Integer, primary_key=True)
    assigned_to = Column(String)
    call_closed_date_time_bst = Column(DateTime)
    call_id = Column(String)
    call_opened_date_time = Column(DateTime)
    call_opened_date_time_bst = Column(DateTime)
    call_topic_category_1 = Column(String)
    call_topic_category_2 = Column(String)
    call_topic_category_3 = Column(String)
    date_time_manual_closed_bst = Column(DateTime)
    host_department = Column(String)
    neighbourhood = Column(String)
    neighbourhood_code = Column(String)
    product_type = Column(String)
    request_status = Column(String)
    service_add1 = Column(String)
    service_add2 = Column(String)
    service_add_post_code = Column(String)
    service_add_premise_name = Column(String)
    service_add_premise_no = Column(String)
    service_address = Column(String)
    source_information = Column(String)
    summary = Column(String)
    uprn = Column(String)
    ward = Column(String)
    def __repr__(self):
        return "<ComplaintCase(id = '%s', assigned='%s', topic='%s'>" % \
               (self.id, self.assigned_to, self.call_topic_category_1)

### Get or create object
def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
