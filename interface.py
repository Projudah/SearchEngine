import main
import cgi
from wsgiref.simple_server import make_server
import webbrowser
import access

port = 8080
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
<div class="selections">
<select id="searchType" class='selection' name="searchType">
    <option value="boolean">Boolean Model</option>
    <option value="vsm">Vector Space Model</option>
</select>
<select id="collectionType" class='selection' name="collectionType">
    <option value="uofo">UofO Corpus</option>
    <option value="reuters">Reuters</option>
    </select>
</div>
</form>
''' % query


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
        response = read_static_content(environ['PATH_INFO'])
    else:
        response = begin
        if environ['REQUEST_METHOD'] == 'POST':
            response += post(environ, start_response)
        elif environ['REQUEST_METHOD'] == 'GET':
            response += get(environ, start_response)
        response += end
    start_response(
        '200 OK', [('Content-Type', get_content_type(environ['PATH_INFO']))])
    return [response.encode("utf-8")]


def get(env, resp):
    if env['QUERY_STRING'] == '':
        return search_bar()
    else:
        formData = cgi.FieldStorage(fp=env['wsgi.input'],
                                    environ=env,
                                    keep_blank_values=True)
        if 'query' in formData:
            query = formData['query'].value
            return search_bar(query)+generate_results(query)

        if 'title' in formData:
            title = formData['title'].value
            return generateContent(title)


def generateContent(title):
    cont = access.getDocContent(title)
    return "<h2>%s | %s</h2><div>%s</div>" % (cont[access.ID], cont[access.TITLE], cont[access.FULL])


def post(env, resp):
    post_env = env.copy()
    post_env['QUERY_STRING'] = ''
    post = cgi.FieldStorage(
        fp=env['wsgi.input'],
        environ=post_env,
        keep_blank_values=True
    )
    return generate_results(post['query'])


def generate_results(query):
    idList = main.query(query)
    result = access.getAllDocs(idList)
    resultclass = "aResult"
    resulttitle = resultclass+"_title"
    resultcontent = resultclass + "_content"
    resultdiv = resultclass + "_div"

    html = "<div class='%s'>" % resultclass

    for item in result:
        link = '?title='+item[access.ID]
        itemHtml = "<a href='%s'><div class='%s' >" \
                   "<h2 class='%s'> %s </h2>" \
                   "<p class='%s'> %s </p>" \
                   "</div></a>" % (link, resultdiv, resulttitle,
                                   item[access.TITLE], resultcontent, item[access.EX])
        html += itemHtml
    return html


def selector():
    return '''<select id="model">
  <option value="volvo">Boolean Model</option>
  <option value="saab">VSM Model</option>
  <option value="opel">Opel</option>
  <option value="audi">Audi</option>
</select>'''


def start():
    webbrowser.open_new(website)
    try:
        httpd = make_server('', port, app)
        print('Serving on port', port, 'open', website)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
