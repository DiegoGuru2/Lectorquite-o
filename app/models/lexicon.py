from sqlalchemy import String, Integer, Boolean, Text, ForeignKey, DateTime, Column, Identity
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship to words
    words: Mapped[List["Word"]] = relationship(
        secondary="word_categories", back_populates="categories"
    )

class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    term: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True) 
    meaning: Mapped[str] = mapped_column(Text)
    origin: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    audio_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) 
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) 
    is_active: Mapped[bool] = mapped_column(Boolean, default=False) 
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False) 
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    categories: Mapped[List["Category"]] = relationship(
        secondary="word_categories", back_populates="words"
    )
    examples: Mapped[List["Example"]] = relationship(
        back_populates="word", cascade="all, delete-orphan"
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="word", cascade="all, delete-orphan"
    )
    votes: Mapped[List["Vote"]] = relationship(
        back_populates="word", cascade="all, delete-orphan"
    )

class Example(Base):
    __tablename__ = "examples"

    id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    sentence: Mapped[str] = mapped_column(Text)
    translation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))

    # Relationship to word
    word: Mapped["Word"] = relationship(back_populates="examples")

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Nested comments (Hilos)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    replies: Mapped[List["Comment"]] = relationship("Comment", back_populates="parent")
    parent: Mapped[Optional["Comment"]] = relationship("Comment", back_populates="replies", remote_side="Comment.id")

    # Relationships
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id", ondelete="CASCADE"))
    word: Mapped["Word"] = relationship(back_populates="comments")
    
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE")) # Cambiado a String para Supabase UID
    author: Mapped["User"] = relationship(back_populates="comments")

class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    value: Mapped[int] = mapped_column(Integer) 
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE")) # String para Supabase UID
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id", ondelete="CASCADE"))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="votes")
    word: Mapped["Word"] = relationship(back_populates="votes")

class User(Base):
    __tablename__ = "users"

    # ID como String para sincronizar con Supabase UID
    id: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) # Para dgurumendi local
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    comments: Mapped[List["Comment"]] = relationship(back_populates="author")
    votes: Mapped[List["Vote"]] = relationship(back_populates="user")

class WordCategory(Base):
    __tablename__ = "word_categories"
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationship to answers
    answers: Mapped[List["QuizAnswer"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id: Mapped[int] = mapped_column(Integer, Identity(start=1), primary_key=True)
    answer_text: Mapped[str] = mapped_column(String(255))
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("quiz_questions.id", ondelete="CASCADE"))

    question: Mapped["QuizQuestion"] = relationship(back_populates="answers")
