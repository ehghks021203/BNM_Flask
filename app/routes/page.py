from flask import Blueprint, jsonify, request, render_template
from config import BASE_DIR
import os
from datetime import datetime

page_routes = Blueprint("page", __name__)

@page_routes.route("/notion_list")
def notion_list():
    """공지사항 리스트 페이지
    """
    COMMON_PATH = BASE_DIR + "/app/templates/notions"
    PIN_PATH = BASE_DIR + "/app/templates/notions/pin"
    pin_items = []
    common_items = []
    common_list = os.listdir(COMMON_PATH)
    pin_list = os.listdir(PIN_PATH)
    for l in common_list:
        if len(l.split(".")) == 2:
            if l.split(".")[1] == "html":
                title = l.split(".")[0]
                date = datetime.fromtimestamp(os.path.getctime(COMMON_PATH + "/" + title + ".html"))
                file_id = 0
                for c in title + date.strftime("%Y-%m-%d %H:%M:%S"):
                    file_id += ord(c)
                common_items.append({"id":file_id, "pin":"non", "date":date.strftime("%Y-%m-%d %H:%M:%S"), "title":title})

    for l in pin_list:
        if len(l.split(".")) == 2:
            if l.split(".")[1] == "html":
                title = l.split(".")[0]
                date = datetime.fromtimestamp(os.path.getctime(PIN_PATH + "/" + title + ".html"))
                file_id = 0
                for c in title + date.strftime("%Y-%m-%d %H:%M:%S"):
                    file_id += ord(c)
                pin_items.append({"id":file_id, "pin":"pin", "date":date.strftime("%Y-%m-%d %H:%M:%S"), "title":title})

        
    return render_template("index.html", pin_items=pin_items, common_items=common_items)

@page_routes.route("/notion", methods=["GET"])
def show_notion():
    """공지사항 페이지
    """
    file_name = request.args.get("name")
    locate = request.args.get("locate")
    if not locate:
        return render_template(f"notions/{file_name}.html")
    else:
        return render_template(f"notions/{locate}/{file_name}.html")
