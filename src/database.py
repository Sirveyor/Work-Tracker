from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class PropertyDetails(Base):
    __tablename__ = 'property_details'

    id = Column(Integer, primary_key=True)
    property_address = Column(String, nullable=False)
    tax_id = Column(String, nullable=False)
    county = Column(String, nullable=False)
    subdivision_name = Column(String, nullable=True)
    lot_number = Column(String, nullable=True)
    block_number = Column(String, nullable=True)

    job_details = relationship("JobDetails", back_populates="property_details", uselist=False)

class JobDetails(Base):
    __tablename__ = 'job_details'

    id = Column(Integer, primary_key=True)
    job_number = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    owner_phone = Column(String, nullable=False)
    owner_address = Column(String, nullable=True)
    requester_name = Column(String, nullable=True)
    requester_phone = Column(String, nullable=True)
    access_restrictions = Column(String, nullable=True)
    requested_services = Column(String, nullable=True)
    expected_due_date = Column(String, nullable=True)
    property_id = Column(Integer, ForeignKey('property_details.id'))

    property_details = relationship("PropertyDetails", back_populates="job_details")

# Example engine creation and session setup
engine = create_engine('sqlite:///job_info_database.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()