from sqlalchemy.orm import sessionmaker, Session
import bcrypt
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from sqlalchemy import create_engine, Column, Integer, String, Text, Table, MetaData
from sqlalchemy.orm import sessionmaker

#uvicorn main:app --reload
#to start the https(api) http://127.0.0.1:8000/

app = FastAPI() #start api

users: Dict[str, str] = {}
log: List[str] = []

class User(BaseModel):
    username: str
    password: str

@app.get("/")
def read_root():
    return {""}

@app.post("/register/")
def register_user(user: User):
    if user.username in users:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    users[user.username] = hashed_password
    log.append(f"Пользователь {user.username} зарегистрирован.")
    return {"message": "Пользователь успешно зарегистрирован"}

@app.post("/login/")
def login(user: User):
    if user.username not in users or not bcrypt.checkpw(user.password.encode('utf-8'), users[user.username]):
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    log.append(f"Пользователь {user.username} вошел в систему.")
    return {"message": "Вход выполнен успешно"}


@app.get("/users/", response_model=List[str])
def get_users():
    return list(users.keys())


@app.get("/user/{username}/")
def get_user_info(username: str):
    if username not in users:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"username": username}


@app.put("/update-username/")
def update_username(old_username: str, new_username: str):
    if old_username not in users:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if new_username in users:
        raise HTTPException(status_code=400, detail="Новое имя пользователя уже существует")

    users[new_username] = users.pop(old_username)
    log.append(f"Пользователь {old_username} изменил имя на {new_username}.")
    return {"message": "Имя пользователя успешно изменено"}


@app.get("/user-log/{username}/")
def get_user_log(username: str):
    if username not in users:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user_log = [entry for entry in log if username in entry]
    return user_log

@app.put("/change-password/")
def change_password(username: str, old_password: str, new_password: str):
    if username not in users or not bcrypt.checkpw(old_password.encode('utf-8'), users[username]):
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    users[username] = hashed_new_password
    log.append(f"Пользователь {username} изменил пароль.")
    return {"message": "Пароль успешно изменен"}


@app.delete("/delete-user/")
def delete_user(username: str, password: str):
    if username not in users or not bcrypt.checkpw(password.encode('utf-8'), users[username]):
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")

    del users[username]
    log.append(f"Пользователь {username} удалил свою учетную запись.")
    return {"message": "Учетная запись пользователя успешно удалена"}

@app.get("/log/")
def get_log():
    return log





# settings
DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# meta
metadata = MetaData()

# detector note
notes_table = Table(
    'notes', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('title', String, index=True),
    Column('content', Text)
)

# table in base info
metadata.create_all(bind=engine)

app = FastAPI()

class Note(BaseModel):
    title: str
    content: str


class NoteResponse(Note):
    id: int


# get current session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# create note
@app.post("/notes/", response_model=NoteResponse)
def create_note(note: Note, db: Session = Depends(get_db)):
    db.execute(notes_table.insert().values(title=note.title, content=note.content))
    db.commit()
    return {**note.dict(),
            "id": db.execute(notes_table.select().where(notes_table.c.title == note.title)).fetchone()[0]}


# get All notes
@app.get("/notes/", response_model=List[NoteResponse])
def read_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    result = db.execute(notes_table.select().offset(skip).limit(limit)).fetchall()
    return [{"id": row[0], "title": row[1], "content": row[2]} for row in result]

# get note on ID
@app.get("/notes/{note_id}", response_model=NoteResponse)
def read_note(note_id: int, db: Session = Depends(get_db)):
    result = db.execute(notes_table.select().where(notes_table.c.id == note_id)).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return {"id": result[0], "title": result[1], "content": result[2]}


# uodate note
@app.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, note: Note, db: Session = Depends(get_db)):
    result = db.execute(notes_table.select().where(notes_table.c.id == note_id)).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    db.execute(notes_table.update().where(notes_table.c.id == note_id).values(title=note.title, content=note.content))
    db.commit()
    return {**note.dict(), "id": note_id}


# del note
@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    result = db.execute(notes_table.select().where(notes_table.c.id == note_id)).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Заметка не найдена")

    db.execute(notes_table.delete().where(notes_table.c.id == note_id))
    db.commit()
    return {"message": "Заметка успешно удалена"}
