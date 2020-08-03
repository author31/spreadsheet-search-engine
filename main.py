import sys
import gspread
import pandas as pd
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, render_template, url_for, request, session

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name("sample.json", scope)
gc = gspread.authorize(credentials)


app = Flask(__name__)
app.config["SECRET_KEY"] ="secretkeys"

class BasicForm(FlaskForm):
    ids = StringField("ID",validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route("/",methods =['POST','GET'])
def main():
    form = BasicForm()
    return render_template("index.html",form = form)


@app.route("/search",methods=["POST"])
def search():
    table = gc.open("contacts").sheet1
    data = table.get_all_values()
    header = data.pop(0)
    df = pd.DataFrame(data,columns= header)
    form = BasicForm()
    if form.validate_on_submit():
        name = request.form["ids"]
        result = df[df["first_name"].str.lower()==name]
        session["result"] = result.to_json()
    return render_template("searching.html",columns = header, record = list(result.values.tolist()))

@app.route("/print")
def print():
    df = pd.read_json(session["result"])
    return render_template("print.html",record = list(df.values.tolist()))


if __name__ == "__main__":
    app.run(debug=True)