"""
퀴즈 게임 프로그램 실행 진입점 (main.py)

프로젝트를 시작하는 메인 실행 파일(Entry Point)입니다.
터미널에서 'python main.py' 명령어로 실행하면 퀴즈 게임이 시작됩니다.

[초보자 팁: 진입점(Entry Point)이란?]
- 프로젝트가 커지면 기능별로 파일(모듈)이 여러 개로 나뉩니다.
- 이때 "어디서부터 프로그램이 시작되는가?"를 명확히 해주는 시작 파일이 main.py입니다.
"""

from game import QuizGame


def main() -> None:
    """
    프로그램의 메인 진입 함수입니다.
    QuizGame 객체를 생성하고 게임 루프(run)를 시작합니다.
    """
    game = QuizGame()
    game.run()


if __name__ == "__main__":
    # 이 파일이 터미널에서 직접 실행되었을 때만 main() 함수를 호출합니다.
    main()
