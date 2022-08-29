from .. import db
from sqlalchemy import asc, desc,  and_


class Comic(db.Model):
    __tablename__ = 'comic'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(2000))
    cover_img = db.Column(db.String(128))

    @staticmethod
    def get_comic_by_name_all(name: str) -> list:
        return Comic.query.filter_by(name=name).all()

    @staticmethod
    def get_comic_by_id(id : int):
        return Comic.query.filter_by(id=id).first()

    @staticmethod
    def get_all_comics() -> list:
        return Comic.query.all()

    def get_latest_chap(self):
        return Chapter.query.filter_by(comic_id = self.id).order_by(Chapter.number.desc()).first()

    def get_first_chap(self):
        return Chapter.query.filter_by(comic_id = self.id).order_by(Chapter.number.asc()).first()

    def count_chaps(self) -> int:
        return len(Chapter.query.filter_by(comic_id = self.id).all())

    def edit_comic_name(self, name: str) -> None:
        self.name = name
        db.session.commit()

    def edit_cover_img(self, path: str) -> None:
        self.cover_img = path
        db.session.commit()

    def get_chaps_all(self) -> list:
        return Chapter.query.filter_by(comic_id = self.id).order_by(Chapter.number.asc()).all()

    def get_genre(self) -> list:
        return Genre.query.filter_by(comic_id = self.id).all()

    def get_alternative_names(self) -> list:
        return AlternativeName.query.filter_by(comic_id = self.id).all()

    def add_alternative_name(self, name: str) -> None:
        alter_name = AlternativeName(name=name, comic_id=self.id)
        db.session.add(alter_name)
        db.session.commit()

    def add_genre(self, name: str) -> None:
        genre = Genre(name=name, comic_id=self.id)
        db.session.add(genre)
        db.session.commit()

    def add_chapter(name: str, number: int, self, path: str) -> None:
        chapter = Chapter(name=name, number=number, path=path, comic_id=self.id)
        db.session.add(chapter)
        db.session.commit()


class AlternativeName(db.Model):
    __tablename__ = 'altername'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), index=True)
    comic_id = db.Column(db.Integer, db.ForeignKey('comic.id'))

    def edit_name(self, name: str):
        self.name = name
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(64), index=True)
    comic_id = db.Column(db.Integer, db.ForeignKey('comic.id'))

    def edit_name(self, name: str):
        self.name = name
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True, index=True)
    number = db.Column(db.Float, index=True)
    name = db.Column(db.String(64), index=True)
    path = db.Column(db.String(128))
    comic_id = db.Column(db.Integer, db.ForeignKey('comic.id'))

    @staticmethod
    def get_chapter(comic_id: int, chap_id: int):
        return Chapter.query.filter(and_(Chapter.comic_id==comic_id, Chapter.id==chap_id)).first()

    def edit_name(self, name: str):
        self.name = name
        db.session.commit()

    def edit_number(self, number: str):
        self.number = number
        db.session.commit()

    def add_page(self, number: int, path: str):
        page = Page(number=number, path=path, chapter_id=self.id, comic_id=self.comic_id)
        db.session.add(page)
        db.session.commit()

    def get_pages(self) -> list:
        return Page.query.filter(and_(Page.chapter_id == self.id,
                                   Page.comic_id == self.comic_id)
                                   ).order_by(Page.number.asc()).all()

    def delete(self):
        pages = self.get_pages()
        for page in pages:
            page.delete()

        db.session.delete(self)
        db.session.commit()



class Page(db.Model):
    __tablename__ = 'page'
    id = db.Column(db.Integer, primary_key=True, index=True)
    number = db.Column(db.Integer)
    path = db.Column(db.String(64))
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    comic_id = db.Column(db.Integer, db.ForeignKey('comic.id'))

    def delete(self):
        db.session.delete(self)
        db.session.commit()


