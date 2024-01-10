from flask import Blueprint, jsonify, request
from app import db

from app.models.user import User
from app.models.user import LevelTest

exercise_routes = Blueprint("exercise", __name__)

@exercise_routes.route("/save_level_test", methods=["POST"])
def save_level_test():
    """사용자 레벨 테스트 저장

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디 (옵션)
        up_level `int`:
            상체 추천 레벨
        down_level `int`:
            하체 추천 레벨

    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
    """
    # 데이터 형식이 JSON이 아닐 때
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request",
            "err_code": "10"
        }), 400
    
    print(request.json)

    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["user_id", "up_level", "down_level"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter", 
                "err_code": "11"
            }), 400
    
    # 사용자 데이터 받아오기
    user_id = request.json["user_id"]
    up_level = request.json["up_level"]
    down_level = request.json["down_level"]
    
    user = User.query.filter_by(user_id=user_id).first()
    # Error: 유저가 존재하지 않음
    if not user:
        return jsonify({
            "result": "error", 
            "msg": "user does not exist", 
            "err_code": "20"
        }), 401
    
    try:
        level_test = LevelTest.query.filter_by(user_id=user.id).first()
        if not level_test:
            level_test = LevelTest(user_id=user.id, up_level=int(up_level), down_level=int(down_level))
            db.session.add(level_test)
            setattr(user, "is_exercise_first", 0)
            db.session.commit()
        else:
            setattr(level_test, "up_level", up_level)
            setattr(level_test, "down_level", down_level)
            db.session.commit()
        return jsonify({
                "result": "success", 
                "msg": "save user level test", 
                "err_code": "00",
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
    
@exercise_routes.route("/get_level_test", methods=["POST"])
def get_level_test():
    """사용자 레벨 테스트 불러오기

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디 (옵션)

    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
        up_level `int`:
            상체 추천 레벨
        down_level `int`:
            하체 추천 레벨
    """
    # 데이터 형식이 JSON이 아닐 때
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request",
            "err_code": "10"
        }), 400
    
    # 사용자 데이터 받아오기
    if "user_id" in request.json:
        user_id = request.json["user_id"]

    # 파라미터 값이 비어있거나 없을 때
    if not user_id:
        return jsonify({
            "result": "error", 
            "msg": "missing user_id parameter",
            "err_code": "11"
        }), 400
    
    user = User.query.filter_by(user_id=user_id).first()
    # Error: 유저가 존재하지 않음
    if not user:
        return jsonify({
            "result": "error", 
            "msg": "user does not exist", 
            "err_code": "20"
        }), 401
    
    level_test = LevelTest.query.filter_by(user_id=user.id).first()

    if not level_test:
        up_level = 0
        down_level = 0
    else:
        up_level = level_test.up_level
        down_level = level_test.down_level
    
    return jsonify({
        "result": "success", 
        "msg": "get user level test result", 
        "err_code": "00",
        "up_level": up_level,
        "down_level": down_level
    }), 200
    
@exercise_routes.route("/save_exercise_log", methods=["POST"])
def save_exercise_log():
    """운동 기록을 저장하는 함수

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디 (옵션)
        pose_name `str`:
            동작 이름
        level `int`:
            동작 레벨 (1, 2, 3Lv)
        count `int`:
            동작 횟수
        sec `int`:
            운동 시간 (단위: 초)

    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
    """