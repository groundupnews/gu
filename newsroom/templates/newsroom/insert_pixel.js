function insertPixel(id)
{
    {% if can_edit  %}
    return;
    {% else %}
    let article = document.getElementById(id);
    if (article) {
        let paras = article.getElementsByTagName('p');
        if (paras.length >= 3) {
            let p = paras[2];
            let img = document.createElement('img');
            img.alt = '';
            img.src =  'https://republish.groundup.org.za/counter/hit/'
                + '{{article.published|date:"Y-m-d"}}/'
                + '{{article.slug}}';
            img.height = "1";
            img.width = "1";
            img.style.height = "1px";
            img.style.width = "1px";
            img.style.visibility = "hidden";
            p.appendChild(img);
        }
    }
    {% endif %}
}
