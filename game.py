"""
퀴즈 게임 엔진 모듈 (game.py)

이 모듈은 퀴즈 게임의 전체 흐름(게임 루프, 점수 계산, 메뉴 처리, 퀴즈 관리)을 총괄하는
'QuizGame' 클래스를 정의합니다.

[역할 분리와 객체지향 설계]
- Quiz (quiz.py): 단일 퀴즈 데이터 표현 및 출력
- storage (storage.py): 파일 입출력 및 데이터 보관/복구
- input_utils (input_utils.py): 안전한 사용자 입력 및 강제 종료 예외 처리
- QuizGame (game.py): 이 모든 모듈을 조율하여 실제 게임을 진행하는 총감독

초보자도 쉽게 읽고 수정 포인트를 찾을 수 있도록 상세한 한국어 주석을 달아두었습니다.
"""

from __future__ import annotations

import random
import sys
from datetime import datetime
from typing import Any

from input_utils import get_int_input, get_text_input, get_yes_no_input, safe_exit
from quiz import Quiz
from storage import STATE_FILE_PATH, load_state, save_state

# ========================================================
# [게임 설정 상수]
# 나중에 게임 규칙을 바꿀 때 이 값들을 손쉽게 변경할 수 있습니다.
# ========================================================
CHOICES_COUNT: int = 4        # 기본 선택지 개수 (4지선다)
SCORE_PER_CORRECT: int = 10   # 정답 1개당 기본 점수 (10점)
HINT_PENALTY: int = 3         # 힌트 1회 사용 시 차감 점수 (3점)


