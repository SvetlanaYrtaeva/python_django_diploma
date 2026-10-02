import re


class FixScriptTagMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not hasattr(response, "content"):
            return response

        try:
            content = response.content.decode("utf-8")
        except (UnicodeDecodeError, AttributeError):
            return response

        if "</body>" not in content:
            return response


        footer_pos = content.rfind("</footer>")
        if footer_pos != -1:
            body_pos = content.find("</body>", footer_pos)
            if body_pos != -1:
                footer_end = footer_pos + len("</footer>")
                mixins_area = content[footer_end:body_pos]

                script_re = re.compile(
                    r'<script\b[^>]*\bsrc="[^"]*"[^>]*>\s*</script>\s*',
                    re.IGNORECASE,
                )

                scripts = script_re.findall(mixins_area)
                if scripts:
                    print(f"[FixScriptTag] Moving {len(scripts)} scripts after </body>")
                    mixins_clean = script_re.sub("", mixins_area)
                    scripts_html = "\n".join(s.strip() for s in scripts)
                    content = (
                        content[:footer_end]
                        + mixins_clean
                        + "</body>\n"
                        + scripts_html
                        + "\n"
                        + content[body_pos + len("</body>"):]
                    )

        patch = """<script>
(function(){
  function patchMask(){
    if(window.jQuery && jQuery.fn && !jQuery.fn._mp){
      var orig = jQuery.fn.mask;
      if(typeof orig === 'function'){
        jQuery.fn.mask = function(){
          try { return orig.apply(this, arguments); }
          catch(e) { return this; }
        };
        jQuery.fn._mp = true;
        console.log('[FixScriptTag] jQuery.mask patched OK');
      }
    }
  }
  var iv = setInterval(function(){
    patchMask();
    if(window.jQuery && jQuery.fn && jQuery.fn._mp) clearInterval(iv);
  }, 10);
  // Запасной таймаут — перестать проверять через 5 секунд
  setTimeout(function(){ clearInterval(iv); }, 5000);
})();
</script>"""

        if "</head>" in content:
            content = content.replace("</head>", patch + "\n</head>", 1)

        response.content = content.encode("utf-8")
        response["Content-Length"] = str(len(response.content))

        return response
