from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

@app.route('/')
def main_page():
    return "sup"

