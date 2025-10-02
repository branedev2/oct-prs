from flask import Flask, request, render_template
import flask

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['DEBUG'] = True


@app.route("/")
def start():

    return render_template("index.html")
# {fact rule=cross-site-scripting@v1.0 defects=1}


@app.route("/home", methods=['POST'])
def home():
    injection = request.form['inj_text']
# defect
    return render_template("index.html", injection = flask.Markup(injection))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

# {/fact}

if __name__ == "__main__":
    app.run(host='0.0.0.0')

