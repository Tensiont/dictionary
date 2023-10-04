import os
import sys

import click
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy

WIN=sys.platform.startswith('win')
if WIN:  #如果是windows系统
    prefix='sqlite:///'
else:  #其它系统
    prefix='sqlite:////'

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'  # 等同于 app.secret_key = 'dev'
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

class Word(db.Model):  #表名将会是 word （自动生成，小写处理)
    id=db.Column(db.Integer,primary_key=True)  #主键
    en=db.Column(db.String(50))  #英文
    ch=db.Column(db.String(50))  #中文

@app.cli.command()  #注册为命令
def init():
    """
    导入初始单词数据
    """
    db.create_all()
    words=[
        {'en':'tension','ch':'张力'},
        {'en':'python','ch':'蟒蛇'}
    ]

    for w in words:
        word=Word(en=w['en'],ch=w['ch'])
        db.session.add(word)

    db.session.commit()
    click.echo('已导入初始单词数据')

#init()

from flask import request, url_for, redirect, flash
@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        # 从表单中获取数据
        en=request.form.get('en')
        ch=request.form.get('ch')
        if not en or not ch or len(en)>45 or len(ch)>45:
            flash('无效输入')
            return redirect(url_for('index'))
        #保存表单数据到数据库
        word=Word(en=en,ch=ch)
        db.session.add(word)
        db.session.commit()
        flash('新添单词：'+en)

        return redirect(url_for('index'))  #重定向回主页
    words=Word.query.all()
    return render_template('index.html',words=words)