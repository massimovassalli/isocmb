from mako.template import Template

mytemplate = Template("hello world!")

pages = [['index','Home'],['history','About'],['board','Board'],['ismb','ISMB']]

for page in pages:
    f = open('build/'+page[0]+'.html','w')
    f.write(Template(filename="templates/header.mako").render(pages=pages,page=page[0]))
    f.write(Template(filename=f"templates/{page[0]}.mako").render())
    f.write(Template(filename="templates/footer.mako").render(pages=pages,page=page))

