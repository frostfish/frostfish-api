#!/usr/bin/env python3
# Sample run: gunicorn frost-fish:app -b 0.0.0.0:5000 -D

from flask import Flask, request, jsonify

app = Flask(__name__)

import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ZAKAZ_MAIL = 'zakaz@frost-fish.ru'

def send_mail(toaddr, subject, html):
    fromaddr = 'noreply@frost-fish.ru'
    password = '<password>'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddr

    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP('smtp.yandex.ru:587')
    server.ehlo()
    server.starttls()
    server.login(fromaddr, password)
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()


@app.route('/post-order', methods = ['POST', 'GET'])
def post_order():
    order_data = json.loads(request.get_data().decode("utf-8"))

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
        send_mail(
            mail,
            'Новый заказ на сайте frost-fish.ru',
            html
        )

    return json.dumps({
        'errors': None,
        'message': 'Заказ успешно оформлен'
    })


@app.route('/post-request', methods = ['POST', 'GET'])
def post_request():
    data = request.form.to_dict()
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


if __name__ == '__main__':
    app.run(use_reloader=True)
