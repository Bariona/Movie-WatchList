# Movie-WatchList by Flask

[成果页面](http://bariona.pythonanywhere.com/)
> 部署在了[pythonanywhere](https://www.pythonanywhere.com/)网站上

[Flask 参考教程](https://tutorial.helloflask.com/)

- `url_for`: 以视图函数名作为参数，返回对应的url

  或者可以直接加载static文件夹中的静态文件
- `db.create_all`: it detects models for us and creates tables for them, if those tables do not exist. If those tables do exist, then db.create_all doesn’t do anything for us.

- [FLlask-WTF](https://flask-wtf.readthedocs.io/en/1.0.x/): Flask拓展, 集成了WTForms

  自动生成对应表单的HTML代码, 省去手动验证的环节

- `unittest`: Python的拓展. 可以支持对项目进行测试, 但是值得注意的一点是默认的测试执行顺序要按照测试函数名**字典序**排序... 对于一些存在依赖性的测试点就要留心了x

- `coverage拓展`: 可以查看整体代码的测试覆盖率并生成对应的HTML文档

## 视图保护:
未登录用户不能执行下面的操作:
- 访问编辑页面
- 访问设置页面
- 执行注销操作
- 执行删除操作
- 执行添加新条目操作

## 模板内容保护:

  比如，不能对未登录用户显示下列内容：
  - 创建新条目表单
  - 编辑按钮
  - 删除按钮