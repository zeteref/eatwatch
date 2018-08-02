import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

meal_ingredients = Table('meal_ingredients', Base.metadata,
        Column('ingredient_id', Integer, ForeignKey('ingredients.id')),
        Column('meal_id', Integer, ForeignKey('meals.id')),
        Column('quantity', Integer))
 
class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    calories = Column(Integer, nullable=False)
    sugar = Column(Integer, nullable=False)
    protein_vege = Column(Integer, nullable=False)
    protein_animal = Column(Integer, nullable=False)
    carbo = Column(Integer, nullable=False)
 

class Meal(Base):
    __tablename__ = 'meals'
    id = Column(Integer, primary_key=True)
    time = Column(Date)

    ingredients = relationship('Ingredient', secondary=meal_ingredients)



 
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///sqlalchemy_example.db')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
