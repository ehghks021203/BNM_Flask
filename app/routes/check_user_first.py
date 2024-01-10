from flask import Blueprint, jsonify, request
from app import db

from app.models.user import User

check_user_first_routes = Blueprint("check_user_first", __name__)

@check_user_first_routes.route("/check_user_first", methods=["POST"])
def check_user_first():
    """사용자가 대화를 처음 시작하는지 확인하는 함수.
    만일 최초 대화라면 대화 시작 전 정보 수집을 위한 모달창을 띄우기 위해
    필요함
    
    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디
        type `str`:
            리퀘스트 타입 (최초 실행 여부 파악: get, 최초 실행 여부 수정: set)
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
        is_first `int`:
            최초 실행 여부 (최초라면 1, 아니면 0)
    """
    # Error: 데이터 형식이 JSON이 아님
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request", 
            "err_code": "10"
        }), 400
    
    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["user_id", "type"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter", 
                "err_code": "11"
            }), 400
        
    # 파라미터 받아오기
    user_id = request.json["user_id"]
    type = request.json["type"]

    if type == "get":
        user = User.query.filter_by(user_id=user_id).first()
        # Error: 사용자가 존재하지 않음
        if not user:
            return jsonify({
                "result": "error", 
                "msg": f"{user_id} id does not exist",
                "err_code": "20"
            }), 401
        else:
            return jsonify({
                "result":"success", 
                "msg":"get user first", 
                "err_code": "00",
                "is_first": 1 if user.is_first else 0 
            }), 200
    elif type == "set":
        user = User.query.filter_by(user_id=user_id).first()
        # Error: 사용자가 존재하지 않음
        if not user:
            return jsonify({
                "result": "error", 
                "msg": f"{user_id} id does not exist",
                "err_code": "20"
            }), 401
        try:
            setattr(user, "is_first", 0)
            db.session.commit()
            return jsonify({
                "result": "success", 
                "msg": "set user first", 
                "err_code": "00",
                "is_first": 0
            }), 200
        # Error: SQL Commit 에러
        except Exception as e:
            print(f"Error during commit: {e}")
            db.session.rollback()
            return jsonify({
                "result": "error", 
                "msg": "Error during commit",
                "err_code": "100"
            }), 500
    else:
        return jsonify({
            "result":"error", 
            "msg":"invaild type value",
            "err_code": "00"
        }), 400
    
@check_user_first_routes.route("/check_user_exercise_first", methods=["POST"])
def check_user_exercise_first():
    """사용자가 운동을 처음 시작하는지 확인하는 함수.
    만일 최초 운동이라면 운동 시작 전 레벨테스트를 위한 모달창을 띄우기 위해
    필요함
    
    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디
        type `str`:
            리퀘스트 타입 (최초 실행 여부 파악: get, 최초 실행 여부 수정: set)
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
        is_exercise_first `int`:
            최초 실행 여부 (최초라면 1, 아니면 0)
    """
    # Error: 데이터 형식이 JSON이 아님
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request", 
            "err_code": "10"
        }), 400
    
    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["user_id", "type"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter", 
                "err_code": "11"
            }), 400
        
    # 파라미터 받아오기
    user_id = request.json["user_id"]
    type = request.json["type"]

    if type == "get":
        user = User.query.filter_by(user_id=user_id).first()
        # Error: 사용자가 존재하지 않음
        if not user:
            return jsonify({
                "result": "error", 
                "msg": f"{user_id} id does not exist",
                "err_code": "20"
            }), 401
        else:
            print({
                "result":"success", 
                "msg":"get user first", 
                "err_code": "00",
                "is_exercise_first": 1 if user.is_exercise_first else 0
            })
            return jsonify({
                "result":"success", 
                "msg":"get user first", 
                "err_code": "00",
                "is_exercise_first": 1 if user.is_exercise_first else 0
            }), 200
    elif type == "set":
        user = User.query.filter_by(user_id=user_id).first()
        # Error: 사용자가 존재하지 않음
        if not user:
            return jsonify({
                "result": "error", 
                "msg": f"{user_id} id does not exist",
                "err_code": "20"
            }), 401
        try:
            setattr(user, "is_exercise_first", 0)
            db.session.commit()
            return jsonify({
                "result": "success", 
                "msg": "set user first", 
                "err_code": "00",
                "is_exercise_first": 0
            }), 200
        # Error: SQL Commit 에러
        except Exception as e:
            print(f"Error during commit: {e}")
            db.session.rollback()
            return jsonify({
                "result": "error", 
                "msg": "Error during commit",
                "err_code": "100"
            }), 500
    else:
        return jsonify({
            "result":"error", 
            "msg":"invaild type value",
            "err_code": "00"
        }), 400
