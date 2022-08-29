from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import (
    StringField,
    SubmitField,
    FloatField,
    TextAreaField
)
from wtforms.fields.html5 import EmailField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.models import Comic
from app.utils import CustomSelectField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
)


from app import db

class NewComicForm(FlaskForm):
    name = StringField('Comic Name', validators=[InputRequired(), Length(1, 64)])
    desc = TextAreaField('Description', validators=[InputRequired(), Length(1, 2000)])
    genre = StringField('Genre name, seperated by commas', validators=[InputRequired(), Length(1, 64)])
    alternative_name = StringField('Alternative name, seperated by commas', validators=[InputRequired(), Length(1, 64)])
    cover_image = FileField(validators=[FileRequired(), FileAllowed(['jpg', 'png', 'webp'], 'Images only!')])
    submit = SubmitField("Create New")


class UploadChapter(FlaskForm):
    comic = QuerySelectField(
        'Comic Name',
        validators=[InputRequired()],
        allow_blank=True,
        get_label='name',
        blank_text='Select Comic',
        query_factory=lambda: Comic.query.all())
    name = StringField('Chapter Name', validators=[InputRequired(), Length(1, 64)])
    number = FloatField('Chaper Number', validators=[InputRequired()])
    chap_zip = FileField('Chapter Zip File', validators=[FileRequired(), FileAllowed(['zip'], 'Zip files only!')])
    submit = SubmitField("Upload Chapter")


class UpdateComic(FlaskForm):
    comic = QuerySelectField(
        'Comic Name',
        validators=[InputRequired()],
        allow_blank=True,
        get_label='name',
        blank_text='Select Comic',
        query_factory=lambda: Comic.query.all())


class DeleteComic(FlaskForm):
    comic = QuerySelectField(
        'Comic Name',
        validators=[InputRequired()],
        allow_blank=True,
        get_label='name',
        blank_text='Select Comic',
        query_factory=lambda: Comic.query.all())
    submit = SubmitField("Delete Comic")



