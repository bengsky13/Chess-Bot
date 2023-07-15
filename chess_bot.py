from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import chess
import chess.pgn
import time
from stockfishpy import Engine
import os
import re
import random
class ChessBot:
    def __init__(self):
        self.engine = Engine('./stockfish', param={'Threads': 10, 'Ponder': None})
        driver = webdriver.Chrome('chromedriver')
        self.move_number = 1
        self.driver = driver
        # self.board_id = "board-vs-personalities" # computer
        self.board_id = "board-single" # online
        self.username = os.getenv("CHESS_USERNAME")
        self.password = os.getenv("CHESS_PASSWORD")
        self.login_url = "https://www.chess.com/login_and_go?returnUrl=https://www.chess.com/"
        self.play_url = "https://www.chess.com/play/online"
        self.color = "white"

    def login(self):
        driver = self.driver
        print(driver.get_window_size())
        driver.get(self.login_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(self.username)
        driver.find_element(By.ID, "password").send_keys(self.password)
        driver.find_element(By.ID, "login").click()
        if driver.current_url == "https://www.chess.com/home":
            print("Login Success")
        else:
            print("Login Failed")
            driver.quit()

    def find_match(self):
        html = ""
        pgn = ""
        open('pgn.pgn', 'w').close()
        self.move_number = 1
        driver = self.driver
        driver.get(self.play_url)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-cy="new-game-index-play"]'))).click()
            html = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'live-game-start-component'))).get_attribute("innerHTML")
        except:
            return self.find_match()
        time.sleep(3)
        if '<strong>New Game</strong> <br> <span><a href="https://www.chess.com/member/'+self.username in html:
            self.color = "white"
            return "white"
        else:
            self.color = "black"
            return "black"


    def get_color(self):
        print('a')

    def highlight_move(self, best_move):

        self.driver.execute_script("""
            chessboard = document.getElementById(arguments[4]);

            highlight1_pos = arguments[0].charCodeAt() - 'a'.charCodeAt() + 1 
            highlight1_class = highlight1_pos + arguments[1];
            element = document.createElement('div'); 
            element.setAttribute("id", "target-piece1");        
            element.setAttribute("class", "highlight square-" + highlight1_class);        
            element.setAttribute("style", "background-color: rgb(235, 97, 80); opacity: 0.8");  
            element.setAttribute("data-test-element", "highlight")  
            element.setAttribute("data-piece-id", highlight1_class)    
            chessboard.appendChild(element);

            highlight2_pos = arguments[2].charCodeAt() - 'a'.charCodeAt() + 1
            highlight2_class = highlight2_pos + arguments[3];
            element = document.createElement('div');
            element.setAttribute("id", "target-piece2");        
            element.setAttribute("class", "highlight square-" + highlight2_class);        
            element.setAttribute("style", "background-color: rgb(235, 97, 80); opacity: 0.8");  
            element.setAttribute("data-test-element", "highlight")    
            element.setAttribute("data-piece-id", highlight2_class)    
            chessboard.appendChild(element);
        """, best_move[0], best_move[1], best_move[2], best_move[3], self.board_id)
        return
    def move_piece(self):
        try:
            driver = self.driver
            if self.move_number > 30:
                rand = 0.15
            elif self.move_number > 20:
                rand = random.randint(2, 5)
            elif self.move_number > 10:
                rand = random.randint(5, 10)
            else:
                rand = 0.05
            self.move_number += 1
            time.sleep(rand)
            driver.execute_script("window.scrollTo(0, 0);")

            element = driver.find_element(By.XPATH, '//*[@id="target-piece1"]')
            ActionChains(driver).move_to_element_with_offset(
                element, 30, 30).click().perform()
            time.sleep(0.05)
            element = driver.find_element(By.XPATH, '//*[@id="target-piece2"]')
            ActionChains(driver).move_to_element_with_offset(
                element, 30, 30).click().perform()

            self.driver.execute_script("""
            document.getElementById("target-piece1").remove()
            document.getElementById("target-piece2").remove()
            """)
        except Exception as e:
            print(e)

    def get_pgn(self, pgn):
        driver = self.driver
        found = False
        while (not found):
            time.sleep(1)
            try:
                try:
                    driver.find_element(By.CLASS_NAME, "game-over-modal-content")
                    print("Game Ended")
                    color = self.find_match()
                    print("Color:",color)
                    if "white" == color:
                        self.highlight_move("e2e4")
                        self.move_piece()
                except:
                    found = False
                last_move = None
                opponent = "white" if self.color == "black" else "black"
                elements = driver.find_element(By.CLASS_NAME, 'vertical-move-list').find_elements(By.CLASS_NAME, 'move')
                if self.color == "black" and len(elements) > 0:
                    try:
                        last_move = elements[-1].find_element(By.CLASS_NAME, self.color)
                    except:
                        found = True
                else:
                    last_move = elements[-1].find_element(By.CLASS_NAME, opponent).get_attribute("innerHTML")
                    found = True
            except:
                found = False

        html = ""
        elements = driver.find_element(By.CLASS_NAME, 'vertical-move-list').find_elements(By.CLASS_NAME, 'move')
        for i in elements:
            for j in i.find_elements(By.CLASS_NAME, "node"):            
                html += j.get_attribute("outerHTML").strip()
        pattern = r'<div .*?>(.*?)</div>'
        span_pattern = r'<span.*?>(.*?)</span>'
        parsed = re.findall(pattern, html)
        figure = r'data-figurine="(\w)"'
        if self.color == "black":
            parsed.append("*")
        parsed = [f'{"".join(re.findall(figure, parsed[i]))}{re.sub(span_pattern, "", parsed[i])} {"".join(re.findall(figure, parsed[i+1]))}{re.sub(span_pattern, "", parsed[i+1])}' for i in range(0, len(parsed), 2)]
        pgn = ' '.join(f'{i+1}. {value}' for (i, value) in enumerate(parsed))
        pgn = re.sub(r'<div[^>]*>|<\/div>', '', pgn)
        print(pgn)
        with open("pgn.pgn", "w") as file:
            file.write(pgn)
        return pgn, last_move
    def get_best_move(self):
        engine = self.engine
        try:
            pgnfilename = str('pgn.pgn')
            with open(pgnfilename) as f:
                game = chess.pgn.read_game(f)

            game = game.end()
            board = game.board()

            engine.ucinewgame()
            engine.setposition(board.fen())

            move = engine.bestmove()
            bestmove = move['bestmove']
        except:
            exit()

        return bestmove