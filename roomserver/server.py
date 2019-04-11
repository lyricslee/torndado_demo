# -*- coding:utf-8 -*-
from tornado.web import Application,RequestHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
import json
import mysql.connector

class DatabaseHandler(object):

    def __init__(self):
        self.init()

    def init(self):
        self.db = mysql.connector.connect(
            host='185.92.220.26',
            port=3307,
            database='js_db',
            user='root',
            passwd='778899'
        )
        print('connect database success')
        self.dbcursor = self.db.cursor(buffered=True)
        self.dbcursor.execute('select now()')
        print(self.dbcursor.fetchall())

    def executeSql(self, sql):
        print('sql: ', sql)
        try:
            self.dbcursor.execute(sql)
        except:
            self.init()
            self.dbcursor.execute(sql)

    def getAllBooks(self):
        sql = 'select DISTINCT(bookname) from books'
        self.executeSql(sql)
        books = [data[0] for data in self.dbcursor.fetchall()]
        return books

    def setNewUser(self, username):
        sql = 'select name from usersinfo where name="%s"' % username
        self.executeSql(sql)
        data = self.dbcursor.fetchone()
        print('data: ',data)
        if data is None:
            sql = ('insert into usersinfo set name="%s"') % (username)
            self.executeSql(sql)
            self.db.commit()

    def getTasksnumByUsername(self, username):
        sql = 'select dailytask from usertask where username="%s"' % username
        self.executeSql(sql)
        data = self.dbcursor.fetchone()
        if data is not None:
            return data[0]
        else:
            init_tasks = 2
            sql = ('insert into usertask set username="%s", dailytask=%d') % (username, init_tasks)
            self.executeSql(sql)
            self.db.commit()
            return init_tasks

    def getFinishedTasknum(self, username):
        sql = 'select count(*) from readprocess where username="%s"' % username
        sql += 'and DATE_FORMAT(finishtime, "%m/%d/%Y")=DATE_FORMAT(curdate(),"%m/%d/%Y")'
        self.executeSql(sql)
        data = self.dbcursor.fetchone()
        return data[0]

    def getFinishedMaxChapter(self, username, bookname):
        sql = ('select max(chapterid) from readprocess where username="%s" and bookname="%s"') % (username, bookname)
        self.executeSql(sql)
        data = self.dbcursor.fetchone()
        max_chapter = int(data[0]) if data[0] is not None else 0
        print('max_chapter: ', max_chapter)
        return max_chapter

    def getChapterContext(self, bookname, chapterid):
        sql = ('select chaptercontext from books where bookname="%s" and chapter="%s"') % (bookname, chapterid)
        self.executeSql(sql)
        data = self.dbcursor.fetchone()
        return data[0]

    def getChaperTotal(self, bookname):
        sql = 'select count(chapter) from books where bookname="%s"' % bookname
        self.executeSql(sql)
        data = self.dbcursor.fetchone()
        return data[0]

    def updateTasksnum(self, username, tasksnum):
        sql = ('update usertask set dailytask="%s" where username="%s"') % (tasksnum, username)
        self.executeSql(sql)
        self.db.commit()

    def setFinishedChapter(self, username, bookname, chapterid):
        sql = ('select chapterid from readprocess where username="%s" and bookname="%s" and chapterid="%s"') % \
              (username, bookname, chapterid)
        self.executeSql(sql)
        data = self.dbcursor.fetchone()
        print('data: ',data)
        if data is None:
            sql = ('insert readprocess set username="%s", bookname="%s", chapterid="%s", finishtime=now()') % \
                  (username, bookname, chapterid)
            self.executeSql(sql)
            self.db.commit()

    def insertReadComment(self, username, bookname, comment):
        sql = ('insert readcomment set username="%s", bookname="%s", comment="%s", finishtime=now()') % \
              (username, bookname, comment)
        self.executeSql(sql)
        self.db.commit()

    def getBookLastComments(self, bookname):
        sql = ('select username, comment from readcomment where bookname="%s"') % \
              (bookname)
        self.executeSql(sql)
        datas = self.dbcursor.fetchall()
        result = []
        print("datas: ", datas)
        for d in datas:
            if len(d) < 2:
                continue
            result.append({
                "bookname": bookname,
                "username": d[0],
                "comment": d[1]}
            )
        return result

