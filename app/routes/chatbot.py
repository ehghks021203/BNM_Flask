from flask import Blueprint, jsonify, request
from app import db
import chatbot

from app.models.user import User
from app.models.user import ChatLog, MemoryTestResult

chatbot_routes = Blueprint("chatbot", __name__)

@chatbot_routes.route("chatbot_chat", methods=["POST"])
def chatbot_chat():
    """챗봇 대화 함수

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디 
        msg `str`:
            사용자가 보낸 채팅 내용
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
    """
    # Error: 데이터 형식이 JSON이 아님
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request", 
            "err_code": 10
        }), 400
    
    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["user_id", "msg"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter", 
                "err_code": 11
            }), 400
        
    # 파라미터 받아오기
    user_id = request.json["user_id"]
    user_msg = request.json["msg"]

    user = User.query.filter_by(user_id=user_id).first()

    # Error: 사용자가 존재하지 않음
    if not user:
        return jsonify({
            "result": "error", 
            "msg": "user does not exist", 
            "err_code": 20
        }), 401

    bot_msg = chatbot.chatbot_chat(user.id, user_msg)

    try:
        new_chat_log_user = ChatLog(user_id=user.id, receiver="user", chat_group_id=user.chat_group_id, text=user_msg)
        db.session.add(new_chat_log_user)
        new_chat_log_chatbot = ChatLog(user_id=user.id, receiver="assistant", chat_group_id=user.chat_group_id, text=bot_msg)
        db.session.add(new_chat_log_chatbot)
        return jsonify({
            "result": "success", 
            "msg": bot_msg,
            "err_code": 0
        }), 200
    # Error: SQL Commit 에러
    except Exception as e:
        print(f"Error during commit: {e}")
        db.session.rollback()
        return jsonify({
            "result": "error", 
            "msg": "Error during commit",
            "err_code": 100
        }), 500
    
chatbot_routes.route("/chatbot_quiz", methods=["POST"])
def chatbot_quiz():
    """챗봇 기억력 테스트 함수

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디 
        msg `str`:
            사용자가 보낸 채팅 내용
        history `list`:
            사용자와의 기억력 테스트 대화 기록
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        history `list`:
            
    """
    # Error: 데이터 형식이 JSON이 아님
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request", 
            "err_code": 10
        }), 400
    
    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["user_id"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter", 
                "err_code": 11
            }), 400
        
    # 파라미터 받아오기
    user_id = request.json["user_id"]
    user_msg = request.json["msg"] if request.json["msg"] != None else ""
    history = request.json["history"] if request.json["history"] != None else []

    user = User.query.filter_by(user_id=user_id).first()

    # Error: 사용자가 존재하지 않음
    if not user:
        return jsonify({
            "result": "error", 
            "msg": "user does not exist", 
            "err_code": 20
        }), 401
    
    bot_msg, history = chatbot.chatbot_chat(user.id, user_msg, history)

    # 문제가 모두 종료되고 챗봇이 결과를 말해줄 때
    try:
        if (history[-2]["content"] == "result"):
            mem_res = history[-1]["content"].split("/")
            memory_test_result = MemoryTestResult(user_id=user.id, correct=int(mem_res[0]), total=int(mem_res[1]))
            db.session.add(memory_test_result)
            return jsonify({
                "result": "end", 
                "msg": bot_msg,
                "err_code": 0,
                "history": history
            }), 200
        else:
            return jsonify({
                "result": "success", 
                "msg": bot_msg,
                "err_code": 0,
                "history": history
            }), 200
    # Error: SQL Commit 에러
    except Exception as e:
        print(f"Error during commit: {e}")
        db.session.rollback()
        return jsonify({
            "result": "error", 
            "msg": "Error during commit",
            "err_code": 100
        }), 500