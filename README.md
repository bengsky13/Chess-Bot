# Chess-Bot

Python chess bot that plays chess online on chess.com using Stockfish Engine

## Getting Started

Install python dependencies

```bash
pip install -r requirements.txt
```

Setting your chess.com account
### Linux / MacOS

```bash
export CHESS_USERNAME=yourusername
export CHESS_PASSWORD=yourpassword
```
### Windows
```bash
set CHESS_USERNAME=yourusername
set CHESS_PASSWORD=yourpassword
```

For Windows please update the chromedriver path in
chess_bot.py
```python
driver = webdriver.Chrome('CHANGEME')
```


run the program

```bash
python main.py
```

## Disclaimer

**This project is written only for educational purpose!!!**

using **Chess-Bot** could get you banned.
