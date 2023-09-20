from flask import Flask, render_template, g , request #importo request per fare controlli con la pagina sulle richieste HTTP
#La g sta per global object
#Render template serve a prendere dalla cartella templates e poterli usare su flask
from datetime import datetime
from database import get_db,connect_db
app = Flask(__name__)

@app.teardown_appcontext
def close_db(error): #Il db viene chiuso
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/' , methods=["GET","POST"])
def index():
    db = get_db()
    if request.method =="POST":
        date = request.form['date']
        dt = datetime.strptime(date, '%Y-%m-%d') #Crea oggetto datetime da stringa
        database_date = datetime.strftime(dt,'%Y%m%d') #Formatta la data in stringa

        db.execute("INSERT INTO log_date (entry_date) VALUES (?)",[database_date])
        db.commit()

    cur = db.execute('''SELECT log_date.entry_date, 
                     sum(food.protein) AS protein,sum(food.carbohydrates) AS carbohydrates,sum(food.fat) AS fat,sum(food.calories) AS calories 
                     FROM log_date 
                     LEFT JOIN food_date ON food_date.log_date_id = log_date.id 
                     LEFT JOIN food ON food.id = food_date.food_id 
                     GROUP BY log_date.id 
                     ORDER BY log_date.entry_date DESC
                     ''')
    result = cur.fetchall() 
    data_results = list()
    for i in result:
        single_data = {}
        single_data['entry_date'] = i['entry_date']
        d = datetime.strptime(str(i['entry_date']),'%Y%m%d')
        single_data['pretty_date'] = datetime.strftime(d, '%B %d , %Y')
        single_data['protein'] = i['protein']
        single_data['carbohydrates'] = i['carbohydrates']
        single_data['fat'] = i['fat']
        single_data['calories'] = i['calories']
        data_results.append(single_data)

    return render_template('home.html',data_results=data_results) 

@app.route('/dailylog/<date>', methods=["GET","POST"])
def dailylog(date):
    db = get_db()
    cur = db.execute('SELECT entry_date,id FROM log_date WHERE entry_date = ?',[date])
    result = cur.fetchone()
    if request.method == "POST":
        db.execute('''INSERT INTO food_date (food_id,log_date_id)
                   VALUES (?,?)''',[request.form['foodselect'],result['id']])
        db.commit()

    d = datetime.strptime(str(result["entry_date"]), '%Y%m%d' )
    entry_date = datetime.strftime(d , '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')

    foodcur = db.execute("SELECT id,name FROM food")
    foodresult = foodcur.fetchall()

    log_cur=db.execute('''SELECT food.name,food.protein,food.carbohydrates,food.fat,food.calories 
                       FROM log_date 
                       JOIN food_date ON food_date.log_date_id = log_date.id 
                       JOIN food ON food.id = food_date.food_id 
                       WHERE log_date.entry_date = ?''',[date]) 
    #Con la query qui sopra possiamo entrare nella tabella dei log delle date tramite l'id della tabella dei pasti e facciamo la stessa cosa con la tabella del cibo
    log_results = log_cur.fetchall()
    proteins = 0
    carbohydratess = 0
    fats = 0
    calories = 0

    for i in log_results:
        proteins += i['protein']
        carbohydratess += i['carbohydrates']
        fats += i['fat']
        calories += i['calories']

    list_food = [proteins,carbohydratess,fats,calories]


    return render_template('day.html',
                        pretty_date=pretty_date,
                            food_result=foodresult,
                                log_results=log_results,
                                    list_food=list_food,
                                        entry_date=entry_date)

@app.route('/addfood' , methods=["GET","POST"])
def addfood():
    db = get_db()
    if request.method == "POST":
        name = request.form["food_name"] #Prendo dal form i dati
        protein = int(request.form["protein"])
        carbs = int(request.form["carbs"])
        fats = int(request.form["fats"])
        #Nella variabile calories andrà il cacolo delle calorie di quel determinato cibo
        calories = protein * 4 + carbs * 4 + fats * 9
        db = get_db()
        db.execute('''INSERT INTO food (name,protein,carbohydrates,fat,calories) 
                   VALUES (?,?,?,?,?)''',[name,protein,carbs,fats,calories]) #eseguo la query
        db.commit()
    cur = db.execute("SELECT name,protein,carbohydrates,fat,calories FROM food")
    result=cur.fetchall()

    return render_template('add_food.html',result=result)


if __name__ == '__main__':
    app.run(debug=False)