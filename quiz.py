"""
퀴즈 모델 모듈 (quiz.py)

이 파일은 퀴즈 게임에서 사용되는 '단일 퀴즈 1개'의 데이터와 기능을 정의합니다.
코딩 초보자도 쉽게 읽고 이해할 수 있도록 각 부분마다 상세한 주석을 달아두었습니다.
"""


class Quiz:
    """
    단일 퀴즈 1개의 정보를 담고 관리하는 클래스(설계도)입니다.

    [속성(데이터)]
    - question (str): 문제 내용 (문자열)
    - choices (list[str]): 4개의 보기/선택지 목록 (문자열 리스트)
    - answer (int): 정답 번호 (1, 2, 3, 4 중 하나의 정수)
    - hint (str): 문제 풀이를 돕는 힌트 (문자열)
    - explanation (str): 정답에 대한 해설 및 보충 설명 (문자열)

    [메서드(동작)]
    - display(): 문제와 4개의 선택지를 보기 좋게 화면에 출력합니다.
    - is_correct(): 사용자가 고른 번호가 정답인지 확인하여 True/False를 반환합니다.
    - display_hint(): 힌트를 화면에 출력합니다.
    - display_explanation(): 정답 해설을 화면에 출력합니다.
    """

    def __init__(
        self,
        question: str,
        choices: list[str],
        answer: int,
        hint: str = "",
        explanation: str = "",
    ) -> None:
        """
        Quiz 객체를 처음 만들 때 자동으로 실행되는 초기화 함수(생성자)입니다.

        :param question: 문제 문장
        :param choices: 4개의 보기 목록 (예: ["사과", "바나나", "포도", "딸기"])
        :param answer: 정답 번호 (1부터 4 사이의 정수)
        :param hint: 힌트 문장 (기본값: 빈 문자열)
        :param explanation: 정답 해설 문장 (기본값: 빈 문자열)
        """
        # [데이터 유효성 검사]
        # 초보자 팁: 올바르지 않은 데이터가 들어오면 미리 오류를 내어 프로그램이 꼬이는 것을 방지합니다.
        if len(choices) != 4:
            raise ValueError(f"선택지는 반드시 4개여야 합니다. (현재 개수: {len(choices)}개)")

        if answer not in (1, 2, 3, 4):
            raise ValueError(f"정답 번호는 1, 2, 3, 4 중 하나여야 합니다. (입력값: {answer})")

        # self는 '지금 만들어지고 있는 이 퀴즈 객체 자신'을 의미합니다.
        # self.변수명 형태로 객체 내부의 보관함(속성)에 데이터를 저장합니다.
        self.question: str = question
        self.choices: list[str] = choices
        self.answer: int = answer
        self.hint: str = hint
        self.explanation: str = explanation

    def display(self, show_hint: bool = False) -> None:
        """
        퀴즈 문제와 1~4번 선택지를 터미널 화면에 보기 좋게 출력합니다.

        :param show_hint: True로 지정하면 힌트가 있을 때 함께 출력합니다. (기본값: False)
        """
        print("\n" + "=" * 50)
        print(f"[문제] {self.question}")
        print("-" * 50)

        # enumerate()는 리스트의 순서 번호(0부터 시작)와 내용을 동시에 꺼내줍니다.
        # 사용자가 보는 보기 번호는 1부터 시작하므로 index + 1을 해줍니다.
        for index, choice in enumerate(self.choices, start=1):
            print(f"  {index}. {choice}")

        print("=" * 50)

        # 힌트 출력이 켜져 있고, 힌트 내용이 있으면 힌트도 표시합니다.
        if show_hint and self.hint:
            self.display_hint()

    def is_correct(self, user_choice: int) -> bool:
        """
        사용자가 입력한 번호가 정답인지 확인합니다.

        :param user_choice: 사용자가 선택한 번호 (1~4)
        :return: 정답이면 True, 오답이면 False (불리언 값)
        """
        # 초보자 팁: == 연산자는 양쪽 값이 같으면 True, 다르면 False를 만듭니다.
        # 그 결과(True 또는 False)를 바로 return(반환)합니다.
        return user_choice == self.answer

    def display_hint(self) -> None:
        """힌트를 화면에 출력합니다."""
        if self.hint:
            print(f"💡 [힌트] {self.hint}")
        else:
            print("💡 [힌트] 제공된 힌트가 없습니다.")

    def display_explanation(self) -> None:
        """정답 해설을 화면에 출력합니다."""
        if self.explanation:
            print(f"📖 [해설] (정답: {self.answer}번) {self.explanation}")
        else:
            print(f"📖 [해설] 정답은 {self.answer}번입니다.")


# ========================================================
# [직접 실행 테스트 영역]
# 이 파일(quiz.py)을 직접 'python quiz.py'로 실행할 때만 아래 코드가 실행됩니다.
# 나중에 다른 파일에서 'import Quiz'로 불러올 때는 실행되지 않으므로 안심하세요!
# ========================================================
if __name__ == "__main__":
    print("[Quiz 클래스 단독 동작 테스트]")

    # 1. 퀴즈 객체 1개 생성해보기
    sample_quiz = Quiz(
        question="파이썬(Python)의 공식 마스코트 동물은 무엇일까요?",
        choices=["코끼리", "비단뱀(뱀)", "돌고래", "사자"],
        answer=2,
        hint="프로그래밍 언어 이름의 그리스 신화 유래와 연관이 있습니다.",
        explanation="Python은 거대한 뱀(비단뱀)을 뜻하며, 로고에도 두 마리의 뱀이 형상화되어 있습니다.",
    )

    # 2. 퀴즈 출력 메서드 테스트
    sample_quiz.display()

    # 3. 힌트 출력 테스트
    sample_quiz.display_hint()

    # 4. 정답 확인 메서드 테스트
    test_choice_correct = 2
    test_choice_wrong = 1

    print(f"\n[정답 확인 테스트]")
    print(f"- 선택 2번: {'정답!' if sample_quiz.is_correct(test_choice_correct) else '오답!'}")
    print(f"- 선택 1번: {'정답!' if sample_quiz.is_correct(test_choice_wrong) else '오답!'}")

    # 5. 해설 출력 테스트
    sample_quiz.display_explanation()
