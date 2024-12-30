from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Define SQLite database
DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL, echo=True)

# Define base model
Base = declarative_base()

# Define User model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<User(name={self.name}, age={self.age})>"

# Create tables in the database
Base.metadata.create_all(engine)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# Add a user
new_user = User(name="John Doe", age=30)
session.add(new_user)
session.commit()

# Query all users
users = session.query(User).all()
for user in users:
    print(user)
