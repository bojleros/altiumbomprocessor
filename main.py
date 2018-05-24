import os
import sqlite3
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import logging


app = Flask(__name__)

body='''
    <!doctype html>
    <title>bojleros BoM optimizer</title>
    <h1>Upload simple BOM Altium csv</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>'''
  

@app.route('/', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    # check if the post request has the file part
    if 'file' not in request.files:
#      flash('No file part')
      return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
#      flash('No selected file')
      return redirect(request.url)


  try:
    file
  except:
    return body + "We need a file ..."
  
  #File was posted , time to process it
  stdout=""
  stderr=""

  db = sqlite3.connect(':memory:')
  cur = db.cursor()

  line_num=1
  cols = None
  cols_num = None
  data = []
  #this can fail on diacretic signs
  lines = file.read().decode("utf-8").splitlines()
  for l in lines:
    if line_num == 1:
      cols = l.lower().split(',')
      cols_num=len(cols)
      q = '''CREATE TABLE bom(id INTEGER PRIMARY KEY,'''
      for cl in cols:
        q += " " + cl
        if cl == "Quantity":
          q += " INT,"
        else:
          q += " TEXT,"
      q = q.rstrip(',') + ')'
      #creating table
      cur.execute(q)
      db.commit()
    else:
      ls = l.split('","')
      if len(ls) == cols_num:
        ls[0]=ls[0].strip('"')
        ls[cols_num-1] = ls[cols_num-1].strip('"')
        data.append(tuple(ls))
      else:
        stderr += "Skipping line " +str(line_num)+ " : " + str(ls) + '<br>'

    line_num += 1

  #pushing the data in
  q = '''INSERT INTO bom(''' + ','.join(cols) + ''') VALUES(''' + ','.join(['?'] * cols_num) + ''')'''
  cur.executemany(q,data)
  db.commit()

  stdout+="<h3>Optimized for shopping</h3><br>"
  q='''SELECT COUNT(comment),comment,footprint,group_concat(designator),description FROM bom GROUP BY comment,footprint ORDER BY COUNT(comment) DESC'''
  cur.execute(q)
  for a in cur.fetchall():
    stdout += ';'.join(map(str,a)) +'<br>'

  stdout += "<br><br><h3>Optimized for fabrication/placement</h3><br><h4>Top Layer</h4><br>"

  q='''SELECT COUNT(comment),comment,footprint,group_concat(designator),layer,description FROM bom WHERE layer=='Top' GROUP BY layer,comment,footprint ORDER BY layer,COUNT(comment) DESC'''
  cur.execute(q)
  for a in cur.fetchall():
    stdout += ';'.join(map(str,a)) +'<br>'

  stdout += "<br><br><h3>Optimized for fabrication/placement</h3><br><h4>Bottom Layer</h4><br>"

  q='''SELECT COUNT(comment),comment,footprint,group_concat(designator),layer,description FROM bom WHERE layer=='Bottom' GROUP BY layer,comment,footprint ORDER BY layer,COUNT(comment) DESC'''
  cur.execute(q)
  for a in cur.fetchall():
    stdout += ';'.join(map(str,a)) +'<br>'

  db.close()

  return body + "<br>stdout:<br>" + str(stdout) + "<br>stderr:<br>" + str(stderr)

if __name__ == '__main__':
  app.run(debug=True,host='0.0.0.0',port=80)

