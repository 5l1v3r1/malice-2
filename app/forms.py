from flask.ext.wtf import Form
from flask.ext.wtf.file import FileField, FileRequired, FileAllowed
from wtforms import TextField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import Required, Length


class SearchForm(Form):
    hashes = TextAreaField('hashes')#, [Required("Please enter a message.")])
    label = TextField('label')
    submit = SubmitField("Search")
    force = BooleanField('Force', default=False)