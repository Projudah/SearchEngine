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

end = '''</body>
<script>
function fill(sug){
var text = sug.innerHTML
el = document.getElementById('searchInput');
el.value = text;
getsuggestion();
}
function getsuggestion(){
var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("suggestions").innerHTML = this.responseText;
    }
  };
el = document.getElementById('searchInput');
encoded = encodeURI(el.value)
xhttp.open("POST", "", true);
xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
xhttp.send("query="+encoded);
document.getElementById("suggestions").innerHTML = 'Loading...'
}

function expand(el){
var text = el.innerHTML
el = document.getElementById('searchInput');
el.value = text;
document.getElementById('mainSearch').submit()
}
</script>
</html>'''


def search_bar(query=''):
    expansion = None
    if query is not '':
        expansion = main.globalExpand(query)
    suggestion = '''<h2>Suggestions</h2><p onclick="expand(this)">%s</p>''' % (expansion) if expansion else ''
    bar = '''<h1 id="title">Searchify</h1>
<form id="mainSearch" class="formInline" method="get" action="">
<div id='searchdiv'>
	<input autocomplete="off" id='searchInput' list="suggestions" oninput="getsuggestion()" class = "searchBar" type="text" name="query" value="%s" placeholder="Enter a Search Query">
	<div id="suggestions">
    </div>
	<input class = "searchButton" type="submit" value="Search">
</div>
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
    return bar+suggestion


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
        response = ''
        if environ['REQUEST_METHOD'] == 'POST':
            response += post(environ, start_response)
        elif environ['REQUEST_METHOD'] == 'GET':
            response = begin
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
    return generateSuggestions(post['query'].value)

def generateSuggestions(query):
    sugs = main.complete(query)
    suggestions = ''
    for data in sugs:
        suggestions += '<div class="aSuggest" onclick="fill(this)">'+query.strip()+' '+data+'</div>'
    return suggestions

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

def start():
    webbrowser.open_new(website)
    try:
        httpd = make_server('', port, app)
        print('Serving on port', port, 'open', website)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
