import openai
from config import Key, Chatbot

def chatbot_chat(uid: int, msg: str):
    """챗봇 대화 함수

    Params:
        uid `int`:
            사용자의 아이디
        msg `str`:
            사용자가 보낸 채팅 내용
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
    """
    messages = []
    messages.append({"role":"system", "content":Chatbot.CHAT_PROMPT})
    messages.append({"role":"user", "content":Chatbot.request_propmt(uid=uid)})
    messages.extend(Chatbot.load_chat_log(uid=uid))     # 채팅 로그 불러오기
    messages.append({"role":"user", "content":msg})     # 사용자 메시지 추가하기
    chatbot = openai.ChatCompletion.create(
        model = Chatbot.MODEL,
        messages = messages
    )
    bot_msg = chatbot["choices"][0]["message"]["content"]
    return bot_msg

def chatbot_quiz(uid: int, msg: str, history: list = []):
    """챗봇 대화 함수

    Params:
        uid `int`:
            사용자의 아이디
        msg `str`:
            사용자가 보낸 채팅 내용
    
    Returns:
        result `str`:
            응답 성공 여부 (success, error)
        msg `str`:
            응답 메시지
    """
    messages = []
    messages.append({"role":"system", "content":Chatbot.QUIZ_PROMPT})
    messages.append({"role":"user", "content":Chatbot.request_propmt(uid=uid)})
    messages.append({"role":"user", "content":Chatbot.load_quiz_log(uid=uid)})
    messages.extend(history)

    chatbot = openai.ChatCompletion.create(
        model = Chatbot.MODEL,
        messages = messages
    )
    bot_msg = chatbot["choices"][0]["message"]["content"]
    history.append({"role":"assistant", "content":bot_msg})
    if "기억력 퀴즈는 여기까지 하도록 하겠습니다" in bot_msg:
        bot_str, history = chatbot_quiz(1, "result", history)
    
    return bot_msg, history