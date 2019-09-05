from flask import (Blueprint, render_template, abort, url_for, request, flash,
                  redirect)
from jinja2 import TemplateNotFound
from subscribie import current_app
from subscribie.db import get_db
from base64 import urlsafe_b64encode, urlsafe_b64decode
import sqlite3

module_seo_page_title = Blueprint('seo_page_title', __name__, template_folder='templates')


@module_seo_page_title.route('/list-page-titles')
def list_pages():
  rules = []
  for rule in current_app.url_map.iter_rules():
    rules.append({
              'path': rule, 
              'encodedPath': urlsafe_b64encode(str(rule).encode('ascii')),
              'title': getPathTitle(str(rule))
    })

  try:
    return render_template('list-urls.html', rules=rules)
  except TemplateNotFound:
    return "OK"
    abort(404)

def getPathTitle(path):
  """Return page title of a given path, or None"""
  db = get_db()
  res = db.execute('SELECT title FROM module_seo_page_title WHERE path = ?', (path,)).fetchone()
  if res is None:
    return ''
  else:
    title = res[0]
    return title 

@module_seo_page_title.route('/set-page-title/<encodedPath>', methods=['GET', 'POST'])
def set_page_title(encodedPath):
  path = urlsafe_b64decode(encodedPath).decode('utf-8')
  if request.method == "GET":
    return render_template('set-page-title.html', path=str(path))
  elif request.method == "POST":
    title = request.form['title']
    con = sqlite3.connect(current_app.config['DB_FULL_PATH'])
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO module_seo_page_title (path, title) values (?,?)", (path, title))
    con.commit()
    con.close()
    flash("Page title saved")
    return redirect(url_for('seo_page_title.list_pages'))
