from flask import Blueprint, jsonify, request
from app import db, bcrypt
from datetime import datetime

from app.models.user import User, MainNok

auth_routes = Blueprint("auth", __name__)

@auth_routes.route("/login", methods=["POST"])
def login():
    """사용자 로그인
    
    Params:
        user_id `str`:
            유저의 이메일 주소.
        user_pw `str`:
            유저의 비밀번호.
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
        user_type `str`:
            로그인 한 유저의 타입 (user 또는 main_nok)
    """
    # Error: 데이터 형식이 JSON이 아님
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request", 
            "err_code": "10"
        }), 400
    
    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["user_id", "user_pw"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter", 
                "err_code": "11"
            }), 400
        
    # 사용자 데이터 받아오기
    # 주 보호자 데이터 받아오기    
    user_id = request.json["user_id"]
    user_pw = request.json["user_pw"]

    user = User.query.filter_by(user_id=user_id).first()

    if user:
        if bcrypt.check_password_hash(user.user_pw, user_pw):
            return jsonify({
                "result": "success", 
                "msg": "correct password", 
                "err_code": "00", 
                "user_type": "user"
            }), 200
        # Error: 비밀번호 불일치
        else:
            return jsonify({
                "result": "error", 
                "msg": "incorrect password", 
                "err_code": "22", 
                "user_type": "user"
            }), 401
    else:
        main_nok = MainNok.query.filter_by(nok_id=user_id).first()
        if main_nok:
            if bcrypt.check_password_hash(main_nok.nok_pw, user_pw):
                return jsonify({
                    "result": "success", 
                    "msg": "correct password", 
                    "err_code": "00", 
                    "user_type": "main_nok"
                }), 200
            # Error: 비밀번호 불일치
            else:
                return jsonify({
                    "result": "error",
                    "msg": "incorrect password", 
                    "err_code": "22", 
                    "user_type": "main_nok"
                }), 401
    # Error: 사용자가 존재하지 않음
    return jsonify({
        "result": "error", 
        "msg": "user does not exist", 
        "err_code": "20"
    }), 401

