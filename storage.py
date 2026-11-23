"""
저장소 및 데이터 입출력 모듈 (storage.py)

이 모듈은 프로젝트 루트의 'state.json' 파일에 퀴즈 및 게임 상태를
안전하게 저장하고 불러오는 역할을 전담합니다.

[주요 책임 분리]
- Quiz 클래스 (quiz.py): 단일 퀴즈 데이터 표현 및 개별 출력/정답 검증
- storage 모듈 (storage.py): JSON 파일 입출력, 스키마 검증, 예외 처리 및 데이터 복구

초보자도 직관적으로 이해할 수 있도록 쉬운 한국어 주석을 달아두었습니다.
"""

from __future__ import annotations

import json
import os
from typing import Any

from default_data import get_default_state
from quiz import Quiz

# 상태를 저장할 기본 JSON 파일 경로
STATE_FILE_PATH: str = "state.json"


def validate_state_schema(data: Any) -> bool:
    """
    JSON에서 읽어온 데이터가 프로그램에서 요구하는 필수 규격(스키마)을 만족하는지 검사합니다.

    [필수 스키마]
    1. 최상위 데이터는 딕셔너리(dict)여야 합니다.
    2. 'quizzes' 키가 있고, 그 값은 리스트(list)여야 합니다.
    3. 'best_score' 키가 있고, 그 값은 정수(int)여야 합니다.
    4. 'history' 키가 있고, 그 값은 리스트(list)여야 합니다.
    5. 'quizzes' 안의 각 항목은 퀴즈 필수 속성(question, choices, answer)을 포함해야 합니다.

    :param data: 검사할 데이터
    :return: 규격을 만족하면 True, 아니면 False
    """
    if not isinstance(data, dict):
        return False

    # 필수 최상위 키 존재 여부 확인
    if "quizzes" not in data or "best_score" not in data or "history" not in data:
        return False

    # 자료형 검사
    if not isinstance(data["quizzes"], list):
        return False
    if not isinstance(data["best_score"], int):
        return False
    if not isinstance(data["history"], list):
        return False

    # quizzes 리스트 내부의 각 퀴즈 데이터 기본 구조 검사
    for item in data["quizzes"]:
        if not isinstance(item, dict):
            return False
        # 필수 키 체크
        if "question" not in item or "choices" not in item or "answer" not in item:
            return False
        if not isinstance(item["choices"], list) or len(item["choices"]) != 4:
            return False
        if item["answer"] not in (1, 2, 3, 4):
            return False

    return True


def save_state(state: dict[str, Any], filepath: str = STATE_FILE_PATH) -> bool:
    """
    게임 상태 딕셔너리를 JSON 파일로 저장합니다.

    초보자 팁:
    - ensure_ascii=False: 한글이 '\\uac00' 같은 유니코드 코드로 깨지지 않고 그대로 저장되게 합니다.
    - indent=2: 사람이 파일 메모장으로 열어봤을 때 읽기 편하도록 2칸 들여쓰기를 적용합니다.
    - encoding="utf-8": 전 세계 표준 문자 인코딩 방식으로 한글 깨짐을 방지합니다.

    :param state: 저장할 상태 딕셔너리 (quizzes, best_score, history 포함)
    :param filepath: 저장할 파일 경로 (기본값: "state.json")
    :return: 저장 성공 시 True, 실패 시 False
    """
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False, indent=2)
        return True
    except OSError as error:
        print(f"❌ [오류] 파일 저장 중 문제가 발생했습니다: {error}")
        return False


def load_state(filepath: str = STATE_FILE_PATH) -> dict[str, Any]:
    """
    state.json 파일에서 상태를 불러옵니다.

    [안전 장치 및 자동 복구]
    1. 파일이 없으면 -> 안내 메시지를 출력하고 기본 30개 퀴즈 데이터로 새 파일을 생성합니다.
    2. 파일 내용이 손상되었거나(JSON 문법 오류), 규격에 맞지 않으면 ->
       try/except로 오류를 잡고 안내 메시지를 출력한 뒤 기본 데이터로 안전하게 복구합니다.

    :param filepath: 불러올 파일 경로 (기본값: "state.json")
    :return: 정상 상태 딕셔너리 (복구된 기본 상태 포함)
    """
    # 1. 파일이 아예 없는 경우: 새로 생성
    if not os.path.exists(filepath):
        print(f"ℹ️ [안내] '{filepath}' 파일이 없어 기본 30개 퀴즈 데이터로 새로 생성합니다.")
        default_state = get_default_state()
        save_state(default_state, filepath)
        return default_state

    # 2. 파일이 존재하는 경우: 읽기 시도 및 손상 검사
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

        # 스키마 유효성 검사 (필수 키 및 형식 확인)
        if not validate_state_schema(data):
            raise ValueError("데이터 형식(스키마)이 올바르지 않거나 훼손되었습니다.")

        return data

    except (json.JSONDecodeError, UnicodeDecodeError, ValueError, OSError) as error:
        # 파일이 깨졌거나 읽기 오류가 발생한 경우 자동 복구 진행
        print(f"⚠️ [경고] '{filepath}' 파일이 손상되었거나 읽을 수 없습니다. (원인: {error})")
        print("🔄 [복구] 기본 30개 퀴즈 데이터로 안전하게 복구하여 새로 저장합니다.")

        restored_state = get_default_state()
        save_state(restored_state, filepath)
        return restored_state


