from flask import Blueprint, jsonify, request
from app import db

from app.models.user import User, MainNok
from app.models.user import UserFavoriteFood, UserFavoriteMusic, UserFavoriteSeason, UserPastJob, UserPet
from app.models.user import ChatLog, MemoryTestResult

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
    """
    # 데이터 형식이 JSON이 아닐 때
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request",
            "err_code":10
        }), 400
    
    # 사용자 데이터 받아오기
    nok_id = request.json["nok_id"]
    user_id = request.json["user_id"]

    # 파라미터 값이 비어있거나 없을 때
    if not nok_id and not user_id:
        return jsonify({
            "result": "error", 
            "msg": f"missing nok_id or user_id parameter",
            "err_code":11
        }), 400

    # 주 보호자에 대한 회원 탈퇴일 경우
    if nok_id:
        main_nok = MainNok.query.filter_by(nok_id=nok_id).first()
        if not main_nok:
            return jsonify({"result": "error", "msg": f"{nok_id} id does not exist"}), 401
        nid = main_nok.id
        # 주 보호자와 연결된 사용자 리스트 생성
        user_list = User.query.filter_by(main_nok_id=nid).all()
    # 일반 사용자에 대한 회원 탈퇴일 경우
    elif user_id:
        user = User.query._filter_by(user_id=user_id).first()
        if not user:
            return jsonify({"result": "error", "msg": f"{user_id} id does not exist"}), 401
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
            
            db.session.delete(user)
            db.session.commit()
        # 주 보호자에 대한 회원 탈퇴인 경우 주 보호자 데이터 제거
        if nok_id:
            db.session.delete(main_nok)
            db.session.commit()
        return jsonify({"result": "success", "msg": "user deleted"}), 200
    # SQL에 데이터 제거 중 예외 발생
    except Exception as e:
        print(f"Error during delete: {e}")
        db.session.rollback()
        return jsonify({"result": "error", "msg": "Error during delete"}), 500
    # DB 연결
    cur = mysql.connection.cursor()

    # 주 보호자에 대한 회원 탈퇴일떄
    if nok_id:
        # 주 보호자의 고유 id 받아오기
        sql = "SELECT id FROM main_nok WHERE nok_id='{}'".format(nok_id)
        cur.execute(sql)
        sql_res = cur.fetchone()
        if not sql_res:
            cur.close()
            return jsonify({"result":"error","msg":"main_nok does not exist"}), 401
        nid = sql_res["id"]
        
        # 주 보호자와 연결된 사용자 리스트 생성
        sql = "SELECT id FROM user WHERE main_nok_id=%s"
        cur.execute(sql, (nid,))
        user_list = cur.fetchall()
    
    # 일반 사용자에 대한 회원 탈퇴일때
    if not nok_id:
        user_id = request.json.get("user_id")
        if user_id:
            # DB 연결
            cur = mysql.connection.cursor()

            # 사용자의 고유 id 받아오기
            sql = "SELECT id FROM user WHERE user_id='{}'".format(user_id)
            cur.execute(sql)
            user_list = cur.fetchall()
            if len(user_list) == 0:
                cur.close()
                return jsonify({"result":"error","msg":"user does not exist"}), 401

    # 유저 제거 (주 보호자 탈퇴 시 주 보호자와 연결되어있는 사용자 모두 제거)
    for user in user_list:
        sql = "DELETE FROM chat_log WHERE user_id=%s"
        cur.execute(sql, (user["id"],))
        sql = "DELETE FROM memory_test_result WHERE user_id=%s"
        cur.execute(sql, (user["id"],))
        sql = "DELETE FROM user_favorite_food WHERE user_id=%s"
        cur.execute(sql, (user["id"],))
        sql = "DELETE FROM user_favorite_music WHERE user_id=%s"
        cur.execute(sql, (user["id"],))
        sql = "DELETE FROM user_favorite_season WHERE user_id=%s"
        cur.execute(sql, (user["id"],))
        sql = "DELETE FROM user_past_job WHERE user_id=%s"
        cur.execute(sql, (user["id"],))
        sql = "DELETE FROM user_pet WHERE user_id=%s"
        cur.execute(sql, (user["id"],))
        sql = "DELETE FROM user WHERE id=%s"
        cur.execute(sql, (user["id"],))
        mysql.connection.commit()
        

    # 주 보호자에 대한 회원 탈퇴일떄 주 보호자에 연결된 사용자를 모두 제거한 후
    if nok_id:
        # 주 보호자 데이터 제거
        sql = "DELETE FROM main_nok WHERE id=%s"
        cur.execute(sql, (nid,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"result":"success","msg":"main_nok and user deleted"}), 200
    else:
        cur.close()
        return jsonify({"result":"success","msg":"user deleted"}), 200

@user_modify_routes.route("/modify_nok_info", methods=["POST"])
def modify_nok_info():
    """사용자의 정보를 수정하는 함수
    해당 함수의 파라미터는 모두 필수가 아님.

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        nok_id `str`:
            주 보호자 아이디 
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
        modify_value `list`:
            수정된 데이터 범주
    """
    # 데이터 형식이 JSON이 아닐 때
    if not request.is_json:
        return jsonify({"result": "error", "msg": "missing json in request"}), 400
    
    # 주 보호자 데이터 받아오기
    nok_id = request.json["nok_id"]

    # 주 보호자에 대한 정보 조회
    main_nok = MainNok.query.filter_by(nok_id=nok_id).first()
    if not main_nok:
        return jsonify({"result": "error", "msg": f"{nok_id} id does not exist"}), 401

    # 주어진 데이터로 주 보호자 정보 수정
    modify_data = []
    for key in ["name", "birthday", "gender", "address", "tell"]:
        value = request.json.get(key)
        # 만약 해당 키의 값이 None이면 패스
        if value is not None:
            setattr(main_nok, key, value)
            modify_data.append(key)
    
     # 변경사항을 확정하고 저장
    try:
        db.session.commit()
        return jsonify({"result": "success", "msg": "nok data modified", "modify_value": modify_data}), 200
    except Exception as e:
        print(f"Error during commit: {e}")
        db.session.rollback()
        return jsonify({"result": "error", "msg": "Error during commit"}), 500

@user_modify_routes.route("/modify_user_info", methods=["POST"])
def modify_user_info():
    """사용자의 정보를 수정하는 함수
    좋아하는 음식, 좋아하는 음악, 반려동물 등의 정보 추가 또한 해당 함수에서 진행함.
    해당 함수의 파라미터는 모두 필수가 아님.

    ** 현재 아이디만 안다면 데이터를 수정할 수 있는 상태로, 수정이 필요

    Params:
        user_id `str`:
            사용자 아이디  
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
        modify_value `list`:
            수정된 데이터 범주
    """
    # 데이터 형식이 JSON이 아닐 때
    if not request.is_json:
        return jsonify({"result": "error", "msg": "missing json in request"}), 400
    
    # 주 보호자 데이터 받아오기
    user_id = request.json["user_id"]

    try:
        # 주 보호자에 대한 정보 조회
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({"result": "error", "msg": f"{user_id} id does not exist"}), 401

        # 주어진 데이터로 주 보호자 정보 수정
        modify_data = []
        for key in ["name", "birthday", "gender", "address", "relation", "blood_type", "chronic_illness", "hometown"]:
            value = request.json.get(key)
            # 만약 해당 키의 값이 None이면 패스
            if value is not None:
                setattr(user, key, value)
                modify_data.append(key)
        for key in ["user_favorite_food", "user_favorite_music", "user_favorite_season", "user_past_job", "user_pet"]:
            value = request.json.get(key)
            # 만약 해당 키의 값이 None이면 패스
            if value is not None:
                # 기존 정보 삭제
                getattr(user, key).delete()
                # 새로운 정보 추가
                for item in value:
                    new_item = globals()[key.capitalize()](
                        user_id=user.id,
                        **{key[:-1]: item} if key.endswith("s") else {key: item}
                    )
                    db.session.add(new_item)
                db.session.commit()
            modify_data.append(key)
        return jsonify({"result": "success", "msg": "user data modified", "modify_value": modify_data}), 200
    except Exception as e:
        print(f"Error during modification: {e}")
        db.session.rollback()
        return jsonify({"result": "error", "msg": "Error during modification"}), 500
    