class BaseHandler(RequestHandler):
    dbhandler = DatabaseHandler()

    def set_default_headers(self):
        print("setting headers")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

class BookListHandler(BaseHandler):

    def post(self):
        username = self.get_argument("username")
        print("username=", username)

        self.dbhandler.setNewUser(username)
        books = self.dbhandler.getAllBooks()
        tasksnum = self.dbhandler.getTasksnumByUsername(username)
        finishedtasks = self.dbhandler.getFinishedTasknum(username)
        result = {
            "books": books,
            "todayfinished": finishedtasks,
            "tasksnum": tasksnum,
        }
        print('booklist return: ', result)
        self.write(json.dumps(result))

class BookChapterHandler(BaseHandler):

    def post(self):
        print(self.request)
        username = self.get_argument("username")
        bookname = self.get_argument("bookname")
        print("username=", username, bookname)

        chapter_total = self.dbhandler.getChaperTotal(bookname)
        finished = self.dbhandler.getFinishedMaxChapter(username, bookname)
        next_chapter = finished + 1

        if chapter_total < next_chapter:
            next_chapter = chapter_total
            chapter_context = ''
        else:
            chapter_context = self.dbhandler.getChapterContext(bookname, next_chapter)

        chapter = {
            "chapterid": next_chapter,
            "chaptertotal": chapter_total,
            "context": chapter_context,
        }
        self.write(json.dumps(chapter))

class BookChangeTaskHandler(BaseHandler):

    def post(self):
        print(self.request)
        username = self.get_argument("username")
        tasknum = self.get_argument("tasknum")
        print("username=", username, tasknum)

        self.dbhandler.updateTasksnum(username, tasknum)
        tasksnum = self.dbhandler.getTasksnumByUsername(username)
        finishedtasks = self.dbhandler.getFinishedTasknum(username)

        result = {
            "status": 'success',
            "todayfinished": finishedtasks,
            "tasksnum": tasksnum,
        }
        self.write(json.dumps(result))

class BookFinishReadHandler(BaseHandler):

    def post(self):
        print(self.request)
        username = self.get_argument("username")
        bookname = self.get_argument("bookname")
        chapterid = self.get_argument("chapterid")
        print("username=", username, bookname, chapterid)

        self.dbhandler.setFinishedChapter(username, bookname, chapterid)
        tasksnum = self.dbhandler.getTasksnumByUsername(username)
        finishedtasks = self.dbhandler.getFinishedTasknum(username)

        result = {
            "status": 'success',
            "todayfinished": finishedtasks,
            "tasksnum": tasksnum,
        }
        self.write(json.dumps(result))

class BookCommitCommentHandler(BaseHandler):

    def post(self):
        print(self.request)
        username = self.get_argument("username")
        bookname = self.get_argument("bookname")
        comment = self.get_argument("comment")
        print("username=", username, bookname, comment)

        self.dbhandler.insertReadComment(username, bookname, comment)

        result = {
        }
        self.write(json.dumps(result))

class BookCommentsHandler(BaseHandler):

    def post(self):
        print(self.request)
        bookname = self.get_argument("bookname")
        print("bookname=", bookname)

        result = self.dbhandler.getBookLastComments(bookname)
        self.write(json.dumps(result))

routes = [
    (r'/booklist',BookListHandler),
    (r'/bookchapter', BookChapterHandler),
    (r'/changetask', BookChangeTaskHandler),
    (r'/finishread', BookFinishReadHandler),
    (r'/commitcomment', BookCommitCommentHandler),
    (r'/bookcomments', BookCommentsHandler),
]
app = Application(routes)


if __name__ == '__main__':
    http_server = HTTPServer(app)

    port = 9035
    http_server.bind(port)
    http_server.start(0)
    print('server start: ', port)

    IOLoop.current().start()
