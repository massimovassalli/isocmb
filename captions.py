
f = open("assets/carousel/caption.txt", "r", encoding="utf-8")
lines = f.readlines()

Template = """
    <!-- Slide {n} -->
    <div class="carousel-item {active}">
        <img src="assets/carousel/00{n}.jpg" class="d-block w-100" alt="Glasgow SynSci ISMB" />
        <div class="container">
            <div class="carousel-caption text-start">
                <span class="badge text-bg-primary brand-badge mb-2">{Badge}</span>
                <h1 class="fw-bold">{Title}</h1>
                <p>{Description}</p>
                <p><a class="btn btn-lg btn-primary" href="{Link}">{LinkText}</a></p>
            </div>
        </div>
    </div>
"""

core = '<div id="ismbCarousel" class="carousel slide" data-bs-ride="carousel">\n\t<div class="carousel-indicators">\n'
core += '\t\t<button type="button" data-bs-target="#ismbCarousel" data-bs-slide-to="0" class="active" aria-current="true" aria-label="Slide 1"></button>\n'
for i in range(1,9):
    core += f'\t\t<button type="button" data-bs-target="#ismbCarousel" data-bs-slide-to="{i}" aria-label="Slide {i+1}"></button>'
core += '\t</div>'

core += '\t<div class="carousel-inner">\n'


for i, line in enumerate(lines[1:]):
    parts = line.strip().split("|")
    if len(parts) != 5:
        continue
    Title = parts[0].strip()
    Badge = parts[1].strip()
    Link = parts[2].strip()
    LinkText = parts[3].strip()
    Description = parts[4].strip()
    if i == 0:
        isactive = "active"
    else:
        isactive = ""
    core += '\t\t'
    core += Template.format(n=i+1, Title=Title, Badge=Badge, Link=Link, LinkText=LinkText, Description=Description,active=isactive)

core+="\n\t</div>"

core += '''
    <button class="carousel-control-prev" type="button" data-bs-target="#ismbCarousel" data-bs-slide="prev">
      <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Previous</span>
    </button>
    <button class="carousel-control-next" type="button" data-bs-target="#ismbCarousel" data-bs-slide="next">
      <span class="carousel-control-next-icon" aria-hidden="true"></span>
      <span class="visually-hidden">Next</span>
    </button>
  </div>
'''

nf = open("assets/carousel/caption_output.txt", "w", encoding="utf-8")
nf.write(core)
