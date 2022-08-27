import os
import sys
import click

from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy  
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
  prefix = 'sqlite:///'
else:  # 否则使用四个斜线
  prefix = 'sqlite:////'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'

# 在扩展类实例化前加载配置
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'login required'


@login_manager.user_loader
def user_load(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
  user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
  return user
# Flask-Login 提供了一个 current_user 变量
# 注册这个函数的目的是，当程序运行后，如果用户已登录， current_user 变量的值会是当前用户的用户模型类记录。  


class User(db.Model, UserMixin):  # 表名将会是 user（自动生成，小写处理）
  id = db.Column(db.Integer, primary_key=True)  # 主键
  name = db.Column(db.String(20))  # 名字, 20为字符串最大长度
  username = db.Column(db.String(20))
  password_hash = db.Column(db.String(128))
  
  def print(self):
    print("Name = ", self.name, " Username = ", self.username)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password) # hash 
    
  def validate_password(self, input):
    return check_password_hash(self.password_hash, input)
    

class Movie(db.Model):  # 表名将会是 movie
  id = db.Column(db.Integer, primary_key=True)  # 主键
  title = db.Column(db.String(60))  # 电影标题
  year = db.Column(db.String(4))  # 电影年份


@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
  """Initialize the database."""
  if drop:  # 判断是否输入了选项
    db.drop_all()
  db.create_all()
  click.echo('Initialized database.') 

@app.cli.command()
def show_first_user():
  """show first user"""
  user = User.query.first()
  if user == None:
    print("Empty DataBase.")
  else:
    user.print()
  
@app.cli.command()
@click.option('--name', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(name, password):
  """"Create user."""
  db.create_all()
  
  user = User.query.first()
  if user != None:
    click.echo('Updating user...')
    user.name = name
    user.set_password(password)
  else:
    click.echo('Creating user...')
    user = User(username='Admin', name=name)
    user.set_password(password)
    db.session.add(user)
    
  db.session.commit()
  click.echo('Done')
    

@app.cli.command()
def forge():
  """"Generate Fake Data."""
  db.create_all()
  
  name = 'Simon Bariona'
  movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
  ]
  
  user = User(name=name)
  db.session.add(user)
  for mov in movies:
    movie = Movie(title=mov['title'], year=mov['year'])
    db.session.add(movie)
  db.session.commit()
  click.echo('Done.')
  
@app.context_processor # 处理好每个模板都要传入的参数
def inject_user():
  user = User.query.first() # 读取用户数据
  return dict(user=user)  # 根据context_processor的定义不难发现这里也要返回一个dict
                          # 类似render_template('404.html', user=user)
                            
@app.route('/', methods = ['GET', 'POST'])
def index():
  if request.method == 'POST': # 获取表单数据 参考: https://tutorial.helloflask.com/form/#_3
    if not current_user.is_authenticated:  # 如果当前用户未认证
      return redirect(url_for('index'))  # 重定向到主页
    
    title = request.form['title']
    year = request.form['year']
    if not title or not year or len(year) > 4 or len(title) > 60:
      flash('Invalid Input.')
      return redirect(url_for('index'))
    movie = Movie(title=title, year=year)  # 创建记录
    db.session.add(movie)  # 添加到数据库会话
    db.session.commit()  
    flash('Item created.')
    return redirect(url_for('index'))  # 重定向回主页
    
  movies = Movie.query.all()  # 读取所有电影记录
  return render_template('index.html', movies=movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    name = request.form['username']
    password = request.form['password']

    if not name or not password:
      flash('Invalid input.')
      return redirect(url_for('login'))

    user = User.query.first()
    # 验证用户名和密码是否一致
    if name == user.name and user.validate_password(password):
      login_user(user)  # 登入用户
      flash('Login successfully.')
      return redirect(url_for('index'))  # 重定向到主页

    flash('Invalid username or password.')  # 如果验证失败，显示错误消息
    return redirect(url_for('login'))  # 重定向回登录页面

  return render_template('login.html')

@app.route('/logout')
@login_required # 用于视图保护
def logout(): 
  logout_user()
  flash('Successfully Logout.')
  return redirect(url_for('index'))
  
@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required # 用于视图保护
def edit(movie_id):
  movie = Movie.query.get_or_404(movie_id)

  if request.method == 'POST':  # 处理编辑表单的提交请求
    title = request.form['title']
    year = request.form['year']

    if not title or not year or len(year) != 4 or len(title) > 60:
      flash('Invalid input.')
      return redirect(url_for('edit', movie_id=movie_id))  # 重定向回对应的编辑页面

    movie.title = title  # 更新标题
    movie.year = year  # 更新年份
    db.session.commit()  # 提交数据库会话
    flash('Item updated.')
    return redirect(url_for('index'))  # 重定向回主页

  return render_template('edit.html', movie=movie)  # 传入被编辑的电影记录

@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required # 用于视图保护
def delete(movie_id):
  movie = Movie.query.get_or_404(movie_id)
  db.session.delete(movie)
  db.session.commit()
  flash('Item Deleted.')
  return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
  if request.method == 'POST':
    name = request.form['name']

    if not name or len(name) > 20:
      flash('Invalid input.')
      return redirect(url_for('settings'))

    current_user.name = name
    db.session.commit()
    flash('Settings updated.')
    return redirect(url_for('index'))
  return render_template('settings.html')
  
@app.errorhandler(404) # 接受404状态的异常
def page_not_found(e):
  return render_template('404.html'), 404  # 返回模板和状态码