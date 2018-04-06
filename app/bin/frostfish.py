#!/usr/bin/env python3
# coding: utf-8

import flask
import flask_cors
import json
import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


app = flask.Flask(__name__)
flask_cors.CORS(app)
FROM_MAIL = 'noreply@frost-fish.ru'
ZAKAZ_MAIL = 'zakaz@frost-fish.ru'
PASSWORD = os.environ['MAIL_PASSWORD']

def get_smtp():
    if not hasattr(flask.g, 'smtp'):
        flask.g.smtp = smtplib.SMTP('smtp.yandex.ru:587')
        flask.g.smtp.ehlo()
        flask.g.smtp.starttls()
        flask.g.smtp.login(FROM_MAIL, PASSWORD)

    return flask.g.smtp

def send_mail(toaddr, subject, html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = FROM_MAIL
    msg['To'] = toaddr
    msg.attach(MIMEText(html, 'html'))

    get_smtp().sendmail(FROM_MAIL, toaddr, msg.as_string())


@app.route('/post-order', methods = ['POST', 'GET'])
def post_order():
    order_data = json.loads(flask.request.get_data().decode("utf-8"))

    print(order_data)
    html = '''\
    <html>
      <head></head>
      <body>
        <p>Здравствуйте!</p>
        <p>Вами был оформлен заказ на сайте <a href="http://frost-fish.ru">frost-fish.ru</a>.</p>
        <p>Телефон: {phone}</p>
        <p>Почта: {mail}</p>
        <p>Комментарий: {comment}</p>
        <table>
        <tr>
          <th>#</th><th>Название</th><th>Количество</th>
        </tr>
    '''.format(**order_data['userdata'])

    total_price = 0

    for i, key in enumerate(sorted(order_data['orderlist'])):
        pos = order_data['orderlist'][key]
        html += '<tr><td>{}</td>'.format(i+1)
        html += '<td>{title}</td><td>{count}</td>\n'.format(**pos)
        html += '</tr>'
        total_price += pos['count'] * pos['price']

    html += '''\
      </table>
      <p>Общая стоимость заказа: {} руб.</p>
      <p>В ближайшее время с вами свяжется менеджер для уточнения деталей и подтверждения заказа.</p>
      </body>
    </html>
    '''.format(total_price)

    recipients = [ZAKAZ_MAIL]

    if order_data['userdata']['mail']:
        recipients.append(order_data['userdata']['mail'])

    for mail in recipients:
        try:
            send_mail(
                mail,
                'Новый заказ на сайте frost-fish.ru',
                html
            )
        except Exception as e:
            print('Error while sending mail:\n{}'.format(e))

    return json.dumps({
        'errors': None,
        'message': 'Заказ успешно оформлен'
    })


@app.route('/post-request', methods = ['POST', 'GET'])
def post_request():
    data = flask.request.form.to_dict()
    if not 'comment' in data:
        data['comment'] = ''

    html = '''\
    <html>
      <head></head>
      <body>
        <p>Телефон: {client_phone}</p>
        <p>Комментарий: {comment}</p>
      </body>
    </html>
    '''.format(**data)

    send_mail(
        ZAKAZ_MAIL,
        'Форма заявки сайта для {client_phone}'.format(**data),
        html
    )

    return 'Заявка отправлена'


@app.route('/ping', methods = ['POST', 'GET'])
def ping():
    return 'All is OK'


if __name__ == '__main__':
    app.run()
