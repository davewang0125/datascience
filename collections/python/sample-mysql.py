
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

# Define the MySQL engine using MySQL Connector/Python
engine = sqlalchemy.create_engine(
    'mysql+mysqlconnector://root:password@localhost:3306/classicmodels',
    echo=True)

 
# Define and create the table
Base = declarative_base()
class User(Base):
    __tablename__ = 'users'
 
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(length=50))
    fullname = sqlalchemy.Column(sqlalchemy.String(length=50))
    nickname = sqlalchemy.Column(sqlalchemy.String(length=50))
 
    def __repr__(self):
        return "<User(name='{0}', fullname='{1}', nickname='{2}')>".format(
                            self.name, self.fullname, self.nickname)
 
Base.metadata.create_all(engine)
 
# Create a session
Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()
 
# Add a user
jwk_user = User(name='jesper', fullname='Jesper Wisborg Krogh', nickname='ggg')
session.add(jwk_user)
# session.commit()
 
# Query the user
our_user = session.query(User).filter_by(name='jesper').first()
print('\nOur User:')
print(our_user)
print('Nick name in hex: {0}'.format(our_user.nickname.encode('utf-8')))
