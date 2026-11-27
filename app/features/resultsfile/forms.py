from flask_wtf import FlaskForm
from wtforms import SubmitField


class ResultsFileForm(FlaskForm):
    submit = SubmitField("Save resultsfile")
