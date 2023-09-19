create table log_date ( --qui verra inserita la data della giornata dove sono state calcolate le calorie
    id integer primary key autoincrement,
    entry_date date not null
);
create table food( --questo è la tabella del cibo
    id integer primary key autoincrement,
    name text not null,
    protein integer not null,
    carbohydrates integer not null,
    fat integer not null,
    calories integer not null
);

create table food_date( --qui verranno inseriti i pasti in una data
    food_id integer not null,
    log_date_id integer not null,
    primary key(food_id,log_date_id) --chiave primaria basata sui parametri precendenti

);