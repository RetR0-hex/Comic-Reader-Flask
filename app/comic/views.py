from flask import (
    Blueprint,
    abort,
    flash,
    render_template,
    redirect,
    url_for
)
from flask_login import login_required
import os
from werkzeug.utils import secure_filename

from app import db
from app.comic.forms import NewComicForm, UploadChapter, DeleteComic

from app.decorators import admin_required
from app.models import Comic, Genre, AlternativeName, Chapter
from zipfile import ZipFile
from .. import basedir

from app.utils import random_name

comic = Blueprint('comic', __name__)


data_dir = os.path.join('static', 'data')

temp_dir = os.path.join(basedir, 'temp')


@comic.route("/manage", methods=["GET", "POST"])
@login_required
@admin_required
def manage():
    comics = Comic.get_all_comics()
    return render_template('comic/manage.html', form=None, comics=comics)


@comic.route("/new-comic", methods=["GET", "POST"])
@login_required
@admin_required
def new_comic():
    form = NewComicForm()
    if form.validate_on_submit():
        genres = str.replace(form.genre.data, " ", "").lower().split(',')
        alter_names = str.replace(form.alternative_name.data, " ", "").lower().split(',')
        cover_img = form.cover_image.data
        cover_img_path = os.path.join(data_dir, random_name(), secure_filename(cover_img.filename))
        os.mkdir(os.path.join(basedir, os.path.dirname(cover_img_path)))
        cover_img.save(os.path.join(basedir, cover_img_path))
        comic_db = Comic(
                     name=form.name.data,
                     cover_img='/' + cover_img_path,
                     description=form.desc.data
                     )
        db.session.add(comic_db)
        db.session.commit()
        db.session.flush()

        # add new genres
        if genres:
            for genre in genres:
                comic_db.add_genre(name=genre)

        # add new ALTERNAMES
        if alter_names:
            for alt_name in alter_names:
                comic_db.add_alternative_name(name=alt_name)

        # Flash success msg to user
        flash('Comic {} successfully created'.format(comic_db.name),
        'form-success')
        return redirect(url_for('comic.manage'))

    return render_template('comic/manage.html', form=form)

@comic.route('/delete', methods=['Get', 'POST'])
@login_required
@admin_required
def delete():
    form = DeleteComic()
    if form.validate_on_submit():
        user_comic = form.comic.data

        if user_comic is None:
            flash(f'Comic is required',
            'form-error')

        comic_dir_path = os.path.join(basedir, os.path.dirname(user_comic.cover_img)[1:])

        # deletes files in the folder recursivly
        for root, dirs, files in os.walk(comic_dir_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        # then deletes the empty folder itself
        try:
            os.rmdir(comic_dir_path)
        except:
            pass

        # now to remove everything related to that comic from the db
        comic = Comic.get_comic_by_id(user_comic.id)

        genres = comic.get_genre()

        alt_names = comic.get_alternative_names()

        chapters = comic.get_chaps_all()

        for chapter in chapters:
            chapter.delete()

        for genre in genres:
            genre.delete()

        for alt_name in alt_names:
            alt_name.delete()

        db.session.delete(comic)
        db.session.commit()
        db.session.flush()


        flash(f'Comic was successfully deleted!',
        'form-success')

        return redirect(url_for('comic.manage'))

    return render_template('comic/manage.html', form=form)


@comic.route('/upload-chapter', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_chapter():
    form = UploadChapter()
    if form.validate_on_submit():
        chap_name = form.name.data
        form_comic = form.comic.data

        # Checking if the comic obj is none or not
        if form_comic is None:
            flash(f'Comic name is required',
            'form-error')

        else:
            chap_num = str(form.number.data)
            chap_zip = form.chap_zip.data

            # remove starting / which i added for front end relaive path
            comic_dir = os.path.dirname(form_comic.cover_img)[1:]

            chap_zip.save(os.path.join(temp_dir, "temp.zip"))

            zpfile = ZipFile(os.path.join(temp_dir, "temp.zip"), 'r')
            chap_path = os.path.join(comic_dir, random_name())
            full_chap_path = os.path.join(basedir, chap_path)
            os.mkdir(full_chap_path)
            zpfile.extractall(path=full_chap_path)

            # remove zip file from temp dir
            os.remove(os.path.join(temp_dir, "temp.zip"))

            # ADD chapter to database along with its path
            chapter = Chapter(name=chap_name, number=chap_num, path=chap_path, comic_id=form_comic.id)

            db.session.add(chapter)
            db.session.commit()
            db.session.flush()

            # add pages to that chapter
            page_number = 1

            for file in sorted(os.listdir(full_chap_path)):
                chapter.add_page(page_number, file)
                page_number += 1

            flash(f'Chapter {chap_num} - {chap_name} successfully created',
            'form-success')

            return redirect(url_for('comic.manage'))

    comics = Comic.get_all_comics()
    return render_template('comic/manage.html', comics=comics, form=form)


@comic.route('/id/<int:comic_id>/info', methods=['GET'])
def show_comic(comic_id):
    comic = Comic.get_comic_by_id(comic_id)
    if not comic:
        abort(404)

    genres = comic.get_genre()

    chapters = comic.get_chaps_all()

    return render_template('comic/info_page.html', comic=comic, genres=genres, chapters=chapters)


@comic.route('/id/<int:comic_id>/chapter/<int:chap_id>/read')
def show_chapter(comic_id, chap_id):
    comic = Comic.get_comic_by_id(comic_id)
    chapter = Chapter.get_chapter(comic_id=comic_id, chap_id=chap_id)

    if not comic or not chapter:
        abort(404)

    pages = chapter.get_pages()

    return render_template('comic/read_chapter.html', pages=pages, comic=comic, chapter=chapter)

@comic.route('/')
def index():
    comics = Comic.get_all_comics()
    return render_template('comic/index.html', comics=comics)