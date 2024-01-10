from flask import Blueprint, jsonify, request, make_response
from app import db
import json
from datetime import datetime

from app.models.user import User
from app.models.user import ChatLog, MemoryTestResult

user_log_routes = Blueprint("user_log", __name__)

@user_log_routes.route("/get_user_chat_log", methods=["POST"])
def get_user_chat_log():
    """사용자 대화 로그 불러오기

    ** 현재 아이디만 안다면 데이터를 확인할 수 있는 상태로, 수정이 필요
    ** 날짜 로직 개떡같이 짜놨음 ㅋㅎ

    Params:
        user_id `str`:
            사용자 아이디
        date `str`:
            기준날짜 (옵션, YYYY-MM-DD)
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
        log `list`:
            대화 로그 리스트
        date `list`:
            대화 날짜 (YYYY-MM-DD)
    """
    # Error: 데이터 형식이 JSON이 아님
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request", 
            "err_code": "10"
        }), 400
    
    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["user_id"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter", 
                "err_code": "11"
            }), 400
        
    # 날짜 데이터가 없는지 확인
    if "date" in request.json and request.json["date"]:
        date = request.json["date"]
    else:
        date = None
        
    user_id = request.json["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    # Error: 유저가 존재하지 않음
    if not user:
        return jsonify({
            "result": "error", 
            "msg": "user does not exist", 
            "err_code": "20"
        }), 401
    
    if not date:
        chat_logs = ChatLog.query.filter_by(user_id=user.id).all()
    else:
        formatted_date = datetime.strptime(date, '%Y-%m-%d').date()
        chat_logs = ChatLog.query.filter_by(user_id=user.id).filter(db.func.date(ChatLog.time) == formatted_date).all()
    log_list = []
    date_list = []
    for log in chat_logs:
        # BLOB 데이터 디코딩
        log_text = log.text.decode('utf-8') if log.text else ""
        log_list.append({log.receiver:log_text})
        date_list.append(log.time.strftime("%Y-%m-%d"))

    response_data = {
        "result": "success", 
        "msg": "get chat log", 
        "err_code": "00",
        "log": log_list,
        "date": date_list
    }
    # 직접 JSON으로 변환하여 유니코드 처리 변경
    response_json = json.dumps(response_data, ensure_ascii=False).encode('utf8')

    # make_response를 사용하여 Response 객체 생성
    response = make_response(response_json)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'

    return response


@user_log_routes.route("/get_user_test_result", methods=["POST"])
def get_user_test_result():
    """챗봇 기억력 테스트 결과 반환 함수

    ** 현재 아이디만 안다면 데이터를 확인할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디 
        date `str`:
            기준날짜 (옵션, YYYY-MM-DD)
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
        correct `list`:
            맞은 개수
        total `list`:
            전체 개수
        date `list`:
            퀴즈 날짜 (YYYY-MM-DD)
    """
    # Error: 데이터 형식이 JSON이 아님
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request", 
            "err_code": "10"
        }), 400
    
    print(request.json)
    
    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["user_id"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter", 
                "err_code": "11"
            }), 400
    
    # 날짜 데이터가 없는지 확인
    if "date" in request.json and request.json["date"]:
        date = request.json["date"]
    else:
        date = None
    
    user_id = request.json["user_id"]
    user = User.query.filter_by(user_id=user_id).first()
    # Error: 유저가 존재하지 않음
    if not user:
        return jsonify({
            "result": "error", 
            "msg": "user does not exist", 
            "err_code": "20"
        }), 401
    
    if not date:
        mem_test_results = MemoryTestResult.query.filter_by(user_id=user.id).all()
    else:
        formatted_date = datetime.strptime(date, '%Y-%m-%d').date()
        mem_test_results = MemoryTestResult.query.filter_by(user_id=user.id).filter(db.func.date(MemoryTestResult.date) == formatted_date).all()
        
    mem_test_correct_list = []
    mem_test_total_list = []
    date_list = []
    for result in mem_test_results:
        mem_test_correct_list.append(result.correct)
        mem_test_total_list.append(result.total)
        date_list.append(result.date.strftime("%Y-%m-%d"))

    response_data = {
        "result": "success", 
        "msg": "get chat log", 
        "err_code": "00",
        "correct": mem_test_correct_list,
        "total": mem_test_total_list,
        "date": date_list
    }
    # 직접 JSON으로 변환하여 유니코드 처리 변경
    response_json = json.dumps(response_data, ensure_ascii=False).encode('utf8')

    # make_response를 사용하여 Response 객체 생성
    response = make_response(response_json)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'

    print(response_json)

    return response
    

