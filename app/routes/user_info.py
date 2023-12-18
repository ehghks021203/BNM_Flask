from flask import Blueprint, jsonify, request
from app import db

from app.models.user import User, MainNok
from app.models.user import UserFavoriteFood, UserFavoriteMusic, UserFavoriteSeason, UserPastJob, UserPet
from app.models.user import ChatLog, MemoryTestResult

user_info_routes = Blueprint("user_info", __name__)

@user_info_routes.route("/check_user_first", methods=["POST"])
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
        is_first `int`:
            최초 실행 여부 (최초라면 1, 아니면 0)
    """
    # Error: 데이터 형식이 JSON이 아님
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request", 
            "err_code": 10
        }), 400
    
    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["user_id", "type"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter", 
                "err_code": 11
            }), 400
        
    # 파라미터 받아오기
    user_id = request.json["user_id"]
    type = request.json["type"]

    if type == "get":
        user = User.filter_by(user_id=user_id).first()
        # Error: 사용자가 존재하지 않음
        if not user:
            return jsonify({
                "result": "error", 
                "msg": f"{user_id} id does not exist",
                "err_code": 20
            }), 401
        else:
            return jsonify({
                "result":"success", 
                "msg":"get user first", 
                "err_code": 0,
                "is_first": user.is_first
            }), 200
    elif type == "set":
        user = User.filter_by(user_id=user_id).first()
        # Error: 사용자가 존재하지 않음
        if not user:
            return jsonify({
                "result": "error", 
                "msg": f"{user_id} id does not exist",
                "err_code": 20
            }), 401
        try:
            setattr(user, "is_first", 0)
            db.session.commit()
            return jsonify({
                "result": "success", 
                "msg": "set user first", 
                "err_code": 0,
                "is_first": 0
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
    else:
        return jsonify({
            "result":"error", 
            "msg":"invaild type value",
            "err_code": 0
        }), 400

user_info_routes.route("/get_main_nok_info", methods=["POST"])
def get_main_nok_info():
    """사용자의 정보를 받아오는 함수

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        nok_id `str`:
            주 보호자 아이디 

    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        name `str`:
            주 보호자의 이름
        birthday `str`:
            주 보호자의 생년월일
        gender `str`:
            주 보호자의 성별
        address `str`:
            주 보호자의 실거주지
        tell `str`:
            주 보호자의 전화번호
        user_list `list`:
            주 보호자와 연결된 사용자 리스트
    """

@user_info_routes.route("/get_user_info", methods=["POST"])
def get_user_info():
    """사용자의 정보를 받아오는 함수

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디 

    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        name `str`:
            사용자의 이름
        birthday `str`:
            사용자의 생년월일
        gender `str`:
            사용자의 성별
        address `str`:
            사용자의 실거주지
        blood_type `str`:
            사용자의 혈액형 (A, B, O, AB)
        main_nok_name `str`:
            주 보호자의 이름
        main_nok_tell `str`:
            주 보호자의 전화번호
    """

@user_info_routes.route("/get_user_info_all", methods=["POST"])
def get_user_info_all():
    """사용자의 정보를 받아오는 함수

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디 

    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        name `str`:
            사용자의 이름
        birthday `str`:
            사용자의 생년월일
        gender `str`:
            사용자의 성별
        address `str`:
            사용자의 실거주지
        blood_type `str`:
            사용자의 혈액형 (A, B, O, AB)
        chronic_illness `str`:
            사용자의 지병
        hometown `str`:
            사용자의 고향
        favorite_food `list`:
            사용자가 좋아하는 음식 -> 추가하는 방식 (제거 없음)
        favorite_music `list`:
            사용자가 좋아하는 음악 -> 추가하는 방식 (제거 없음)
        favorite_season `list`:
            사용자가 좋아하는 계절 (SP, SU, AU, WI) -> 추가하는 방식 (제거 없음)
        pet `list`:
            사용자의 반려동물 -> 추가하는 방식 (제거 없음)
        past_job `list`:
            사용자의 과거 직업 -> 추가하는 방식 (제거 없음)
        details `str`:
            개별 메모 사항
    """

@user_info_routes.route("/get_user_chat_log", methods=["POST"])
def get_user_chat_log():
    """사용자 대화 로그 불러오기

    ** 현재 아이디만 안다면 데이터를 확인할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        log `list`:
            대화 로그 리스트
    """

@user_info_routes.route("/get_user_test_result", methods=["POST"])
def get_user_test_result():
    """챗봇 기억력 테스트 결과 반환 함수

    ** 현재 아이디만 안다면 데이터를 확인할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디 
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        prev `str`:
            이전에 진행한 기억력 테스트 결과 (n/n)
        recent `str`:
            가장 최근에 진행한 기억력 테스트 결과 (n/n)
    """