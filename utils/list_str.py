def listToStr(lst):
    if not lst:
        return ""
    return "<ul>" + "".join(f"<li>{item}</li>" for item in lst) + "</ul>"
