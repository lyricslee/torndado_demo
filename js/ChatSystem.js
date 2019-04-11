
//const host = 'http://localhost:9035';
const host = 'http://178.128.44.144:9035';
const bookListRequest = '/booklist';
const bookChapterRequest = '/bookchapter';
const changeDailyTaskRequest = '/changetask';
const finishReadRequest = '/finishread';
const commitReadComment = '/commitcomment';
const bookCommentsRequest = '/bookcomments';

PlayerName = $.cookie("uuuname");
console.log('username: ', PlayerName);
var readingChapterId;

function httpGetAsync(theUrl, callback)
{
    console.log('Get URL: ', theUrl);
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    };
    xmlHttp.open("GET", theUrl, true); // true for asynchronous
    xmlHttp.send(null);
}

function httpPostAsync(theUrl, data, callback)
{
    console.log('POST URL: ', theUrl, data);

    $.post(theUrl, data, function(result){
        results = JSON.parse(result);
        console.log('results: ', results);
        callback(results);
    });
}

var books = {};

function initBooks(){
    var booklist = document.getElementById("booklist");
    var senddata = {'username': PlayerName};
    var url = host + bookListRequest;

    httpPostAsync(url, senddata, function(results){

        var allbooks = results['books'];
        var todayfinished = results['todayfinished'];
        var tasksnum = results['tasksnum'];

        var booklist = document.getElementById("booklist");
        booklist.innerHTML = '';
        for (var i = 0; i < allbooks.length; ++i) {
            value = i.toString();
            bookname = allbooks[i];
            str = '<option value=' + value +'>'+ bookname + '</option>';
            booklist.innerHTML += str;

            books[value] = allbooks[i];
        }

        var taskProcess = todayfinished.toString() + '/' + tasksnum.toString();
        var currentBook = document.getElementById("currentBook");
        currentBook.innerHTML = books[booklist.value];
        var taskProcessDiv = document.getElementById("taskProcess");
        taskProcessDiv.innerHTML = taskProcess;

        getBookNextChapter();
        getBookLastComments();
    });
}

function getBookNextChapter() {
    var booklist = document.getElementById("booklist");
    var bookname = books[booklist.value];
    var senddata = {'bookname': bookname, 'username': PlayerName};
    var url = host + bookChapterRequest;

    httpPostAsync(url, senddata, function(results){
        var chapterContext = document.getElementById("chapterContext");
        var chapterId = document.getElementById("chapterId");

        chapterId.innerHTML = 'chapter: ' + results['chapterid'];
        chapterContext.innerHTML = results['context'];
        readingChapterId = results['chapterid'];

        var currentBook = document.getElementById("currentBook");
        currentBook.innerHTML = books[booklist.value];
    });
}

function getBookLastComments() {
    var comments = document.getElementById("comments");
    var booklist = document.getElementById("booklist");
    var bookname = books[booklist.value];
    var senddata = {'bookname': bookname};
    var url = host + bookCommentsRequest;

    httpPostAsync(url, senddata, function(results){
        console.log(results);

        comments.innerHTML = "";
        for (var i = 0; i < results.length; i++) {
            data = results[i];
            str = '<div class="comment_context_con"><span>' + data["username"] + ": " + data["comment"] +'</span></div>';
            comments.innerHTML += str;
        }
    });
}

function getCurrentBoookTasks() {
    var booklist = document.getElementById("booklist");
    //var senddata = {'bookname': booklist.value};
    var senddata = {'bookname': 'ck nu', 'username': PlayerName};

    console.log('booklist.value: ', booklist.value);

    httpPostAsync(host+booktasks_request, senddata, function(results){
        results = JSON.parse(results);
        console.log('results: ', results);

        var booktasks = document.getElementById("booktasks");
        booktasks.innerHTML = '';
        for (var i = 0; i < results.length; ++i) {
            str = results[i]['task'].toString() + ' ' + results[i]['finish'].toString() + '%';
            str = '<option value=' + i.toString() +'>'+ str + '</option>';
            booktasks.innerHTML += str;
        }
    });
}

function booklistOnChange(){
    httpGetAsync(host+booklist_request, function(results){
        books = JSON.parse(results);
        console.log('results: ', results);

        booklist.innerHTML = '';
        for (var i = 0; i < books.length; ++i) {
            var value = i+1;

            str = '<option value=' + value.toString() +'>'+ books[i] + '</option>';
            booklist.innerHTML += str;
        }
    })
}

function onChangeDailyTask(){
    var booklist = document.getElementById("booklist");
    var booktasks = document.getElementById("booktasks");
    var senddata = {'tasknum': booktasks.value, 'username': PlayerName};
    var url = host + changeDailyTaskRequest;

    httpPostAsync(url, senddata, function(results){
        var taskProcess = results['todayfinished'] + '/' + results['tasksnum'];
        var taskProcessDiv = document.getElementById("taskProcess");
        taskProcessDiv.innerHTML = taskProcess;
    });
}

function onFinishRead(){
    var booklist = document.getElementById("booklist");
    var bookname = books[booklist.value];
    var senddata = {'bookname': bookname, 'username': PlayerName, 'chapterid': readingChapterId};
    var url = host + finishReadRequest;

    httpPostAsync(url, senddata, function(results){
        var taskProcess = results['todayfinished'] + '/' + results['tasksnum'];
        var currentBook = document.getElementById("currentBook");
        currentBook.innerHTML = books[booklist.value];
        var taskProcessDiv = document.getElementById("taskProcess");
        taskProcessDiv.innerHTML = taskProcess;
    });
}

function onCommitComment(){
    var comments = document.getElementById("comments");
    var commentContext = document.getElementById("commentContext");

    if(commentContext.value == ""){
        alert("empty comment context");
        return;
    }

    var booklist = document.getElementById("booklist");
    var bookname = books[booklist.value];
    var senddata = {'bookname': bookname, 'username': PlayerName, 'comment': commentContext.value};
    var url = host + commitReadComment;

    httpPostAsync(url, senddata, function(results){
        str = '<div class="comment_context_con"><span>' + PlayerName + ": " + commentContext.value  +'</span></div>';
        comments.innerHTML += str;

        commentContext.value = "";
    });
};

window.onload = function(){
    initBooks();

    var booklist = document.getElementById("booklist");
    var changeDailyTask = document.getElementById("changeDailyTask");
    var finishRead = document.getElementById("finishRead");
    var nextChapter = document.getElementById("nextChapter");
    var commitComment = document.getElementById("commitComment");

    booklist.onchange = function(){
        getBookNextChapter();
        getBookLastComments();
    };
    changeDailyTask.onclick =function () {
        onChangeDailyTask();
    };
    finishRead.onclick =function () {
        onFinishRead();
    };
    nextChapter.onclick =function () {
        getBookNextChapter();
    };
    commitComment.onclick =function () {
        onCommitComment();
    };
};

