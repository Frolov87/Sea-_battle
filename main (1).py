from random import randint #"Импортируем для произвольного расположения кораблей и выстрела игрока Компьютер"
# "создаем точки"
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # "Сравниваем точки"
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    # "Выводит точки в консоль"
    def __repr__(self):
        return f"({self.x}, {self.y})"

# "Создаем класс с классами исключений"
class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

# "Создаем класс Корабль"
class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l #"жизнь корабля"
    
    @property
    # "Задаем направление корабля"
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x 
            cur_y = self.bow.y
            
            if self.o == 0:
                cur_x += i
            
            elif self.o == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots

    # "Определяем попадание"
    def shooten(self, shot):
        return shot in self.dots

# "Создаем класс Доска"
class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        
        self.count = 0
        
        self.field = [ ["O"]*size for _ in range(size) ]
        
        self.busy = []
        self.ships = []


    # "Размещаем корабль"
    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # "Обрисовывает контур корабля"
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    # "Рисуем поле"
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"
        
        if self.hid:
            res = res.replace("■", "O")
        return res
    
    def out(self, d):
        return not((0<= d.x < self.size) and (0<= d.y < self.size))

    # "Производим выстрел и проверяем правильность "
    def shot(self, d):
        if self.out(d):
            raise BoardOutException() # "Если выходит за границы"
        
        if d in self.busy:
            raise BoardUsedException()# "Если точка занята"
        
        self.busy.append(d)

        # "Проверяем, принадлежит ли точка кораблю"
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0: #"Если жизни закончились"
                    self.count += 1 #"Добавляем корабль в счетчик уничтоженных"
                    self.contour(ship, verb = True) #"Обводим уничтоженный корабль"
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        
        self.field[d.x][d.y] = "." #"Если выстрел мимо"
        print("Мимо!")
        return False
    
    def begin(self):
        self.busy = []


# "Пишем класс Игрок"
class Player:
    def __init__(self, board, enemy): #"передаем свою доску и доску противника"
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        raise NotImplementedError()

    #"запрос на выстрел"
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

#"Создаем класс игрока Компьютер"
class AI(Player):
    def ask(self):
        d = Dot(randint(0,5), randint(0, 5)) # "Случайно генерируем две точки"
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d
#"Создаем класс игрока"
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            
            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue
            
            x, y = cords
            
            if not(x.isdigit()) or not(y.isdigit()):
                print(" Введите числа! ")
                continue
            
            x, y = int(x), int(y)
            
            return Dot(x-1, y-1)

#"Основной класс игры"
class Game:

    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()# "Случайная доска игрока"
        co = self.random_board()# "Случайная доска компьютера"
        co.hid = True #"Скрываем корабли компьютера"

        
        self.ai = AI(co, pl)
        self.us = User(pl, co)



    # "Выводим рандомные доски"
    #
    def random_place(self):

        lens = [3, 2, 2, 1, 1, 1, 1] #"Список с длинами кораблей"
        board = Board(size = self.size) # "Создаем доску"
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 10000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    # "Правила игры"
    def greet(self):
        print("  ------------------")
        print(" | Приветсвуем вас | ")
        print(" |     в игре      | ")
        print(" |   морской бой   | ")
        print(  "  ------------------")
        print(" Формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
    
    # "Игровой цикл"
    def loop(self):
        num = 0 # "Номер хода"
        while True:
            print("-"*27)
            print("     Доска пользователя:")
            print(self.us.board)
            print("-"*27)
            print("     Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-"*27)
                print(f"Кол-во уничтоженных кораблей соперника: {self.ai.board.count} из 7")
                print(f"Кол-во уничтоженных кораблей игрока: {self.us.board.count} из 7")
                print("Ходит пользователь!")
                repeat = self.us.move() #"метод move отвечающий за ход"
            else:
                print("-"*27)
                print("Ходит компьютер!")
                repeat = self.ai.move() #"метод move отвечающий за ход"
            if repeat:
                num -= 1
            
            if self.ai.board.count == 7:
                print("-"*27)
                print("Пользователь выиграл!")
                break
            
            if self.us.board.count == 7:
                print("-"*27)
                print("Компьютер выиграл!")
                break
            num += 1
            
    def start(self):
        self.greet()
        self.loop()
            
            
g = Game()
g.start()