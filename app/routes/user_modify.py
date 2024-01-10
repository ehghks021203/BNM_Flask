from flask import Blueprint, jsonify, request
from app import db, bcrypt

from app.models.user import User, MainNok
from app.models.user import UserFavoriteFood, UserFavoriteMusic, UserFavoriteSeason, UserPastJob, UserPet
from app.models.user import ChatLog, MemoryTestResult
from app.models.user import LevelTest

from config import Season

user_modify_routes = Blueprint("user_modify", __name__)

@user_modify_routes.route("/user_delete", methods=["POST"])
def user_delete():
    """사용자 회원 탈퇴 (일반 사용자, 주 보호자 공용)

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    user_id와 nok_id 중 하나는 필수로 있어야 함

    Params:
        user_id `str`:
            사용자 아이디 (옵션)
        nok_id `str`:
            주 보호자 아이디 (옵션)

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
    
    # 사용자 데이터 받아오기
    if "nok_id" in request.json:
        nok_id = request.json["nok_id"]
        user_id = None
    elif "user_id" in request.json:
        user_id = request.json["user_id"]
        nok_id = None
    else:
        # 파라미터 값이 비어있거나 없을 때
        return jsonify({
            "result": "error", 
            "msg": "missing nok_id or user_id parameter",
            "err_code": "11"
        }), 400
    
    # 주 보호자에 대한 회원 탈퇴일 경우
    if nok_id:
        main_nok = MainNok.query.filter_by(nok_id=nok_id).first()
        # Error: 주 보호자가 존재하지 않음
        if not main_nok:
            return jsonify({
                "result": "error", 
                "msg": f"{nok_id} id does not exist",
                "err_code": "20"
            }), 401
        nid = main_nok.id
        # 주 보호자와 연결된 사용자 리스트 생성
        user_list = User.query.filter_by(main_nok_id=nid).all()
    # 일반 사용자에 대한 회원 탈퇴일 경우
    elif user_id:
        user = User.query.filter_by(user_id=user_id).first()
        # Error: 사용자가 존재하지 않음
        if not user:
            return jsonify({
                "result": "error", 
                "msg": f"{user_id} id does not exist",
                "err_code": "20"
            }), 401
        user_list = [user]

    # 주어진 조건에 맞는 유저 제거 (주 보호자 탈퇴 시 주 보호자와 연결되어있는 사용자 모두 제거)
    try:
        for user in user_list:
            # 사용자가 좋아하는 음식 테이블의 유저 데이터 모두 삭제
            user_favorite_foods = UserFavoriteFood.query.filter_by(user_id=user.id).all()
            for user_favorite_food in user_favorite_foods:
                db.session.delete(user_favorite_food)
            # 사용자가 좋아하는 음악 테이블의 유저 데이터 모두 삭제
            user_favorite_musics = UserFavoriteMusic.query.filter_by(user_id=user.id).all()
            for user_favorite_music in user_favorite_musics:
                db.session.delete(user_favorite_music)
            # 사용자가 좋아하는 계절 테이블의 유저 데이터 모두 삭제
            user_favorite_seasons = UserFavoriteSeason.query.filter_by(user_id=user.id).all()
            for user_favorite_season in user_favorite_seasons:
                db.session.delete(user_favorite_season)
            # 사용자의 과거 직업 테이블의 유저 데이터 모두 삭제
            user_past_jobs = UserPastJob.query.filter_by(user_id=user.id).all()
            for user_past_job in user_past_jobs:
                db.session.delete(user_past_job)
            # 사용자의 애완동물 테이블의 유저 데이터 모두 삭제
            user_pets = UserPet.query.filter_by(user_id=user.id).all()
            for user_pet in user_pets:
                db.session.delete(user_pet)
            # 사용자의 챗봇 대화 로그 테이블의 유저 데이터 모두 삭제
            chat_logs = ChatLog.query.filter_by(user_id=user.id).all()
            for chat_log in chat_logs:
                db.session.delete(chat_log)
            # 사용자의 기억력 테스트 테이블의 유저 데이터 모두 삭제
            memory_test_results = MemoryTestResult.query.filter_by(user_id=user.id).all()
            for memory_test_result in memory_test_results:
                db.session.delete(memory_test_result)
            # 사용자의 레벨테스트 테이블의 유저 데이터 모두 삭제
            level_tests = LevelTest.query.filter_by(user_id=user.id).all()
            for level_test in level_tests:
                db.session.delete(level_test)
            
            db.session.delete(user)
            db.session.commit()
        # 주 보호자에 대한 회원 탈퇴인 경우 주 보호자 데이터 제거
        if nok_id:
            db.session.delete(main_nok)
            db.session.commit()
        return jsonify({
            "result": "success", 
            "msg": "user deleted",
            "err_code": "00"
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

@user_modify_routes.route("/modify_nok_info", methods=["POST"])
def modify_nok_info():
    """사용자의 정보를 수정하는 함수
    해당 함수의 파라미터는 모두 필수가 아님.

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        nok_id `str`:
            주 보호자 아이디 
        nok_pw `str`:
            주 보호자 비번
        name `str`:
            주 보호자의 이름 (수정 할 필요 없어보임)
        birthday `str`:
            주 보호자의 생년월일 (수정 할 필요 없어보임)
        gender `str`:
            주 보호자의 성별 (수정 할 필요 없어보임)
        address `str`:
            주 보호자의 실거주지
        tell `str`:
            주 보호자의 전화번호

    Returns:
        Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
        modify_value `list`:
            수정된 데이터 범주
    """
    # 데이터 형식이 JSON이 아닐 때
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request",
            "err_code": "10"
        }), 400
    
    print(request.json)
    
    # 주 보호자 데이터 받아오기
    nok_id = request.json["nok_id"]
    
    # 파라미터 값이 비어있거나 없을 때
    if not nok_id:
        return jsonify({
            "result": "error", 
            "msg": "missing nok_id parameter",
            "err_code": "11"
        }), 400
    
    

    # 주 보호자에 대한 정보 조회
    main_nok = MainNok.query.filter_by(nok_id=nok_id).first()
    if not main_nok:
        return jsonify({
            "result": "error", 
            "msg": f"{nok_id} id does not exist",
            "err_code": "20"
        }), 401

    # 주어진 데이터로 주 보호자 정보 수정
    modify_data = []
    value = request.json.get("nok_pw")
    if value is not None:
        hashed_pw = bcrypt.generate_password_hash(value).decode('utf-8')
        setattr(main_nok, "nok_pw", hashed_pw)
        modify_data.append("nok_pw")
    
    for key in ["name", "birthday", "address", "tell"]:
        value = request.json.get(key)
        # 만약 해당 키의 값이 None이면 패스
        if value is not None:
            setattr(main_nok, key, value)
            modify_data.append(key)
    
    value = request.json.get("gender")
    if value is not None:
        setattr(main_nok, "gender", "M" if value == "남자" else "F" if value == "여자" else "P")
        modify_data.append("gender")
    
     # 변경사항을 확정하고 저장
    try:
        db.session.commit()
        return jsonify({
            "result": "success", 
            "msg": "nok data modified", 
            "err_code": "00",
            "modify_value": modify_data
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

@user_modify_routes.route("/modify_user_info", methods=["POST"])
def modify_user_info():
    """사용자의 정보를 수정하는 함수
    좋아하는 음식, 좋아하는 음악, 반려동물 등의 정보 추가 또한 해당 함수에서 진행함.
    해당 함수의 파라미터는 모두 필수가 아님.

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디 
        user_pw `str`:
            사용자 패스워드
        name `str`:
            사용자의 이름 (수정 할 필요 없어보임)
        birthday `str`:
            사용자의 생년월일 (수정 할 필요 없어보임)
        gender `str`:
            사용자의 성별 (수정 할 필요 없어보임)
        address `str`:
            사용자의 실거주지
        blood_type `str`:
            사용자의 혈액형 (A, B, O, AB) -> 다른 혈액형도 넣어야하나? (Rh- 같은거) -> 10
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

    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
        modify_value `list`:
            수정된 데이터 범주
    """
    # 데이터 형식이 JSON이 아닐 때
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request",
            "err_code": "10"
        }), 400
    
    # 주 보호자 데이터 받아오기
    user_id = request.json["user_id"]

    # 파라미터 값이 비어있거나 없을 때
    if not user_id:
        return jsonify({
            "result": "error", 
            "msg": "missing user_id parameter",
            "err_code": "11"
        }), 400
    
    # 사용자에 대한 정보 조회
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        main_nok = MainNok.query.filter_by(nok_id=user_id).first()
        if not main_nok:
            return jsonify({
                "result": "error", 
                "msg": f"{user_id} id does not exist",
                "err_code": "20"
            }), 401
    
    if user:
        # 주어진 데이터로 사용자 정보 수정
        modify_data = []
        value = request.json.get("user_pw")
        if value is not None:
            hashed_pw = bcrypt.generate_password_hash(value).decode('utf-8')
            setattr(user, "user_pw", hashed_pw)
            modify_data.append("user_pw")

        for key in ["name", "birthday", "address", "relation", "blood_type", "hometown"]:
            value = request.json.get(key)
            # 만약 해당 키의 값이 None이면 패스
            if value is not None and value != "":
                setattr(user, key, value)
                modify_data.append(key)
        
        value = request.json.get("gender")
        if value is not None:
            setattr(user, "gender", "M" if value == "남자" else "F" if value == "여자" else "P")
            modify_data.append("gender")

        value = request.json.get("chronic_illness")
        if value is not None:
            setattr(user, "chronic_illness", value.encode('utf-8'))
            modify_data.append("chronic_illness")
        
        value = request.json.get("favorite_food")
        if value is not None:
            user_favorite_foods = UserFavoriteFood.query.filter_by(user_id=user.id).all()
            for user_favorite_food in user_favorite_foods:
                db.session.delete(user_favorite_food)
            for v in value:
                user_favorite_food = UserFavoriteFood(user_id=user.id, favorite_food=v)
                db.session.add(user_favorite_food)
            modify_data.append("favorite_food")
        
        value = request.json.get("favorite_music")
        if value is not None:
            user_favorite_musics = UserFavoriteMusic.query.filter_by(user_id=user.id).all()
            for user_favorite_music in user_favorite_musics:
                db.session.delete(user_favorite_music)
            for v in value:
                user_favorite_music = UserFavoriteMusic(user_id=user.id, favorite_music=v)
                db.session.add(user_favorite_music)
            modify_data.append("favorite_music")

        value = request.json.get("favorite_season")
        if value is not None:
            user_favorite_seasons = UserFavoriteSeason.query.filter_by(user_id=user.id).all()
            for user_favorite_season in user_favorite_seasons:
                db.session.delete(user_favorite_season)
            for v in value:
                user_favorite_season = UserFavoriteSeason(user_id=user.id, favorite_season=Season.season_data[v])
                db.session.add(user_favorite_season)
            modify_data.append("favorite_season")
        
        value = request.json.get("past_job")
        if value is not None:
            user_past_jobs = UserPastJob.query.filter_by(user_id=user.id).all()
            for user_past_job in user_past_jobs:
                db.session.delete(user_past_job)
            for v in value:
                user_past_job = UserPastJob(user_id=user.id, past_job=v)
                db.session.add(user_past_job)
            modify_data.append("past_job")

        value = request.json.get("pet")
        if value is not None:
            user_pets = UserPet.query.filter_by(user_id=user.id).all()
            for user_pet in user_pets:
                db.session.delete(user_pet)
            for v in value:
                user_pet = UserPet(user_id=user.id, pet=v)
                db.session.add(user_pet)
            modify_data.append("pet")

        value = request.json.get("details")
        if value is not None:
            setattr(user, "details", value)
            modify_data.append("details")
        
        db.session.commit()

        print(
                {
                "result": "success", 
                "msg": "user data modified", 
                "err_code": "00",
                "modify_value": modify_data
            }
        )
        return jsonify({
            "result": "success", 
            "msg": "user data modified", 
            "err_code": "00",
            "modify_value": modify_data
        }), 200
    elif main_nok:
        # 주어진 데이터로 주 보호자 정보 수정
        modify_data = []
        value = request.json.get("nok_pw")
        if value is not None:
            hashed_pw = bcrypt.generate_password_hash(value).decode('utf-8')
            setattr(main_nok, "nok_pw", hashed_pw)
            modify_data.append("nok_pw")
        
        for key in ["name", "birthday", "address", "tell"]:
            value = request.json.get(key)
            # 만약 해당 키의 값이 None이면 패스
            if value is not None:
                setattr(main_nok, key, value)
                modify_data.append(key)
        
        value = request.json.get("gender")
        if value is not None:
            setattr(main_nok, "gender", "M" if value == "남자" else "F" if value == "여자" else "P")
            modify_data.append("gender")
        
        # 변경사항을 확정하고 저장
        try:
            db.session.commit()
            return jsonify({
                "result": "success", 
                "msg": "nok data modified", 
                "err_code": "00",
                "modify_value": modify_data
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