@auth_routes.route("/nok_register", methods=["POST"])
def nok_register():
    """주 보호자 회원가입

    Params:
        nok_id `str`:
            주 보호자의 아이디 (중복 불가)
        nok_pw `str`:
            주 보호자의 비밀번호
        name `str`:
            주 보호자의 실명
        birthday `str`: 
            주 보호자의 생년월일 (YYYY-MM-DD 형식)
        gender `str`:
            주 보호자의 성별 (남자: M, 여자: F, 비공개: P)
        address `str`:
            주 보호자의 실거주지
        tell `str`:
            주 보호자의 전화번호 (구분자 제외)

    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
    """
    # Error: 데이터 형식이 JSON이 아님
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request", 
            "err_code": "10"
        }), 400
    
    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["nok_id", "nok_pw", "name", "birthday", "gender", "address", "tell"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter", 
                "err_code": "11"
            }), 400

    # 주 보호자 데이터 받아오기    
    nok_id = request.json["nok_id"]
    nok_pw = request.json["nok_pw"]
    nok_name = request.json["name"]
    nok_birthday = request.json["birthday"]
    nok_gender = request.json["gender"]
    nok_address = request.json["address"]
    nok_tell = request.json["tell"]

    # Error: 이미 존재하는 아이디
    if MainNok.query.filter_by(nok_id=nok_id).count() > 0:
        return jsonify({
            "result": "error", 
            "msg": f"{nok_id} id already exists",
            "err_code": "21"
        }), 401

    # 비밀번호 암호화
    hashed_pw = bcrypt.generate_password_hash(nok_pw).decode('utf-8')

    # 회원정보 main_nok 테이블에 삽입
    try:
        new_main_nok = MainNok(nok_id=nok_id, nok_pw=hashed_pw, name=nok_name, birthday=nok_birthday,
                        gender=nok_gender, address=nok_address, tell=nok_tell)
        db.session.add(new_main_nok)
        db.session.commit()
        return jsonify({
            "result":"success", 
            "msg":"main nok register",
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

@auth_routes.route("/user_register", methods=["POST"])
def user_register():
    """사용자 회원가입

    Params:
        nok_id `str`:
            주 보호자의 아이디
        user_id `str`:
            사용자의 아이디 (중복 불가)
        user_pw `str`:
            사용자의 비밀번호
        name `str`:
            사용자의 실명
        birthday `str`: 
            사용자의 생년월일 (YYYY-MM-DD 형식)
        gender `str`:
            사용자의 성별 (남자: M, 여자: F, 비공개: P)
        relation `str`:
            주 보호자와의 관계
        address `str`:
            사용자의 실거주지
        blood_type `str`:
            사용자의 혈액형 (A, B, O, AB) -> 다른 혈액형도 넣어야하나? (Rh- 같은거) -> 10
        chronic_illness `str`:
            사용자의 지병

    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
    """
    # Error: 데이터 형식이 JSON이 아님
    if not request.is_json:
        return jsonify({
            "result": "error", 
            "msg": "missing json in request",
            "err_code": "10"
        }), 400
    
    # Error: 파라미터 값이 비어있거나 없음
    required_fields = ["nok_id", "user_id", "user_pw", "name", "birthday", "gender", 
                       "relation", "address", "blood_type", "chronic_illness"]
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            print(f"missing {field} parameter")
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter",
                "err_code": "11"
            }), 400
        
    # 사용자 데이터 받아오기
    nok_id = request.json["nok_id"]
    user_id = request.json["user_id"]
    user_pw = request.json["user_pw"]
    user_name = request.json["name"]
    user_birthday = request.json["birthday"]
    user_birthday = datetime.strptime(user_birthday, "%Y-%m-%d").date()
    user_gender = request.json["gender"]
    user_relation = request.json["relation"]
    user_address = request.json["address"]
    user_blood_type = request.json["blood_type"]
    user_chronic_illness = request.json["chronic_illness"].encode('utf-8') if request.json["chronic_illness"] else None

    main_nok = MainNok.query.filter_by(nok_id=nok_id).first()

    # Error: 주 보호자 아이디가 존재하지 않음
    if not main_nok:
        return jsonify({
            "result": "error", 
            "msg": f"{nok_id} id does not exits",
            "err_code": "20"
        }), 401
    nid = main_nok.id
    print(nid)

    # Error: 이미 존재하는 아이디
    if User.query.filter_by(user_id=user_id).count() > 0:
        return jsonify({
            "result": "error", 
            "msg": f"{user_id} id already exists",
            "err_code": "21"
        }), 401

    # 비밀번호 암호화
    hashed_pw = bcrypt.generate_password_hash(user_pw).decode('utf-8')

    # 회원정보 main_nok 테이블에 삽입
    try:
        new_user = User(main_nok_id=nid, user_id=user_id, user_pw=hashed_pw, name=user_name, birthday=user_birthday,
                    gender=user_gender, relation=user_relation, address=user_address, blood_type=user_blood_type, 
                    chronic_illness=user_chronic_illness)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "result":"success", 
            "msg":"user register",
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

@auth_routes.route("/check_id_duplicate", methods=["POST"])
def check_id_duplicate():
    """사용자 아이디 중복 확인 함수

    Params:
        user_id `str`:
            사용자의 아이디 (중복 불가)

    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
        err_code `str`:
            오류 코드 (API_GUIDE.md 참고)
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
            print(f"missing {field} parameter")
            return jsonify({
                "result": "error", 
                "msg": f"missing {field} parameter",
                "err_code": "11"
            }), 400
        
    user_id = request.json["user_id"]
    print(user_id)
    # Error: 이미 존재하는 아이디
    if MainNok.query.filter_by(nok_id=user_id).count() > 0:
        return jsonify({
            "result": "error", 
            "msg": f"{user_id} id already exists",
            "err_code": "21"
        }), 401
    # Error: 이미 존재하는 아이디
    elif User.query.filter_by(user_id=user_id).count() > 0:
        return jsonify({
            "result": "error", 
            "msg": f"{user_id} id already exists",
            "err_code": "21"
        }), 401
    else:
        return jsonify({
            "result": "success", 
            "msg": f"{user_id} is available.",
            "err_code": "00"
        }), 200
