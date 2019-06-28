# coding=utf-
from flask import Flask, jsonify, request,Flask,redirect
from flask_pymongo import PyMongo
from flask_restful import Resource, Api
from flask_mail import Mail, Message
from threading import Thread
from pymongo import MongoClient
from flask import render_template
from snownlp import SnowNLP
app = Flask(__name__)
# 加载配置文件
app.config.from_pyfile('config.ini')
api = Api(app)
mongo = PyMongo(app)
mail = Mail(app)
app.url_map.strict_slashes = False # Disable redirecting on POST method from /star to /star/
# 开启异步加载进行发送
def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)
def send_email(name,email,subject,message):
    msg = Message( '你收到一条来自网站的留言：我是{},{}'.format(name,subject), recipients=["630117639@qq.com"])
    # recipients是个列表，包含所有收件人
    # 此处的test是邮箱的主题，sender和config中的MAIL_USERNAME要一致哦
    msg.body = '你好，我是{}，{}，我的邮箱是{}，我有一些事情需要向您请教，{},感谢。{}'.format(name,subject,email,message,name)
    # 邮件发送给目标，可以有文本，两种方式呈现，你能看见怎样的取决于你的客户端
    thr = Thread(target=send_async_email, args=[app, msg])
    # 使用多线程，在实际开发中，若是不使用异步、多线程等方式，网页会卡住
    thr.start()
@app.route('/',methods=['GET','POST'])
def index():
    # 提取表单内容
    if request.method == 'POST':
        name = request.form.get('form-name')
        email = request.form.get('form-email')
        subject = request.form.get('form-subject')
        message = request.form.get('form-message')
        if len(str(message))>5:
            send_email(name, email, subject, message)
        # 对所有的页面使用重定向可以解决页面表单form的历史输入问题
        return redirect('/')
    return render_template('index.html')
class get_api(Resource):
    def get(self,id):
        import time
        st=time.clock()
        star = mongo.db.hot
        output = []
        s1 = star.find({'question_id':int(id)})
        for s in s1:
            question_title = s[u'question_title']
            output.append({'question_title':str(question_title), 'hot_point':s['hot_point'],
                           'rank':s['rank'], 'update_time':s['crawled_time'],'type':s['type']})
        print(time.clock()-st)
        return jsonify({'result': output})
class Sentiment_analysis(Resource):
    def get(self,comment):
        import time
        s=time.clock()
        sa=SnowNLP(comment).sentiments
        output = {'comment':comment, 'sa':sa}
        print(time.clock()-s)
        return jsonify({'result': output})

class post_api(Resource):
    def get(self,id):
        import time
        st=time.clock()
        star = mongo.db.hot
        output = []
        s1 = star.find({'question_id':int(id)})
        for s in s1:
            output.append({'question_title':s[u'question_title'], 'hot_point':s['hot_point'],
                           'rank':s['rank'], 'update_time':s['crawled_time'],'type':s['type']})
        print(time.clock()-st)
        return jsonify({'result': output})
    def post(self,id):
        # curl -X POST http://127.0.0.1:5000/post_api/330354375
        import time
        st = time.clock()
        star = mongo.db.hot
        output = []
        s1 = star.find({'question_id': int(id)})
        for s in s1:
            output.append({'question_title': s[u'question_title'], 'hot_point': s['hot_point'],
                           'rank': s['rank'], 'update_time': s['crawled_time'], 'type': s['type']})
        print(time.clock() - st)
        return jsonify({'result': output})
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')
@app.errorhandler(500)
def not_found(error):
    return render_template('404.html')
api.add_resource(post_api, '/post_api/<string:id>')
# id必须使用不带有/的符号，传参数使用<string:id>
api.add_resource(get_api, '/hot_research_api/<string:id>')
# 情感分析api
api.add_resource(Sentiment_analysis, '/sa_api/<string:comment>')
# http://127.0.0.1:5000/hot_research_api/330354375
# http://127.0.0.1:5000/post_api/330354375
# http://127.0.0.1:5000/sa_api/有家的感觉
# 关键字api，主要显示当前zhihu的热点信息


# 时序信息api,显示某一个热点事件的整体热度表现，以及对其进行预测和显示
if __name__ == '__main__':
    # 使用ipconfig进行调试，http://172.20.10.7:5000/hot_research_api/330354375
    # app.run(host='0.0.0.0')
    app.run()