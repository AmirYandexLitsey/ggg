from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return "<h1>Миссия Колонизация Марса</h1>"


@app.route('/index')
def index2():
    return "<h2>И на Марсе будут яблони цвести!</h2>"


# @app.route('/sample_page')
# def return_sample_page():
#     return """<!doctype html>
#                 <html lang="en">
#                   <head>
#                     <meta charset="utf-8">
#                     <title>Привет, Яндекс!</title>
#                   </head>
#                   <body>
#                     <h1>Первая HTML-страница</h1>
#                   </body>
#                 </html>"""
#
#
# @app.route('/count')
# def countdown():
#     count_list = [str(x) for x in range(10, 0, -1)]
#     count_list.append('GO!!!!')
#     return '</br>'.join(count_list)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
