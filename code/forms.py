from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerRangeField, SubmitField
from wtforms import validators

class ReviewForm(FlaskForm):
    username = StringField("Username:", [validators.InputRequired()],
                           render_kw={"style": "font-family: 'Gotham-Black', sans-serif;"
                                               "font-size: 18px;"
                                               "height: 18px;"
                                               "width: 250px;"
                                               "border-radius: 8px;"
                                               "padding: 8px;",
                                               "class": "custom-class"})

    singer = StringField("Singer:", [validators.InputRequired()],
                         render_kw={"style": "font-family: 'Gotham-Black', sans-serif;"
                                             "font-size: 18px;"
                                             "height: 18px;"
                                             "width: 250px;"
                                             "border-radius: 8px;"
                                             "padding: 8px;",
                                             "class": "custom-class"})

    song = StringField("Song:", [validators.InputRequired()],
                       render_kw={"style": "font-family: 'Gotham-Black', sans-serif;"
                                           "font-size: 18px;"
                                           "height: 18px;"
                                           "width: 250px;"
                                           "border-radius: 8px;"
                                           "padding: 8px;",
                                           "class": "custom-class"})

    review = TextAreaField("Review:", [validators.InputRequired()],
                           render_kw={"style": "font-family: 'Gotham-Black', sans-serif;"
                                               "font-size: 18px;"
                                               "height: 18px;"
                                               "width: 250px;"
                                               "border-radius: 8px;"
                                               "padding: 8px;",
                                               "class": "custom-class"})

    lyrics = IntegerRangeField("Lyrics:", [validators.NumberRange(min=1, max=10)])
    structure = IntegerRangeField("Song structure:", [validators.NumberRange(min=1, max=10)])
    performance = IntegerRangeField("Performance:", [validators.NumberRange(min=1, max=10)])
    mixing = IntegerRangeField("Mixing:", [validators.NumberRange(min=1, max=10)])
    individuality = IntegerRangeField("Individuality:", [validators.NumberRange(min=1, max=10)])
    charisma = IntegerRangeField("Charisma:", [validators.NumberRange(min=1, max=10)])
    atmosphere = IntegerRangeField("Atmosphere:", [validators.NumberRange(min=1, max=10)])
    instrumental = IntegerRangeField("Instrumental:", [validators.NumberRange(min=1, max=10)])
    submit = SubmitField("Send")
