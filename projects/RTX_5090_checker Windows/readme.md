# Running a little annoying GUI for in stock 5090's on Windows

Currently this only works for NewEgg, BestBuy, and Amazon.

I used VSCode to create virtual environment, and assign the preferred Python version.

I used Python 3.10.6 for this environment.

ctrl+shift+p in VSCode to create the environment.

Then ctrl+shift+p again to select the interpreter.

There are some commands in the terminal you can use for this alternatively.

```
cd /path/to/your/project
python3 -m venv .venv
source .venv/bin/activate
```

If you downloaded the requirements.txt file you can do 

```
pip install -r requirements.txt
```

or if not:

```
pip install selenium python-dotenv
```

You'll need to make sure you have the chromedriver.exe that matches closely to your Chrome version for this to work as well.

Here's a guide that works well:
https://developer.chrome.com/docs/chromedriver/get-started

You'll need to place that chromedriver.exe in your project folder.

You can add your own links from NewEgg, BestBuy, or Amazon in the 

```
ITEM_URLS = [

]
```

The python script will just run through them. Should play an annoying beep when it detects inventory availability. Cheers. Feel free to use, or suggest changes. 

When you're in the project directory, right click, open in terminal, and then:

```
python background.py
```

Start turns the bot on, stop turns it off. Ezpz.

Sorry about the rough readme.md. Lazy.