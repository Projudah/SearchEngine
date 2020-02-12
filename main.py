import cgi
from wsgiref.simple_server import make_server
import webbrowser

port = 8888
website = "http://localhost:"+str(port)
begin = '''<html>
<head>
	<title>Search Page</title>
	<link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>'''

end = '''</body></html>'''

def search_bar(query=''):
    return '''<h1 id="title">Searchify</h1>
<form class="formInline" method="get" action="">
	<input class = "searchBar" type="text" name="query" value="%s" placeholder="Enter a Search Query">
	<input class = "searchButton" type="submit" value="Search">
</form>''' % query

def get_content_type(pathInfo):
    if pathInfo.endswith(".css"):
        return "text/css"
    else:
        return "text/html"

def read_static_content(filename):
    with open('.'+filename, 'r') as f:
        return f.read()

def app(environ, start_response):
    if get_content_type(environ['PATH_INFO']) == "text/css":
        response =  read_static_content(environ['PATH_INFO'])
    else:
        response = begin
        if environ['REQUEST_METHOD'] == 'POST':
            response += post(environ, start_response)
        elif environ['REQUEST_METHOD'] == 'GET':
            response += get(environ, start_response)
        response += end
    start_response('200 OK', [('Content-Type', get_content_type(environ['PATH_INFO']))])
    return [response.encode("utf-8")]

def get(env, resp):
    if env['QUERY_STRING'] == '':
        return search_bar()
    else:
        formData = cgi.FieldStorage(fp=env['wsgi.input'],
            environ=env,
            keep_blank_values=True)
        query = formData['query'].value
        return search_bar(query)+generate_results()

def post(env, resp):
    post_env = env.copy()
    post_env['QUERY_STRING'] = ''
    post = cgi.FieldStorage(
        fp=env['wsgi.input'],
        environ=post_env,
        keep_blank_values=True
    )
    print(post['query'])
    return generate_results()

def generate_results():
    result = [['Title 1', 'Content 1'],['Title 2', 'Content 2'],['Title 3', 'Content 3'],['Title 4', 'Content 4'],['Title 5', 'Content 5']]
    resultclass = "aResult"
    resulttitle = resultclass+"_title"
    resultcontent = resultclass + "_content"
    resultdiv = resultclass + "_div"

    html = "<div class='%s'>" % resultclass

    for item in result:
        itemHtml = "<div class='%s' >" \
                   "<h2 class='%s'> %s </h2>" \
                   "<p class='%s'> %s </p>" \
                   "</div>" % (resultdiv, resulttitle, item[0], resultcontent, item[1])
        html += itemHtml
    return html
        

def start():
    try:
        httpd = make_server('', port, app)
        print('Serving on port',port, 'open',website)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')

if __name__ == '__main__':
    # webbrowser.open_new(website)
    start()
