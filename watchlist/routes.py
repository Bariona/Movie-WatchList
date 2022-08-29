from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user

from watchlist import app, db
from watchlist.models import User, Movie
                     
@app.route('/', methods = ['GET', 'POST'])
def index():
  if request.method == 'POST': # 获取表单数据 参考: https://tutorial.helloflask.com/form/#_3
    if not current_user.is_authenticated:  # 如果当前用户未认证
      return redirect(url_for('index'))  # 重定向到主页
    
    title = request.form['title']
    year = request.form['year']
    if not title or not year or len(year) > 4 or len(title) > 60:
      flash('Invalid input.')
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
  