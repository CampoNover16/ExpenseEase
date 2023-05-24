# ExpenseEase
It's coursework for PTN lectures in PJATK. This web application is dedicated to helping you manage your expenses and take control of your finances! <br />

Our website offers a range of tools and resources to help you stay on top of your expenses, including budget tracking tools, expense categories, and spending reports.
You can easily add your income and expenses to our system, categorize them, and view detailed reports on your spending habits.<br />

Our goal is to empower you to make smarter financial choices and achieve your financial goals. Whether you're looking to save for a down payment on a house, pay off debt, or simply want to have a better understanding of your spending, we're here to help. 

## Contribution
Project requires installed python on your device(atleast version 3.11).<br />
Make sure you added to environmental variables path to python and python scripts.<br />
After that in the terminal console enter the following commands<br />

To create an environment
```pip
py -3 -m venv .venv
```

To activate an environment
```pip
.venv\Scripts\activate
```

If you cannot run your virtual environment try running this command 
```pip
Set-ExecutionPolicy Unrestricted -Scope Process
```
This would allow running virtualenv in the current PowerShell session.

To install flask
```pip
pip install Flask
```

To install mysql for flask
```pip
pip install flask_mysqldb
```

To install session
```pip
pip install Flask-Session
```

To install XlsxWriter
```pip
pip install XlsxWriter
```

And after that your project is ready to run. To make that simply run command
```pip
python app.py
```

## Credits
Sebastian Mackiewicz - https://github.com/CampoNover16 <br/>
Mikolaj Kusinski - https://github.com/Mikolajkusinski

## License

MIT