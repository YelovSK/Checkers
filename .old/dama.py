import tkinter as tk
from tkinter import messagebox, filedialog
from random import choice
from time import time
# verzia bez mandatory capture

class Piece():
    'figurka'
    c = None

    def __init__(self, side, pos, size, king=False):
        self.colour = '#ffffff' if side == 'white' else '#000000'
        self.side = side
        self.king = king
        self.pos = pos
        self.x, self.y = pos
        self.marked = False
        self.size = size
        self.outline = None
        self.circle = self.draw('', self.colour)
        self.check_king()
    
    def draw(self, outline, fill=''):
        x, y, size_r = self.coord()
        return self.c.create_oval(x, y, x+size_r, y+size_r, fill=fill, outline=outline, width=int(size_r * 0.05))

    def mark(self):
        'vykresli štvorec ako oznacenie polia'
        self.outline = self.draw('red')
        self.marked = True

    def unmark(self):
        '''odstrani oznacenie'''
        self.c.delete(self.outline)
        self.marked = False

    def delete(self):
        'odstrania sa tkinter objekty'
        self.c.delete(self.circle)
        if self.king:
            self.c.delete(self.koruna)

    def move(self, x, y):
        'presunie figurku na dane suradnice'
        self.unmark()
        self.c.delete(self.circle)
        if self.king:
            self.c.delete(self.koruna)
        self.x, self.y = x, y
        self.circle = self.draw('', self.colour)

    def check_king(self):
        'skontroluje, ci sa figurka nestala kralom'
        if not self.king:
            if self.side == 'white' and self.y == 0:
                self.king = True
            elif self.side == 'black' and self.y == 7:
                self.king = True
        if self.king:
            c = 'white' if self.side == 'black' else 'black'
            x, y, size_r = self.coord()
            fsize = f'helvetica {int(self.size*0.5)}'
            self.koruna = self.c.create_text(x+size_r/2, y+size_r//2, text='♔', font=fsize, fill=c)

    def coord(self):
        'suradnice pre canvas'
        size_r = self.size * 0.8
        shift = int((self.size - size_r) // 2)
        x, y = self.x*self.size + shift, self.y*self.size + shift
        return (x, y, size_r)
        

class Board():

    def __init__(self, size=500, ai=False):
        self.root = tk.Tk()
        self.root.title("Dama")
        self.root.iconbitmap("icon.ico")
        self.root.resizable(0, 0)
        self.size = size
        self.rect_size = self.size/8
        self.ai = ai
        self.c = Piece.c = tk.Canvas(width=size, height=size, bg="#bcbcbc")
        self.c.pack()
        self.menu_bar()
        self.draw_board()
        self.choose_side()

    def timer(self):
        'pocita cas od zaciatku hry, vypise pri konci'
        if self.do_timer:
            self.time = round(time() - self.start) + self.add
            self.c.after(1000, self.timer)

    def choose_side(self):
        'otvori sa okno s vyberom bielej/ciernej/nahodnej strany'
        def closed():
            self.root.destroy()

        self.side_win = tk.Toplevel()
        self.side_win.title('Choose side')
        self.side_win.iconbitmap('icon.ico')
        self.side_win.attributes('-topmost', True)
        self.side_win.resizable(0, 0)
        self.side_win.geometry('260x110')
        self.side_win.protocol('WM_DELETE_WINDOW', closed)
        label = tk.Label(self.side_win, text='Choose side', font=('Helvetica', int(self.rect_size/3)))
        label.pack()
        self.black = tk.Button(
            self.side_win,
            text="BLACK",
            font=('helvetica', 13), 
            bd=2,
            background='black',
            fg='white',
            activeforeground='#ffffff',
            activebackground='#444444',
            command=lambda: chose_side('black')
        )
        self.white = tk.Button(
            self.side_win,
            text="WHITE",
            font=('helvetica', 13),
            bd=2,
            background='white',
            command=lambda: chose_side('white')
        )
        self.random = tk.Button(
            self.side_win,
            text="RANDOM",
            font=('helvetica', 13),
            bd=2,
            background='gray',
            command=lambda: chose_side('random')
        )
        self.black.place(x=10, y=50)
        self.white.place(x=90, y=50)
        self.random.place(x=165, y=50)

        def chose_side(col):
            if col == 'random':
                self.side = choice(('black', 'white'))
            else:
                self.side = col
            self.side_win.destroy()
            self.place_pieces()
            self.selected = None

        self.side_win.mainloop()

    def menu_bar(self):
        'horna lista s prikazmi'
        self.side, self.highlight_valid = None, []
        self.do_timer, self.add, self.move_side = False, 0, 'black'

        def save():
            if not self.side:
                messagebox.showinfo('Warning', 'Choose a side first')
                return

            save_file = filedialog.asksaveasfile(
                mode='w', initialdir='saves', title='Save game', 
                filetypes=[('Text files', '*.txt')], 
                defaultextension=[('Text files', '*.txt')])

            if not save_file:
                return

            op = 'ai' if self.ai else 'player'
            save_file.write(f'{self.side} {self.time} {op} {self.move_side} ')

            for i in self.board:
                for j in i:
                    if j:
                        k = 'k' if j.king else 'n'
                        save_file.write(f'{j.x}/{j.y}/{j.side}/{k} ')

        def load():
            if not self.side:
                messagebox.showinfo('Warning', 'Choose a side first')
                return

            save_file = filedialog.askopenfilename(
            initialdir='saves', title='Load game', 
            filetypes=[('Text files', '*.txt')])
            if not save_file:
                return

            with open(save_file, 'r') as file:
                line = file.readline().split()

            self.side, self.add = line[0], int(line[1])
            self.ai = True if line[2] == 'ai' else False
            self.move_side = line[3]
            self.c.delete('all')
            self.draw_board()
            self.board = [[None for i in range(8)] for j in range(8)]

            for i in line[4:]:
                x, y, side, king = i.split('/')
                k = True if king == 'k' else False
                self.board[int(x)][int(y)] = Piece(side, (int(x), int(y)), self.rect_size, k)
            if self.ai and self.side != self.move_side:
                self.c.update()
                self.c.after(1000, self.ai_moves())

        def exit():
            if tk.messagebox.askyesno('Exit', 'Do you want to quit the game?'):
                self.root.destroy()

        def restart():  # ak pouzite, tak na konci sa v konzole vypise tkinter.TclError //bug
            if not self.side:
                messagebox.showinfo('Warning', 'Choose a side first')
                return

            self.root.unbind("<ButtonPress-1>")
            self.side = None

            if tk.messagebox.askyesno("Restart", "Do you want to restart the game?"):
                self.move_side = 'black'
                self.highlight_valid = []
                self.c.delete('all')
                self.draw_board()
                self.c.update()
                self.choose_side()
                self.draw_board()
                self.start = time()
                self.place_pieces()

        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        subMenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=subMenu)
        subMenu.add_command(label="Save", command=save)
        subMenu.add_command(label="Load", command=load)
        subMenu.add_command(label="Restart", command=restart)
        subMenu.add_command(label="Exit", command=exit)

    def place_pieces(self):
        'vytvori figurky, ktore vlozi do polia dosky'
        self.board = [[None for i in range(8)] for j in range(8)]
        side = 'black'
        for y in (0, 1, 2, 5, 6, 7):
            if y == 5:
                side = 'white'
            for x in range(1-y%2, 8-y%2, 2):
                self.board[x][y] = (Piece(side, (x, y), self.rect_size))
        self.do_timer = True
        self.start = time()
        self.timer()
        if self.ai and self.side != self.move_side:
            self.c.update()
            self.waiting_for_ai = True
            self.c.after(1000, self.ai_moves())
        self.c.bind_all("<ButtonPress-1>", self.click)

    def draw_board(self):
        'vykresli sa doska'
        self.light, self.dark = '#ffceaf', '#a34911'
        for y in range(8):
            for x in range(8):
                rec_c = self.dark if (x+y) % 2 else self.light
                coords = [y*self.rect_size, x*self.rect_size, y*self.rect_size+self.rect_size, x*self.rect_size+self.rect_size]
                try:
                    self.c.create_rectangle(*coords, fill=rec_c, outline="")
                except:
                    pass

    def ai_moves(self):
        '''najde vsetky legalne tahy a tie ohodnoti
        +1 za kazdu vybitu figurku
        +0.75 ak sa stane kralom
        +(kolko moze oponent vyhodit)*0.5 (chcem aby sa dostal prec)
        -(kolko by oponent mohol vyhodit po skoku)*0.75
        // preferuje vyhodit figurku a potom byt ohrozeny
        // ak ohrozeny, tak preferuje zostat nez pohnut sa a byt znova ohrozeny (vyzera to navonok inteligentnejsie.. asi)'''
        def threatened_num(piece):  # kam skocim, najdem co by ma ohrozovalo, najdem tahy toho co ohrozuje, kolko moze max vybit
            threats = self.threatened(piece)    # figurky, ktore ohrozuju 'piece'
            if threats:
                op_can_take = 0
                for threat in threats:
                    op_moves = self.valid_moves((threat[0], threat[1])) # tahy figurky, ktora ohrozuje 'piece'
                    for op_move in op_moves.values():
                        if op_move and (len(op_move) > op_can_take):
                            op_can_take = len(op_move)
                return op_can_take  # kolko moze oponent najviac vyhodit
            return 0

        ai_side = 'white' if self.side == 'black' else 'black'
        if ai_side != self.move_side:
            return

        ai_pieces = [piece for line in self.board for piece in line if (piece and piece.side == ai_side)]
        moves = []

        for piece in ai_pieces:
            move = self.valid_moves((piece.x, piece.y), False)
            # tvar move -> {(kam_1.x, kam_1.y): vyhodi1, (kam_2.x, kam_2.y): vyhodi1, vyhodi2}
            if move:
                for key, value in move.items():
                    goes_from = self.board[piece.x][piece.y]
                    score = 0 if not value else len(value)
                    score += threatened_num(piece)*0.5
                    
                    if key[1] == 7 and goes_from.side == 'black' and not goes_from.king:
                        score += 0.75
                    elif key[1] == 0 and goes_from.side == 'white' and not goes_from.king:
                        score += 0.75

                    self.board[key[0]][key[1]] = Piece(goes_from.side, (key[0], key[1]), self.rect_size, goes_from.king)
                    self.board[piece.x][piece.y] = None
                    if value:
                        for remove in value:
                            self.board[remove.x][remove.y] = None
                    # ^^ docasne upravene rozmiestnenie figurok (pre kroky dopredu)
                    score -= threatened_num(self.board[key[0]][key[1]]) * 0.75
                    self.board[key[0]][key[1]].delete()
                    self.board[piece.x][piece.y] = goes_from
                    self.board[key[0]][key[1]] = None
                    if value:
                        for remove in value:
                            self.board[remove.x][remove.y] = remove
                    # ^^ rozmiestnenie sa vratilo
                    moves.append(((piece.x, piece.y), key, score, value)) # (from.x, from.y), (to.x, to.y), score

        for move in moves:
            takes = ''
            if move[3]:
                for i in move[3]:
                    takes += f'({i.x}, {i.y}) '
            else:
                takes = 'None'
            print(f'From: {move[0]} | To: {move[1]} | Score: {move[2]} | Takes: {takes}')
        print('-'*50)

        if not moves:
            messagebox.showinfo('Game finished', f'{self.side.capitalize()} won in {self.time} seconds!')
            return

        best, scores, max = [], [], -10
        for move in moves:
            if move[2] > max:
                best = []
                scores.append(move[2])
                max = move[2]
                best.append((move[0], move[1], move[3]))
            elif move[2] == max:
                best.append((move[0], move[1], move[3]))
        go_make_king = True

        for i, score in enumerate(scores):
            if score != 0:
                go_make_king = False
                break

        best_choice = None
        if go_make_king:    # ak nie je dobry tah, tak chod s pesiakom spravit krala
            for move in best:
                pom = self.board[move[0][0]][move[0][1]]
                if not pom.king:
                    best_choice = ((move[0], move[1], move[2]))
                    break
        if not best_choice:
            best_choice = choice(best)
            pom = self.board[best_choice[0][0]][best_choice[0][1]]

        pom.move(*best_choice[1])
        self.board[best_choice[0][0]][best_choice[0][1]] = None
        self.board[best_choice[1][0]][best_choice[1][1]] = pom
        pom.check_king()

        if best_choice[2]:
            for rem in best_choice[2]:
                self.board[rem.x][rem.y] = None
                rem.delete()
                del rem

        self.move_side = 'black' if self.move_side == 'white' else 'white'
        for highlight in self.highlight_valid:
            self.c.delete(highlight)

    def click(self, event):
        'stara sa o klikanie myšou (oznacenie, odznacenie, spravenie tahu, AI spravi dalsi tah)'
        field = self.field_index(event.x, event.y)
        if not field:
            return
        elif self.ai and (self.side != self.move_side):
            return

        for highlight in self.highlight_valid:
            self.c.delete(highlight)

        if type(field) == tuple:
            x, y = field
            field = None
        else:
            x, y = field.x, field.y

        if self.selected:
            if (x, y) in self.moves.keys():     # odstrania sa vyznacene tahy
                remove = self.moves[(x, y)]
                if remove:
                    for rem in remove:
                        self.board[rem.x][rem.y] = None
                        rem.delete()
                        del rem
                self.board[self.selected.x][self.selected.y] = None
                self.selected.move(x, y)
                self.selected.check_king()
                self.board[x][y] = self.selected
                self.move_side = 'black' if self.move_side == 'white' else 'white'
                if self.ai:
                    self.c.update()
                    self.c.after(500, self.ai_moves())
                if self.check_win():
                    self.root.unbind("<ButtonPress-1>")
                    messagebox.showinfo('Game finished', f'{self.check_win()} won in {self.time} seconds!')
                    self.do_timer = False
                    return
            elif field:
                self.selected.unmark()
                self.selected = field
                field.mark()
            self.selected.unmark()
            self.selected = None
        elif field and field.side == self.move_side:
            field.mark()
            self.moves = self.valid_moves((x, y))   # oznacene tahy
            self.selected = field

    def valid(self, selected, field):
        'zisti, ci je tah z policka na policko validny'
        if field[0] < 0 or field[0] > 7 or field[1] < 0 or field[1] > 7:
            return False

        if self.board[field[0]][field[1]]: # klikol som na obsadene
            return False
        else:
            x, y = field
            if not (x+y) % 2:   # klikol som na svetle
                return False

        if selected.result == 'black':
            if selected.y == 7 and not selected.king:
                return False
            shift = (1,)
        else:
            if selected.y == 0 and not selected.king:
                return False
            shift = (-1,)
        if selected.king:
            shift = (-1, 1)

        for i in (-1, 1):
            for j in shift:
                if y-j == selected.y and x+i == selected.x: # klikol som na prazdne v okolí 1
                    return (x, y)

        def between_coords(axis): # poličko v strede 2 policok
            a = selected.x if axis == 'x' else selected.y
            b = x if axis == 'x' else y
            return int(a+((b-a)//2))

        piece = self.board[between_coords('x')][between_coords('y')]
        threatened = self.threatened(piece)

        if not threatened:    # Piece medzi mnou a prazdnym nie je ohrozena
            return False

        if (selected.x, selected.y) in threatened:    # ak moja Piece ohrozovala figurku medzi
            return (x, y), piece

    def valid_moves(self, field, highlight=True):
        'vrati vsetky mozne tahy figurky (aj s preskakovanim)'
        field = self.board[field[0]][field[1]]
        moves = {}
        for i in (-1, 1):
            for j in (-1, 1):
                move = self.valid(field, (field.x+i, field.y+j))
                if move:
                    moves[move] = None

        def long_jump(field, prev=[]):  # rekurzivne najde tahy a vyhodene figurky 
            # ak mozem ist na pole viacerymi cestami, tak to nemusi nevybrat najlepsiu (najviac vyhodenych) //bug
            for i in (-2, 2):
                for j in (-2, 2):
                    if not field:
                        pass
                    else:
                        move = self.valid(field, (field.x + i, field.y + j))
                        if move:
                            x, y = move[0][0], move[0][1]
                            moves[move[0]] = [move[1]]+prev
                            pom = self.board[x][y] = Piece(field.result, (x, y), self.rect_size, field.king)
                            long_jump(pom, prev+[move[1]])  # ak mozem skocit: pridaj tah a ci mozem z toho noveho dalej skocit
                            pom.delete()
                            del pom
                            self.board[x][y] = None

        long_jump(field)

        for move in moves.keys():
            x, y = move
            x *= self.rect_size
            y *= self.rect_size
            if highlight:
                self.highlight_valid.append(self.c.create_rectangle(
                        x, y, x+self.rect_size, y+self.rect_size, 
                        fill='', outline='red', width=3))

        return moves
            
    def field_index(self, x, y):
        'vrati index polia zo suradnic mysi'
        x, y = int(x // self.rect_size), int(y // self.rect_size)
        if x == 8 or y == 8:
            return False
        if self.board[x][y]:
            return self.board[x][y]
        else:
            return (x, y)

    def threatened(self, piece):
        'vrati figurky, ktoe ohrozuju figurku (iba okolo +-1)'
        if not piece:
            return False
        x, y = piece.x, piece.y
        if x in (0, 7) or y in (0, 7):
            return False
        opponent = 'white' if piece.result == 'black' else 'black'
        out = []
        for i in (-1, 1):
            for j in (-1, 1):
                op = self.board[x+i][y+j]  # ten co ohrozuje
                if op and op.side == opponent and not self.board[x-i][y-j]:   # ci je prazdny na druhej strane
                    if not op.king:
                        if not (piece.result == 'white' and op.y > piece.y) and not (piece.result == 'black' and op.y < piece.y):
                            out.append((x+i, y+j))
                    else:
                        out.append((x+i, y+j))   # coords toho co ohrozuje
        if out == []:
            return False
        return out

    def check_win(self):
        'kontroluje, ci strane zostali figurky'
        b, w = 0, 0
        for i in self.board:
            for j in i:
                if j:
                    if j.side == 'white':
                        w += 1
                    else:
                        b += 1
        if not b: return 'White' 
        elif not w: return 'Black'
        return False


game = Board(size=600, ai=True)