def load_quizzes(filepath: str = STATE_FILE_PATH) -> list[Quiz]:
    """
    state.json 파일에서 퀴즈 목록을 읽어와 Quiz 객체의 리스트로 변환하여 반환합니다.
    (저장소와 Quiz 클래스가 깔끔하게 연결되는 지점입니다.)

    :param filepath: 불러올 파일 경로 (기본값: "state.json")
    :return: Quiz 객체들이 담긴 리스트 (list[Quiz])
    """
    state = load_state(filepath)
    raw_quizzes = state.get("quizzes", [])

    quizzes: list[Quiz] = []
    for raw in raw_quizzes:
        try:
            quizzes.append(Quiz.from_dict(raw))
        except (ValueError, TypeError) as err:
            print(f"⚠️ [경고] 특정 퀴즈 데이터를 Quiz 객체로 변환하지 못했습니다: {err}")

    # 만약 모든 퀴즈 변환에 실패하여 빈 목록이 되었다면 기본 상태로 복구
    if not quizzes:
        print("⚠️ [경고] 유효한 퀴즈가 없어 기본 퀴즈 데이터로 복구합니다.")
        default_state = get_default_state()
        save_state(default_state, filepath)
        quizzes = [Quiz.from_dict(q) for q in default_state["quizzes"]]

    return quizzes


def save_quizzes(quizzes: list[Quiz], filepath: str = STATE_FILE_PATH) -> bool:
    """
    Quiz 객체 리스트를 딕셔너리로 변환하여 기존 상태(best_score, history)와 함께 저장합니다.

    :param quizzes: 저장할 Quiz 객체 리스트
    :param filepath: 저장할 파일 경로
    :return: 저장 성공 여부
    """
    state = load_state(filepath)
    state["quizzes"] = [quiz.to_dict() for quiz in quizzes]
    return save_state(state, filepath)


def reset_to_default(filepath: str = STATE_FILE_PATH) -> dict[str, Any]:
    """
    state.json 파일을 언제든 기본 30개 퀴즈 상태로 강제 초기화(복구)합니다.

    :param filepath: 초기화할 파일 경로
    :return: 새로 생성된 기본 상태 딕셔너리
    """
    print(f"🔄 [초기화] '{filepath}' 파일을 기본 30개 퀴즈 데이터로 초기화합니다.")
    default_state = get_default_state()
    save_state(default_state, filepath)
    return default_state


# ========================================================
# [직접 실행 테스트 영역]
# 이 파일(storage.py)을 직접 실행하여 기능이 정상 동작하는지 테스트합니다.
# ========================================================
if __name__ == "__main__":
    import tempfile

    print("[storage 모듈 단독 동작 테스트 시작]\n")

    # 임시 디렉터리에서 안전하게 테스트 진행
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test_state.json")

        # 1. 파일 없음 초기화 테스트
        print("1. [파일 없음 초기화 테스트]")
        state = load_state(test_file)
        print(f"-> 로드된 퀴즈 개수: {len(state['quizzes'])}개")
        print(f"-> 파일 존재 여부: {os.path.exists(test_file)}")

        # 2. Quiz 객체 변환 테스트
        print("\n2. [Quiz 객체 변환 및 출력 테스트]")
        quizzes = load_quizzes(test_file)
        print(f"-> 변환된 Quiz 객체 개수: {len(quizzes)}개")
        print(f"-> 1번 문제 미리보기: {quizzes[0].question}")

        # 3. 손상된 파일 복구 테스트
        print("\n3. [손상된 state.json 자동 복구 테스트]")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("{ 손상된 JSON 데이터 !!!")

        recovered_state = load_state(test_file)
        print(f"-> 복구 후 퀴즈 개수: {len(recovered_state['quizzes'])}개")

        # 4. 스키마 훼손 복구 테스트
        print("\n4. [스키마 훼손 자동 복구 테스트]")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({"wrong_key": 123}))

        recovered_schema_state = load_state(test_file)
        print(f"-> 스키마 복구 후 퀴즈 개수: {len(recovered_schema_state['quizzes'])}개")

    print("\n[모든 storage 모듈 테스트 성공 완료!]")
