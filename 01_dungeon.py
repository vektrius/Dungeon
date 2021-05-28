# -*- coding: utf-8 -*-

# С помощью JSON файла rpg.json задана "карта" подземелья.
# Подземелье было выкопано монстрами и они всё ещё скрываются где-то в его глубинах,
# планируя набеги на близлежащие поселения.
# Само подземелье состоит из двух главных разветвлений и нескольких развилок,
# и лишь один из путей приведёт вас к главному Боссу
# и позволит предотвратить набеги и спасти мирных жителей.

# Напишите игру, в которой пользователь, с помощью консоли,
# сможет:
# 1) исследовать это подземелье:
#   -- передвижение должно осуществляться присваиванием переменной и только в одну сторону
#   -- перемещаясь из одной локации в другую, пользователь теряет время, указанное в конце названия каждой локации
# Так, перейдя в локацию Location_1_tm500 - вам необходимо будет списать со счёта 500 секунд.
# Тег, в названии локации, указывающий на время - 'tm'.
#
# 2) сражаться с монстрами:
#   -- сражение имитируется списанием со счета персонажа N-количества времени и получением N-количества опыта
#   -- опыт и время указаны в названиях монстров (после exp указано значение опыта и после tm указано время)
# Так, если в локации вы обнаружили монстра Mob_exp10_tm20 (или Boss_exp10_tm20)
# необходимо списать со счета 20 секунд и добавить 10 очков опыта.
# Теги указывающие на опыт и время - 'exp' и 'tm'.
# После того, как игра будет готова, сыграйте в неё и наберите 280 очков при положительном остатке времени.

# По мере продвижения вам так же необходимо вести журнал,
# в котором должна содержаться следующая информация:
# -- текущее положение
# -- текущее количество опыта
# -- текущая дата (отсчёт вести с первой локации с помощью datetime)
# После прохождения лабиринта, набора 280 очков опыта и проверки на остаток времени (remaining_time > 0),
# журнал необходимо записать в csv файл (назвать dungeon.csv, названия столбцов взять из field_names).

# Пример лога игры:
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 1234567890.0987654321 секунд
# Прошло уже 0:00:00
# Внутри вы видите:
# -- Монстра Mob_exp10_tm0
# -- Вход в локацию: Location_1_tm10400000
# -- Вход в локацию: Location_2_tm333000000
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Выход
import re
from datetime import datetime
from decimal import Decimal
import csv
import json

# если изначально не писать число в виде строки - теряется точность!
field_names = ['current_location', 'current_experience', 'current_date']
location_re = r'Location_(?:(?:B\d+)|\d+)_tm((\d+\.\d+)|\d+)'

# TODO тут ваш код


def check_mob(str):
    mob_re = r'Mob_exp\d+_tm\d+'
    match = re.search(mob_re,str)
    if match:
        return True
    else:
        return False


def check_boss(str):
    boss_re = r'Boss\d*_exp\d+_tm\d+'
    match = re.search(boss_re,str)
    if match:
        return True
    else:
        return False


def check_loc(str):
    match = re.search(location_re,str)
    if match:
        return True
    else:
        return False


def write_csv(path,data):
    with open(path, "w", newline='') as out_file:
        writer = csv.writer(out_file)
        for row in data:
            writer.writerow(row)

class GameDungeon:
    def __init__(self):
        self.act_num = 0
        with open('rpg.json', 'r') as file:
            self.data = json.load(file)
        self.remaining_time = '1234567890.0987654321'
        self.current_location = self.data["Location_0_tm0"]
        self.time_from_the_beginning = datetime.today()
        self.exp = Decimal(0)
        self.current_act = []
        self.loc_name = ["Location_0_tm0"]
        self.list_exp_loc_date = [field_names]


    def Start(self):
        while self.exp < 280 and Decimal(self.remaining_time) > 0:
            act = self.get_info()

            if act == None:
                print('Вы проиграли!')
                break
            elif act == 'Error':
                print('Введите верное число!')
                self.current_act.clear()
                continue
            self.event_handling(act)
        else:
            if self.remaining_time <= 0:
                print('Вы проиграли!')
            else:
                print('Вы победили!')
                write_csv('test.csv',self.list_exp_loc_date)

    def event_handling(self,act):
        if check_mob(act):
            mob_re = r'Mob_exp(\d+)_tm(\d+)'
            mob_exp = int(re.findall(mob_re, act)[0][0])
            mob_time = int(re.findall(mob_re, act)[0][1])
            self.exp += mob_exp
            self.remaining_time = Decimal(self.remaining_time) - Decimal(mob_time)
            act_mob = re.search(mob_re, act)[0]
            self.current_location.pop(self.act_num)
            self.current_act.clear()

        elif check_boss(act):
            mob_re = r'Boss\d*_exp(\d+)_tm(\d+)'
            mob_exp = int(re.findall(mob_re, act)[0][0])
            mob_time = int(re.findall(mob_re, act)[0][1])
            self.exp += mob_exp
            self.remaining_time = Decimal(self.remaining_time) - Decimal(mob_time)
            act_mob = re.search(mob_re, act)[0]
            self.current_location.pop(self.act_num)
            self.current_act.clear()

        elif check_loc(act):
            self.loc_name = re.search(location_re, act)
            self.current_location = self.current_location[self.act_num][self.loc_name[0]]
            loc_exp = re.findall(location_re, act)[0][0]
            self.remaining_time = Decimal(self.remaining_time) - Decimal(loc_exp)
            self.current_act.clear()


    def get_info(self):
        current_time = datetime.today() - self.time_from_the_beginning
        self.list_exp_loc_date.append([self.loc_name[0], str(self.exp)[0], str(current_time)])
        print('Вы находитесь в', self.loc_name[0] )
        print(f'Колл-во опыта - {self.exp}, времени осталось - {Decimal(self.remaining_time)}')
        print('Прошло уже:', current_time)

        for i in self.current_location:
            if isinstance(i, str) and (check_mob(i) or check_boss(i)):
                print(f'-- Монстр {i}')
                self.current_act.append(f'Атаковать монстра {i}')
            elif type(i) == list:
                fin_exp = 0
                fin_time = 0
                print('Вы нарвались на пачку гоблинов!')
                for j in i:
                    mob_re = r'Mob_exp(\d+)_tm(\d+)'
                    mob_exp = int(re.findall(mob_re, j)[0][0])
                    mob_time = int(re.findall(mob_re, j)[0][1])
                    fin_exp += mob_exp
                    fin_time += mob_time
                Mob = f'Mob_exp{fin_exp}_tm{fin_time}'
                self.current_act.append(Mob)
            else:
                key = list(i.keys())
                for i in key:
                    print(f'-- Вход в подземелье {i}')
                    self.current_act.append(f'Вход в подземелье {i}')

        for i in range(len(self.current_act)):
            print(i+1,' ',self.current_act[i])

        if len(self.current_act) == 0:
            return None



        try:
            self.act_num = int(input('Выберите номер действия - ')) - 1
            if (self.act_num + 1) > len(self.current_act):
                return 'Error'
        except Exception:
            print('Вы ввели неверное число!')
            return 'Error'

        return self.current_act[self.act_num]

# Учитывая время и опыт, не забывайте о точности вычислений!

if __name__ == '__main__':
    game = GameDungeon()
    game.Start()
    #TODO допилить проигрыш, протестить все проходы