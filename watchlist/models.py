from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from watchlist import db

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