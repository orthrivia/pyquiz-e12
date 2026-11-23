"""
사용자 입력 검증 및 안전 종료 헬퍼 모듈 (input_utils.py)

터미널 환경에서 사용자의 입력을 안전하게 처리하고,
올바르지 않은 입력에 대한 친절한 재입력 안내 및
Ctrl+C(KeyboardInterrupt), EOFError 발생 시 데이터 저장 후 안전 종료를 지원합니다.

[주요 기능]
1. safe_input(): 키보드 인터럽트(Ctrl+C, EOF) 발생 시 안전하게 종료하는 기본 입력 함수
2. get_int_input(): 공백 제거, 빈 입력/문자/범위 밖 숫자 검증 및 재입력 처리
3. get_text_input(): 공백 제거 및 빈 문자열 검증 처리
4. safe_exit(): 전달받은 저장 콜백을 안전하게 호출한 뒤 프로그램을 종료하는 함수

코딩 초보자도 쉽게 원리를 이해하고 복습할 수 있도록 쉬운 주석을 달아두었습니다.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any


def safe_exit(
    on_exit: Callable[[], Any] | None = None,
    message: str = "\n\n👋 프로그램을 종료합니다. 이용해 주셔서 감사합니다!",
) -> None:
    """
    프로그램을 종료하기 전 안전하게 안내 메시지를 출력하고,
    전달받은 저장 콜백(on_exit)이 있다면 실행한 뒤 정상 종료(0)합니다.

    초보자 팁:
    - '콜백(Callback) 함수'란 다른 함수의 인자(재료)로 전달되어 특정 순간(여기서는 종료 직전)에
      대신 실행되는 함수를 말합니다.
    - 게임 진행 중 갑자기 Ctrl+C를 눌러도 지금까지 푼 점수나 상태를 저장할 수 있게 해줍니다.

    :param on_exit: 종료 직전 실행할 함수 (예: storage.save_state 또는 게임 저장 로직)
    :param message: 사용자에게 보여줄 종료 안내 메시지
    """
    print(message)

    # 저장해야 할 작업(콜백 함수)이 등록되어 있다면 실행합니다.
    if on_exit is not None:
        try:
            print("💾 [저장] 종료 전 변경 사항을 안전하게 저장하는 중입니다...")
            on_exit()
            print("✅ [저장 완료] 데이터가 안전하게 저장되었습니다.")
        except Exception as error:
            # 저장 중 오류가 생겨도 프로그램 종료 흐름 자체는 멈추지 않고 알려줍니다.
            print(f"⚠️ [주의] 종료 중 자동 저장에 실패했습니다: {error}")

    # sys.exit(0)은 파이썬 프로그램을 정상(0) 상태로 완전히 종료하라는 명령어입니다.
    sys.exit(0)


def safe_input(
    prompt: str = "",
    on_exit: Callable[[], Any] | None = None,
) -> str:
    """
    파이썬 내장 input() 함수를 감싸서,
    사용자가 Ctrl+C(강제 중단)나 EOF(입력 종료)를 발생시켰을 때
    빨간 에러 메시지(Traceback) 대신 깔끔한 안내와 함께 안전 종료를 수행합니다.

    초보자 팁:
    - KeyboardInterrupt: 사용자가 터미널에서 Ctrl + C 키를 눌렀을 때 발생하는 신호입니다.
    - EOFError (End Of File): 입력 스트림이 예기치 않게 닫혔을 때(예: Ctrl + D 또는 파일 끝) 발생합니다.

    :param prompt: 사용자에게 입력을 유도하는 문구
    :param on_exit: 비정상 종료 감지 시 호출할 저장 함수
    :return: 사용자가 입력한 원본 문자열
    """
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        # 트레이스백(에러 로그)을 터뜨리지 않고 우리가 만든 safe_exit으로 안전하게 이동합니다.
        safe_exit(on_exit=on_exit)
        return ""  # sys.exit()으로 종료되므로 실제로는 도달하지 않습니다.


def get_int_input(
    prompt: str,
    min_val: int | None = None,
    max_val: int | None = None,
    on_exit: Callable[[], Any] | None = None,
) -> int:
    """
    사용자로부터 올바른 정수(숫자)를 입력받을 때까지 반복해서 물어봅니다.

    [검증 단계]
    1. .strip()으로 앞뒤의 쓸데없는 공백 제거
    2. 빈 값(Enter만 누름)인지 검사
    3. 숫자로 바꿀 수 없는 문자("abc", "한글", 특수문자 등)인지 검사
    4. 허용 범위(min_val ~ max_val)를 벗어났는지 검사
    모든 검증을 통과해야만 숫자를 반환(return)합니다.

    :param prompt: 입력 안내 문구 (예: "정답을 선택하세요 (1~4): ")
    :param min_val: 허용 가능한 최소 정수값 (None이면 하한선 없음)
    :param max_val: 허용 가능한 최대 정수값 (None이면 상한선 없음)
    :param on_exit: 강제 종료 시 호출할 저장 함수
    :return: 유효성이 검증된 정수(int)
    """
    while True:
        # 1. 안전하게 사용자 입력 받기
        raw_input = safe_input(prompt, on_exit=on_exit)

        # 2. 앞뒤 공백 제거하기
        # 예: "  2  " -> "2"
        cleaned = raw_input.strip()

        # 3. 빈 입력(Enter만 침) 검사
        if not cleaned:
            print("⚠️ 아무것도 입력되지 않았습니다. 숫자를 입력해 주세요.")
            continue

        # 4. 숫자 변환 가능 여부 검사
        try:
            value = int(cleaned)
        except ValueError:
            print(f"⚠️ '{cleaned}'은(는) 올바른 숫자가 아닙니다. 숫자만 입력해 주세요.")
            continue

        # 5. 숫자 범위(min_val ~ max_val) 검사
        if min_val is not None and max_val is not None:
            if not (min_val <= value <= max_val):
                print(f"⚠️ {min_val}부터 {max_val} 사이의 숫자를 입력해 주세요. (입력값: {value})")
                continue
        elif min_val is not None:
            if value < min_val:
                print(f"⚠️ {min_val} 이상의 숫자를 입력해 주세요. (입력값: {value})")
                continue
        elif max_val is not None:
            if value > max_val:
                print(f"⚠️ {max_val} 이하의 숫자를 입력해 주세요. (입력값: {value})")
                continue

        # 모든 검증을 통과했으므로 정수 반환
        return value


def get_text_input(
    prompt: str,
    allow_empty: bool = False,
    on_exit: Callable[[], Any] | None = None,
) -> str:
    """
    사용자로부터 텍스트(문자열)를 입력받습니다.
    앞뒤 공백을 자동으로 잘라내며, 빈 입력을 방지할 수 있습니다.
    (추후 퀴즈 추가, 사용자 이름 입력 등에서 유용하게 재사용됩니다.)

    :param prompt: 입력 안내 문구
    :param allow_empty: 빈 문자열을 허용할지 여부 (기본값: False)
    :param on_exit: 강제 종료 시 호출할 저장 함수
    :return: 유효성이 검증된 문자열
    """
    while True:
        raw_input = safe_input(prompt, on_exit=on_exit)
        cleaned = raw_input.strip()

        # 빈 문자열을 허용하지 않는데 비어있는 경우
        if not allow_empty and not cleaned:
            print("⚠️ 공백만 있거나 비어있는 내용은 입력할 수 없습니다. 내용을 입력해 주세요.")
            continue

        return cleaned


# ========================================================
# [직접 실행 테스트 / 데모 영역]
# 이 파일(input_utils.py)을 직접 실행할 때 동작을 눈으로 확인할 수 있는 예제 코드입니다.
# ========================================================
if __name__ == "__main__":
    print("[input_utils 모듈 동작 데모]\n")

    # 가상의 저장 콜백 함수
    def mock_save() -> None:
        print("  -> [콜백 실행] 현재 진행 상황을 파일에 안전하게 기록했습니다.")

    print("1. 숫자 입력 테스트 (1부터 4 사이의 번호 선택, Ctrl+C로 종료 가능)")
    print("   (팁: 잘못된 문자나 빈 엔터를 쳐보세요)")
    try:
        user_num = get_int_input("번호를 입력하세요 (1~4): ", min_val=1, max_val=4, on_exit=mock_save)
        print(f"선택된 번호: {user_num}\n")

        print("2. 텍스트 입력 테스트 (공백 불가)")
        user_text = get_text_input("퀴즈 문제 내용을 입력하세요: ", on_exit=mock_save)
        print(f"입력된 내용: {user_text}\n")
    except SystemExit:
        pass

