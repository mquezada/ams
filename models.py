from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Tweet(Base):
    __tablename__ = 'tweet'

    tweet_id = Column(BigInteger, primary_key=True)
    text = Column(String(140))
    in_reply_to_status_id = Column(BigInteger)
    favorite_count = Column(Integer)
    source = Column(String(255))
    coordinates = Column(String(255))
    entities = Column(String(255))
    in_reply_to_screen_name = Column(String(255))
    in_reply_to_user_id = Column(BigInteger)
    retweet_count = Column(Integer)
    is_retweet = Column(Boolean)
    retweet_of_id = Column(BigInteger)
    user_id_id = Column(BigInteger)
    lang = Column(String(255))
    created_at = Column(DateTime)
    event_id_id = Column(Integer)

    document_id = Column(Integer, ForeignKey('document.id'))
    document = relationship('Document', back_populates='tweets')

    def __str__(self):
        return f"<id={self.tweet_id}, text={self.text}>"

    def __repr__(self):
        return self.__str__()


class Event(Base):
    __tablename__ = 'event_id'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    event_id = Column(Integer)


class Document(Base):
    __tablename__ = 'document'

    id = Column(Integer, primary_key=True)
    url = Column(String(512))

    tweets = relationship('Tweet', back_populates='document')


class TweetURL(Base):
    __tablename__ = 'tweet_url'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(BigInteger)
    url_id = Column(Integer)

    def __str__(self):
        return f"<tweet_id={self.tweet_id}, url_id={self.url_id}>"

    def __repr__(self):
        return self.__str__()


class URL(Base):
    __tablename__ = 'url'

    id = Column(Integer, primary_key=True)
    short_url = Column(String(255))
    expanded_url = Column(String(512))
    title = Column(String(512))

    def __str__(self):
        return f"<id={self.id}, short={self.short_url}, exp={self.expanded_url}, title={self.title}>"

    def __repr__(self):
        return self.__str__()