class QuizGame:
    """
    퀴즈 게임의 전체 진행을 담당하는 클래스입니다.

    [속성(데이터)]
    - filepath (str): 상태를 저장하고 불러올 JSON 파일 경로
    - quizzes (list[Quiz]): 현재 게임에 등록된 Quiz 객체 목록
    - best_score (int): 역대 최고 점수
    - history (list[dict]): 역대 플레이 기록 목록

    [주요 메서드(기능 분리)]
    1. calculate_score(): 점수 계산 방식 전담 (수정 포인트)
    2. play_game(): 퀴즈 출제, 정답 판정, 점수 갱신 및 기록
    3. add_quiz(): 새 퀴즈 입력 검증 및 등록
    4. list_quizzes(): 등록된 퀴즈 목록 열람
    5. delete_quiz(): 지정한 번호의 퀴즈 삭제
    6. view_scores(): 최고 점수 및 역대 플레이 히스토리 조회
    7. save(): 현재 게임 상태를 파일에 저장
    8. run(): 메인 메뉴 반복 실행 루프
    """

    def __init__(self, filepath: str = STATE_FILE_PATH) -> None:
        """
        QuizGame 객체를 생성하고 저장 파일에서 기존 데이터를 불러옵니다.

        :param filepath: 상태 JSON 파일 경로 (기본값: "state.json")
        """
        self.filepath: str = filepath

        # storage 모듈을 통해 state.json 파일에서 상태를 불러옵니다.
        state = load_state(self.filepath)

        # JSON에서 읽어온 딕셔너리 리스트를 Quiz 객체 리스트로 조립합니다.
        self.quizzes: list[Quiz] = [Quiz.from_dict(raw) for raw in state.get("quizzes", [])]
        self.best_score: int = int(state.get("best_score", 0))
        self.history: list[dict[str, Any]] = list(state.get("history", []))

    def save(self) -> bool:
        """
        현재 메모리에 있는 퀴즈 목록, 최고 점수, 히스토리를 state.json 파일에 저장합니다.
        (프로그램 종료 전이나 데이터 변경 직후 즉시 호출됩니다.)

        :return: 저장 성공 여부 (True/False)
        """
        state_dict: dict[str, Any] = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
        }
        return save_state(state_dict, self.filepath)

    # ----------------------------------------------------
    # [수정 포인트 1] 점수 계산 로직
    # 점수 체계를 바꾸고 싶을 때(예: 백분율, 차등 점수 등) 이 메서드만 수정하면 됩니다.
    # ----------------------------------------------------
    def calculate_score(
        self,
        correct_count: int,
        total_questions: int,
        hint_used_count: int = 0,
    ) -> int:
        """
        맞힌 문제 수, 전체 문제 수, 힌트 사용 횟수를 바탕으로 최종 점수를 계산합니다.

        [점수 체계]
        - 정답 1개당 +SCORE_PER_CORRECT(10점) 획득
        - 힌트 1회 사용당 -HINT_PENALTY(3점) 차감
        - 점수가 0점 미만(음수)으로 떨어지지 않도록 최소 0점을 보장합니다. (max(0, 점수))

        :param correct_count: 맞힌 문제 수
        :param total_questions: 푼 전체 문제 수
        :param hint_used_count: 힌트를 확인한 횟수 (기본값: 0)
        :return: 계산된 최종 점수 (최소 0점)
        """
        if total_questions == 0:
            return 0
        raw_score = (correct_count * SCORE_PER_CORRECT) - (hint_used_count * HINT_PENALTY)
        # 0점 미만 방어
        return max(0, raw_score)

    # ----------------------------------------------------
    # [기능 1] 퀴즈 풀기
    # ----------------------------------------------------
    def play_game(self) -> None:
        """
        사용자 설정(문제 수 선택, 랜덤 출제 여부)에 따라 퀴즈를 출제하고,
        문제 풀이 중 힌트 보기(점수 차감) 및 정답/오답 판정, 점수 갱신/저장을 진행합니다.
        """
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요!")
            return

        available_total = len(self.quizzes)

        # 1. 출제 문제 수 선택 (1 ~ 현재 등록된 문제 수)
        print("\n" + "=" * 50)
        print(f"🎯 [퀴즈 설정] (현재 등록된 문제: 총 {available_total}개)")
        print("=" * 50)
        question_count = get_int_input(
            f"출제할 문제 수를 입력하세요 (1~{available_total}): ",
            min_val=1,
            max_val=available_total,
            on_exit=self.save,
        )

        # 2. 랜덤 출제 여부 선택 (y/n)
        is_random = get_yes_no_input(
            "문제 출제 순서를 무작위(랜덤)로 섞으시겠습니까? (y/n): ",
            on_exit=self.save,
        )

        # 퀴즈 목록 추출 (랜덤 추출 또는 앞에서부터 순서대로 추출)
        if is_random:
            # random.sample(): 중복 없이 원하는 개수만큼 무작위 추출
            selected_quizzes = random.sample(self.quizzes, question_count)
        else:
            selected_quizzes = self.quizzes[:question_count]

        # 3. 퀴즈 풀이 진행
        correct_count = 0
        hint_used_total = 0

        print("\n" + "=" * 50)
        order_text = "무작위(랜덤)" if is_random else "기본 순서"
        print(f"🚀 퀴즈를 시작합니다! (출제 문제 수: {question_count}개 | 순서: {order_text})")
        print(f"💡 [팁] 보기 번호(1~4) 대신 '0'을 누르면 힌트를 볼 수 있습니다. (힌트 확인 시 {HINT_PENALTY}점 차감)")
        print("=" * 50)

        for index, quiz in enumerate(selected_quizzes, start=1):
            print(f"\n[문제 {index} / {question_count}]")
            quiz.display()

            # 이번 문제에서 이미 힌트를 확인했는지 추적 (중복 차감 방지)
            hint_viewed_this_question = False

            while True:
                choice = get_int_input(
                    f"정답 번호를 선택하세요 (1~{len(quiz.choices)}, 힌트 보기: 0): ",
                    min_val=0,
                    max_val=len(quiz.choices),
                    on_exit=self.save,
                )

                # 0번 입력: 힌트 보기
                if choice == 0:
                    if not quiz.hint:
                        print("💡 [힌트] 제공된 힌트가 없습니다. (힌트가 없으므로 점수는 차감되지 않습니다.)")
                    else:
                        quiz.display_hint()
                        if not hint_viewed_this_question:
                            hint_viewed_this_question = True
                            hint_used_total += 1
                            print(f"⚠️ 힌트를 확인했습니다! (최종 점수에서 -{HINT_PENALTY}점 차감)")
                        else:
                            print("ℹ️ 이미 확인한 힌트입니다. (추가 차감 없음)")
                    # 힌트 확인 후 다시 답안을 입력할 수 있도록 루프를 이어갑니다.
                    continue

                # 1~4번 입력: 정답 선택 완료
                break

            # 정답 판정
            if quiz.is_correct(choice):
                print(f"🎉 정답입니다! (+{SCORE_PER_CORRECT}점)")
                correct_count += 1
            else:
                print(f"❌ 아쉽네요, 오답입니다! (선택: {choice}번)")

            # 해설 출력
            quiz.display_explanation()

        # 4. 게임 종료 후 점수 계산 (힌트 감점 및 0점 방어 적용)
        final_score = self.calculate_score(correct_count, question_count, hint_used_total)

        print("\n" + "=" * 50)
        print("🏁 퀴즈를 모두 마쳤습니다! 결과 발표:")
        print(f"- 푼 문제 수: {question_count}문제")
        print(f"- 맞힌 개수: {correct_count}개")
        print(f"- 힌트 사용: {hint_used_total}회 (총 -{hint_used_total * HINT_PENALTY}점 차감)")
        print(f"- 획득한 최종 점수: {final_score}점 (최소 0점 방어 적용)")

        # 최고 점수 갱신 확인
        is_new_best = final_score > self.best_score
        if is_new_best:
            print(f"🎊 축하합니다! 새로운 최고 점수를 달성하셨습니다! (기존: {self.best_score}점 -> 신기록: {final_score}점)")
            self.best_score = final_score
        else:
            print(f"- 역대 최고 점수: {self.best_score}점")

        # 플레이 히스토리 기록 추가
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "date": now_str,
            "total": question_count,
            "correct": correct_count,
            "hint_used": hint_used_total,
            "score": final_score,
        }
        self.history.append(record)

        # 변경된 상태 파일에 즉시 저장
        self.save()
        print("💾 게임 결과가 안전하게 저장되었습니다.")
        print("=" * 50)

    # ----------------------------------------------------
    # [기능 2] 퀴즈 추가
    # ----------------------------------------------------
    def add_quiz(self) -> None:
        """
        새로운 퀴즈(문제, 4개 선택지, 정답 번호, 힌트, 해설)를 입력받아 등록하고 저장합니다.
        """
        print("\n" + "=" * 50)
        print("➕ [새 퀴즈 추가하기]")
        print("=" * 50)

        # 1. 문제 입력 (빈 문자열 불가)
        question = get_text_input("1. 문제 내용을 입력하세요: ", on_exit=self.save)

        # 2. 4개의 선택지 입력
        print(f"\n2. {CHOICES_COUNT}개의 선택지를 차례대로 입력하세요.")
        choices: list[str] = []
        for i in range(1, CHOICES_COUNT + 1):
            choice_text = get_text_input(f"  - 보기 {i}: ", on_exit=self.save)
            choices.append(choice_text)

        # 3. 정답 번호 입력 (1~CHOICES_COUNT 범위 검증)
        print(f"\n3. 위 보기 중 정답 번호(1~{CHOICES_COUNT})를 지정하세요.")
        answer = get_int_input(
            f"정답 번호 입력 (1~{CHOICES_COUNT}): ",
            min_val=1,
            max_val=CHOICES_COUNT,
            on_exit=self.save,
        )

        # 4. 힌트 및 해설 입력 (선택 사항: Enter만 치면 생략 가능)
        print("\n4. 힌트와 해설을 입력하세요 (생략하려면 그냥 Enter를 누르세요).")
        hint = get_text_input("  - 힌트 (선택): ", allow_empty=True, on_exit=self.save)
        explanation = get_text_input("  - 해설 (선택): ", allow_empty=True, on_exit=self.save)

        # Quiz 객체 생성 및 리스트에 추가
        new_quiz = Quiz(
            question=question,
            choices=choices,
            answer=answer,
            hint=hint,
            explanation=explanation,
        )
        self.quizzes.append(new_quiz)

        # 파일에 즉시 반영
        self.save()
        print("\n✅ 새 퀴즈가 성공적으로 추가되고 state.json에 저장되었습니다!")

    # ----------------------------------------------------
    # [기능 3] 퀴즈 목록 조회
    # ----------------------------------------------------
    def list_quizzes(self) -> None:
        """
        현재 등록되어 있는 모든 퀴즈의 목록을 간략히 보여줍니다.
        """
        if not self.quizzes:
            print("\n⚠️ 현재 등록된 퀴즈가 없습니다.")
            return

        print("\n" + "=" * 50)
        print(f"📋 [퀴즈 목록] (총 {len(self.quizzes)}문제)")
        print("=" * 50)

        for index, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[{index}번 문제] {quiz.question}")
            for c_idx, choice in enumerate(quiz.choices, start=1):
                marker = " (정답)" if c_idx == quiz.answer else ""
                print(f"   {c_idx}. {choice}{marker}")
            if quiz.hint:
                print(f"   💡 힌트: {quiz.hint}")

        print("=" * 50)

    # ----------------------------------------------------
    # [기능 4] 퀴즈 삭제
    # ----------------------------------------------------
    def delete_quiz(self) -> None:
        """
        등록된 퀴즈 중 하나를 번호로 지정하여 삭제하고 저장합니다.
        """
        if not self.quizzes:
            print("\n⚠️ 삭제할 퀴즈가 없습니다.")
            return

        print("\n" + "=" * 50)
        print("🗑️ [퀴즈 삭제하기]")
        print("=" * 50)

        # 삭제를 돕기 위해 문제 제목들만 간략히 출력
        for index, quiz in enumerate(self.quizzes, start=1):
            # 문제가 너무 길면 앞부분만 자르고 줄임표 처리
            short_q = quiz.question if len(quiz.question) <= 30 else quiz.question[:27] + "..."
            print(f"  {index}. {short_q}")

        print("  0. 삭제 취소")
        print("-" * 50)

        target_num = get_int_input(
            f"삭제할 퀴즈 번호를 입력하세요 (1~{len(self.quizzes)}, 취소: 0): ",
            min_val=0,
            max_val=len(self.quizzes),
            on_exit=self.save,
        )

        if target_num == 0:
            print("취소되었습니다. 메뉴로 돌아갑니다.")
            return

        # 리스트 인덱스는 0부터 시작하므로 target_num - 1
        deleted_quiz = self.quizzes.pop(target_num - 1)
        self.save()
        print(f"\n🗑️ '{deleted_quiz.question}' 퀴즈가 삭제되었습니다.")
        print(f"남은 퀴즈 수: {len(self.quizzes)}개")

    # ----------------------------------------------------
    # [기능 5] 점수 및 히스토리 조회
    # ----------------------------------------------------
    def view_scores(self) -> None:
        """
        역대 최고 점수와 플레이 기록(날짜, 문제 수, 점수 등)을 조회합니다.
        """
        print("\n" + "=" * 50)
        print("🏆 [점수 및 플레이 기록]")
        print("=" * 50)
        print(f"⭐ 역대 최고 점수: {self.best_score}점\n")

        if not self.history:
            print("ℹ️ 아직 플레이한 기록이 없습니다. 먼저 퀴즈를 풀어보세요!")
            print("=" * 50)
            return

        print("📜 [최근 플레이 히스토리]")
        print("-" * 50)
        # 최근 기록이 위로 오도록 역순(reversed)으로 출력하거나 순서대로 출력
        for idx, rec in enumerate(self.history, start=1):
            date_str = rec.get("date", "날짜 없음")
            total = rec.get("total", 0)
            correct = rec.get("correct", 0)
            score = rec.get("score", 0)
            hints = rec.get("hint_used", 0)
            hint_str = f" (힌트: {hints}회)" if hints > 0 else ""
            print(f" {idx}. [{date_str}] 정답: {correct}/{total}개{hint_str} | 점수: {score}점")

        print("=" * 50)

    # ----------------------------------------------------
    # [기능 6] 안전 종료
    # ----------------------------------------------------
    def exit_game(self) -> None:
        """
        현재 상태를 파일에 저장하고 프로그램을 안전하게 종료합니다.
        """
        safe_exit(on_exit=self.save, message="\n👋 퀴즈 게임을 종료합니다. 이용해 주셔서 감사합니다!")

    # ----------------------------------------------------
    # [메인 메뉴 화면 및 실행 루프]
    # ----------------------------------------------------
    def display_menu(self) -> None:
        """메인 메뉴 선택지를 화면에 출력합니다."""
        print("\n" + "=" * 50)
        print("⚽ [UEFA 챔피언스리그 퀴즈 게임]")
        print("=" * 50)
        print("  1. 퀴즈 풀기")
        print("  2. 퀴즈 추가")
        print("  3. 퀴즈 목록")
        print("  4. 퀴즈 삭제")
        print("  5. 점수 확인")
        print("  6. 게임 종료")
        print("=" * 50)

    def run(self) -> None:
        """
        퀴즈 게임의 전체 메인 루프입니다.
        사용자가 6번(종료)을 선택하거나 Ctrl+C를 누를 때까지 반복 실행됩니다.
        """
        while True:
            self.display_menu()
            choice = get_int_input(
                "원하시는 메뉴 번호를 선택하세요 (1~6): ",
                min_val=1,
                max_val=6,
                on_exit=self.save,
            )

            if choice == 1:
                self.play_game()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.list_quizzes()
            elif choice == 4:
                self.delete_quiz()
            elif choice == 5:
                self.view_scores()
            elif choice == 6:
                self.exit_game()


# ========================================================
# [직접 실행 테스트 영역]
# ========================================================
if __name__ == "__main__":
    game = QuizGame()
    game.run()
