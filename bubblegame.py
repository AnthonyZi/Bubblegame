import tkinter as tk
from tkinter import ttk
import time
import threading
import random
import math
import pickle
from PIL import Image,ImageTk

class Entity(object):
    def __init__(self, canvas, width, cor_x, cor_y, orientation, velocity):
        self.canvas = canvas
        self.width = width
        self.cor_x = cor_x
        self.cor_y = cor_y
        self.velocity = velocity
        self.orientation = orientation

        self.entity = self.canvas.create_oval(cor_x-self.width/2,cor_y-self.width/2,cor_x+self.width/2,cor_y+self.width/2, fill="blue")

    def move(self):
        d_x = math.cos(self.orientation)*(self.velocity)
        d_y = math.sin(self.orientation)*(self.velocity)
        self.cor_x += d_x
        self.cor_y += d_y
#        self.canvas.move(self.entity,d_x,d_y)
#        coords = self.canvas.coords(self.entity)
#        if len(coords) == 4:
#            self.cor_x = (coords[0]+coords[2])/2
#            self.cor_y = (coords[1]+coords[3])/2

class Player(object):
    def __init__(self, canvas, width, cor_x, cor_y):
        self.canvas = canvas
        self.width = width
        self.cor_x = cor_x
        self.cor_y = cor_y
        self.cor_x_start = cor_x
        self.cor_y_start = cor_y

        self.entity = self.canvas.create_oval(cor_x-self.width/2,cor_y-self.width/2,cor_x+self.width/2,cor_y+self.width/2, fill="green")

        self.points = 0

        self.player_drag = False

        self.canvas.bind("<Motion>", self.mouse_move_callback)
        self.canvas.bind("<Button-1>", self.mouse_click_callback)

    def mouse_move_callback(self,event):
        if self.player_drag:
            self.cor_x = event.x
            self.cor_y = event.y
            x0,x1 = self.cor_x-self.width/2,self.cor_x+self.width/2
            y0,y1 = self.cor_y-self.width/2,self.cor_y+self.width/2
            self.canvas.coords(self.entity,x0,y0,x1,y1)

    def mouse_click_callback(self,event):
        dist = math.hypot(event.x-self.cor_x,event.y-self.cor_y)
        if dist < self.width:
            self.player_drag = not self.player_drag

class Food(object):
    def __init__(self, canvas, width, cor_x, cor_y, account):
        self.canvas = canvas
        self.width = width
        self.cor_x = cor_x
        self.cor_y = cor_y
        self.account = account

        self.entity = self.canvas.create_oval(cor_x-self.width/2,cor_y-self.width/2,cor_x+self.width/2,cor_y+self.width/2, fill="yellow")


class GameCanvas(threading.Thread):
    def __init__(self,game, width, height):
        super().__init__()
        self.game = game
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self.game.root, width=self.width, height=self.height, borderwidth=0, highlightthickness=0, bg="#DDD")
        self.canvas.grid(row=0, column=1, padx=10, pady=10)

        self.player_width = 30
        self.entity_width = 30
        self.food_width = 20
        self.update_rate = 40 #fps
        self.entities = []
        self.food = []

        self.entity_collisions = []
        self.wall_x_collisions = []
        self.wall_y_collisions = []

        self.pause = True
        self.player = Player(self.canvas, self.player_width, self.width-100, self.height-100)

        self.number_food = 10
        self.food_reduce_counter_value = 5
        self.number_entities = 0

    def get_entity_start_pos(self,num):
        middle_x, middle_y = self.width/2, self.height/2

        #offset in x-direction
        num_entities_per_row = self.number_entities
        while 1.5*num_entities_per_row*self.entity_width > self.width:
            num_entities_per_row = int(num_entities_per_row/2)

        offset_x = -1.5*num_entities_per_row/2
        offset_x += 1.5*(num%num_entities_per_row)
        offset_x *= self.entity_width

        #offset in y-direction
        num_entities_per_col = self.number_entities/num_entities_per_row
        if self.number_entities%num_entities_per_row > 0:
            num_entities_per_col += 1

        offset_y = -1.5*num_entities_per_col/2
        offset_y += 1.5*int(num/num_entities_per_row)
        offset_y *= self.entity_width

        return middle_x+offset_x,middle_y+offset_y

    def clear_game(self,number_entities):
        self.canvas.delete("all")
        self.number_entities = number_entities
        self.game.label_score_string_var.set("0 Points")
        self.entities = []
        self.food = []

        self.entity_collisions = []
        self.wall_x_collisions = []
        self.wall_y_collisions = []

        for i in range(self.number_entities):
            cor_x,cor_y = self.get_entity_start_pos(i)
            entity = Entity(self.canvas, self.entity_width, cor_x, cor_y, random.random()*math.pi, (random.random()*100+50)/self.update_rate)
#            entity = Entity(self.canvas, self.entity_width, cor_x, cor_y, 0, (50)/self.update_rate)
#            entity = Entity(self.canvas, self.entity_width, cor_x, cor_y, 0, 50/self.update_rate)
            self.entities.append(entity)

        self.player = Player(self.canvas, self.player_width, self.width-100, self.height-100)

        for i in range(self.number_food):
            cor_x = random.randint(self.food_width/2,self.width-self.food_width/2)
            cor_y = random.randint(self.food_width/2,self.height-self.food_width/2)
            f = Food(self.canvas, self.food_width, cor_x, cor_y, int(10+self.number_entities))
            self.food.append(f)

        self.pause = False
        self.food_reduce_counter = self.food_reduce_counter_value
        self.canvas.update()
        time.sleep(2)

    def run(self):
        current_update_wait_time = 1/self.update_rate
#        current_game_time = time.time()
#        step_time = 1/self.update_rate
        while True:
            while self.pause:
                time.sleep(1)

            loop_start_time = time.time()

#            frames = 0
#            while current_game_time < time.time() and frames < 5:
##                print(time.time()-current_game_time)
#                current_game_time += step_time
#                frames += 1

            to_remove = []
            for c1_i,c2_i in self.entity_collisions:
                d_e_x = self.entities[c1_i].cor_x - self.entities[c2_i].cor_x
                d_e_y = self.entities[c1_i].cor_y - self.entities[c2_i].cor_y
                distance = math.hypot(d_e_x,d_e_y)
                min_distance = (self.entities[c1_i].width + self.entities[c2_i].width + self.entities[c1_i].velocity + self.entities[c2_i].velocity)/2
                if distance > min_distance:
                    to_remove.append([c1_i,c2_i])
            for r in to_remove:
                self.entity_collisions.remove(r)


            to_remove = []
            for e_i in self.wall_x_collisions:
                e = self.entities[e_i]
                if e.cor_x > e.width/2 or e1.cor_x < self.width-e1.width/2:
                    to_remove.append(e_i)
            for r in to_remove:
                self.wall_x_collisions.remove(r)

            to_remove = []
            for e_i in self.wall_y_collisions:
                e = self.entities[e_i]
                if e.cor_y > e.width/2 or e1.cor_y < self.height-e1.width/2:
                    to_remove.append(e_i)
            for r in to_remove:
                self.wall_y_collisions.remove(r)

            collision_set = set(self.wall_x_collisions + self.wall_y_collisions + [c[0] for c in self.entity_collisions] + [c[1] for c in self.entity_collisions])

            for e_i,e in enumerate(self.entities):
                e.move()
#                if not e_i in collision_set:
#                    self.canvas.itemconfigure(e.entity,fill="blue")


            for e1_i,e1 in enumerate(self.entities):
                for e2_i in range(e1_i+1,len(self.entities)):
                    e2 = self.entities[e2_i]
                    if not [e1_i,e2_i] in self.entity_collisions:
                        d_e_x = e1.cor_x - e2.cor_x
                        d_e_y = e1.cor_y - e2.cor_y
                        distance = math.hypot(d_e_x,d_e_y)
                        min_distance = (e1.width + e2.width + e1.velocity + e2.velocity)/2
                        if distance < min_distance:
#                            self.canvas.itemconfigure(e1.entity,fill="red")
#                            self.canvas.itemconfigure(e2.entity,fill="red")

                            bounce_orientation_e1 = math.atan2(e2.cor_y-e1.cor_y,e2.cor_x-e1.cor_x)
                            bounce_orientation_e2 = bounce_orientation_e1 + math.pi

                            orientation_difference_e1 = bounce_orientation_e1 - e1.orientation
                            orientation_difference_e2 = bounce_orientation_e2 - e2.orientation

                            orthogonal_e1 = math.sin(orientation_difference_e1)*e1.velocity
                            orthogonal_e2 = math.sin(orientation_difference_e2)*e2.velocity

                            bounce_e1 = math.cos(orientation_difference_e2)*e2.velocity
                            bounce_e2 = math.cos(orientation_difference_e1)*e1.velocity

                            e1_x_orthogonal = math.cos(bounce_orientation_e1+math.pi/2)*orthogonal_e1
                            e1_y_orthogonal = math.sin(bounce_orientation_e1+math.pi/2)*orthogonal_e1
                            e1_x_bounce = -1*math.cos(bounce_orientation_e1)*bounce_e1
                            e1_y_bounce = -1*math.sin(bounce_orientation_e1)*bounce_e1
                            e1_x = e1_x_orthogonal + e1_x_bounce
                            e1_y = e1_y_orthogonal + e1_y_bounce
                            e1.orientation = math.atan2(e1_y,e1_x)
                            e1.velocity = math.hypot(e1_x,e1_y)

                            e2_x_orthogonal = math.cos(bounce_orientation_e2+math.pi/2)*orthogonal_e2
                            e2_y_orthogonal = math.sin(bounce_orientation_e2+math.pi/2)*orthogonal_e2
                            e2_x_bounce = -1*math.cos(bounce_orientation_e2)*bounce_e2
                            e2_y_bounce = -1*math.sin(bounce_orientation_e2)*bounce_e2
                            e2_x = e2_x_orthogonal + e2_x_bounce
                            e2_y = e2_y_orthogonal + e2_y_bounce
                            e2.orientation = math.atan2(e2_y,e2_x)
                            e2.velocity = math.hypot(e2_x,e2_y)

                            self.entity_collisions.append([e1_i,e2_i])

                if e1.cor_x < e1.width/2 or e1.cor_x > self.width-e1.width/2:
#                    self.canvas.itemconfigure(e1.entity,fill="red")
                    e1_x = math.cos(e1.orientation)*e1.velocity
                    e1_y = math.sin(e1.orientation)*e1.velocity
                    e1_x *= -1
                    e1.orientation = math.atan2(e1_y,e1_x)
                    e1.velocity = math.hypot(e1_x,e1_y)
                    self.wall_x_collisions.append(e1_i)
                if e1.cor_y < e1.width/2 or e1.cor_y > self.height-e1.width/2:
#                    self.canvas.itemconfigure(e1.entity,fill="red")
                    e1_x = math.cos(e1.orientation)*e1.velocity
                    e1_y = math.sin(e1.orientation)*e1.velocity
                    e1_y *= -1
                    e1.orientation = math.atan2(e1_y,e1_x)
                    e1.velocity = math.hypot(e1_x,e1_y)
                    self.wall_y_collisions.append(e1_i)

                d_e_x = e1.cor_x - self.player.cor_x
                d_e_y = e1.cor_y - self.player.cor_y
                distance = math.hypot(d_e_x,d_e_y)
                min_distance = e1.width/2 + self.player.width/2
                if distance < min_distance:
                    self.canvas.itemconfigure(self.player.entity, fill="red")
                    self.pause = True
                    self.game.game_end_callback("loose")

            to_remove = []
            for f in self.food:
                distance = math.hypot(self.player.cor_x-f.cor_x,self.player.cor_y-f.cor_y)
                min_distance = self.player.width/2 + f.width/2
                if distance < min_distance:
                    self.player.points += f.account
                    self.game.label_score_string_var.set("{} Points".format(self.player.points))
                    to_remove.append(f)
                    if self.food_reduce_counter > 0:
                        cor_x = random.randint(self.food_width/2,self.width-self.food_width/2)
                        cor_y = random.randint(self.food_width/2,self.height-self.food_width/2)
                        f_new = Food(self.canvas, self.food_width, cor_x, cor_y, int(10+self.number_entities))
                        self.food.append(f_new)
                    else:
                        self.food_reduce_counter = self.food_reduce_counter_value
                    self.food_reduce_counter -= 1

            for f in to_remove:
                self.canvas.delete(f.entity)
                self.food.remove(f)


            if self.player.cor_x < self.player.width/2 \
            or self.player.cor_x > self.width-self.player.width/2 \
            or self.player.cor_y < self.player.width/2 \
            or self.player.cor_y > self.height-self.player.width/2:
                self.canvas.itemconfigure(self.player.entity, fill="red")
                self.pause = True
                self.game.game_end_callback("loose")

            if len(self.food) == 0:
                self.pause = True
                self.game.game_end_callback("win")


            # actually move the entities
            for e in self.entities:
                self.canvas.coords(e.entity, e.cor_x-e.width/2,e.cor_y-e.width/2,e.cor_x+e.width/2,e.cor_y+e.width/2)

            self.canvas.update()
            time.sleep(current_update_wait_time)
            loop_end_time = time.time()

            if loop_end_time-loop_start_time > 1/self.update_rate:
                current_update_wait_time *= 0.95
            else:
                current_update_wait_time *= 1.05
#            print("current_update_wait_time",current_update_wait_time)





class Game(object):
    def __init__(self,width,height):
        self.width = width
        self.height = height

        self.root = tk.Tk()
        self.root.config(background = "white")

        self.left_frame = tk.Frame(self.root,width=200,height=self.height, bg="#F5F5F5")
        self.left_frame.grid(row=0,column=0,padx=10,pady=10)

        self.slider_level= tk.Scale(self.left_frame, from_=1, to=8, resolution=1, orient=tk.HORIZONTAL, length=160)
        self.slider_level.grid(row=0, column=0, padx=5, pady=5)

        self.entry_playername = tk.Entry(self.left_frame, width=20)
        self.entry_playername.insert(0,"Playername")
        self.entry_playername.grid(row=1, column=0, padx=5, pady=5)
        self.entry_playername.bind("<Key>", self.entry_playername_callback)

        self.button_start_game = tk.Button(self.left_frame, text="Start Game", bg="#00F0FF", width=20, font="Monospace", command=self.button_start_new_game)
        self.button_start_game.grid(row=2, column=0, padx=5, pady=5)

        self.label_score_string_var = tk.StringVar()
        self.label_score_string_var.set("0 Points")
        self.label_points = tk.Label(self.left_frame, textvariable = self.label_score_string_var, font="Monospace", bg="#F5F5F5")
        self.label_points.grid(row=3, column=0, padx=5, pady=5)

        self.load_leader_board()
        self.label_leader_board_string_var = tk.StringVar()
        self.label_leader_board_string_var.set(self.get_leader_board_string())
        self.label_leader_board = tk.Label(self.left_frame, textvariable = self.label_leader_board_string_var, font="Monospace", bg="#F5F5F5")
        self.label_leader_board.grid(row=4, column=0, padx=5, pady=5)


        self.load_game_stats()
        self.frame_trophys = tk.Frame(self.left_frame, width=180, height=400, bg="#F0F0F0")
        self.frame_trophys.grid(row=5, column=0, padx=5, pady=5)
        self.frame_trophys_indices = [(0,0),(0,1),(1,0),(1,1),(2,0),(2,1),(3,0),(3,1)]
        self.labels_trophy_images = []
        self.photoimage_trophy_placeholder = self.get_photoimage_fixed("Padlock.png",(80,80))
        for ind in self.frame_trophys_indices:
            iy,ix = ind
            lab = tk.Label(self.frame_trophys, image=self.photoimage_trophy_placeholder)
            lab.image = self.photoimage_trophy_placeholder
            lab.grid(row=iy,column=ix,padx=5,pady=5)
            self.labels_trophy_images.append(lab)

        self.playerstats = dict()
        self.playerstats["trophys"] = []

        self.trophy_images = ["frog.png","Snowman.png","Reindeer.png","donkey.png","Duck.png","Lion.png","wulf.png","Dragon.png"]

        self.game_canvas = GameCanvas(self, self.width-200,self.height)
        self.game_canvas.start()

        self.root.wm_title("BubbleGame")
        self.root.mainloop()

    def button_start_new_game(self):
        number_entities = self.slider_level.get()*20
        self.game_canvas.clear_game(number_entities)
        self.game_start_time = time.time()

    def get_photoimage_fixed(self,filename,size):
        img = Image.open(filename)
        img = img.resize(size)
        photo = ImageTk.PhotoImage(img)
        return photo

    def load_leader_board(self):
        try:
            with open("bubblegame.leaderboard", "rb") as f:
                self.leader_board = pickle.load(f)
        except IOError as e:
            self.leader_board = []

    def save_leader_board(self):
        with open("bubblegame.leaderboard", "wb") as f:
            pickle.dump(self.leader_board, f)

    def get_leader_board_string(self):
        out = ""
        for entry_i,entry in enumerate(self.leader_board):
            playername,score = entry
            out += "{}  {: <10}  {}\n".format(str(entry_i+1).zfill(2),playername,str(score).zfill(6))
        return out

    def load_game_stats(self):
        try:
            with open("bubblegame.gamestats","rb") as f:
                self.game_stats = pickle.load(f)
        except IOError as e:
            self.game_stats = dict()

    def save_game_stats(self):
        with open("bubblegame.gamestats", "wb") as f:
            pickle.dump(self.game_stats, f)

    def entry_playername_callback(self,event):
        playername = "{}{}".format(self.entry_playername.get(),event.char)
        if playername in self.game_stats.keys():
            self.playerstats = self.game_stats[playername]
        else:
            self.playerstats = dict()
            self.playerstats["trophys"] = []
        self.update_trophys(playername)

    def update_trophys(self,playername=None):
        if playername == None:
            playername = self.entry_playername.get()
        for trophy_id in range(len(self.trophy_images)):
            if trophy_id in self.playerstats["trophys"]:
                trophy_photo = self.get_photoimage_fixed(self.trophy_images[trophy_id],(80,80))
            else:
                trophy_photo = self.photoimage_trophy_placeholder
            self.labels_trophy_images[trophy_id].configure(image=trophy_photo)
            self.labels_trophy_images[trophy_id].image = trophy_photo

    def game_end_callback(self,end_type):
        playername = self.entry_playername.get()
        if end_type == "loose":
            score = int(self.label_score_string_var.get().split(" ")[0])
        if end_type == "win":
            score = int(self.label_score_string_var.get().split(" ")[0])
            game_time = time.time()-self.game_start_time
            extra_points = int((self.game_canvas.number_entities**2)*300/game_time)
            self.label_score_string_var.set("{} Points\n{} Timebonus".format(score,extra_points))
            score += extra_points
            self.playerstats["trophys"].append(self.slider_level.get()-1)
            self.game_stats[playername] = self.playerstats
            self.update_trophys()

        self.leader_board.append((playername,score))
        self.leader_board.sort(key=lambda x:x[1])
        self.leader_board = self.leader_board[-10:]
        self.leader_board = self.leader_board[::-1]
        self.save_leader_board()
        self.save_game_stats()
        self.label_leader_board_string_var.set(self.get_leader_board_string())


if __name__ == "__main__":

    game = Game(1500,800)

#
#while True:
#    for i in range(1,number_entities):
#        canvas.itemconfigure(entity_list[i],fill="red")
#        canvas.itemconfigure(entity_list[i-1],fill="")
#        canvas.update()
#        time.sleep(0.1)
#    for i in range(1,number_entities):
#        j = number_entities-1-i
#        canvas.itemconfigure(entity_list[j],fill="red")
#        canvas.itemconfigure(entity_list[j+1],fill="")
#        canvas.update()
#        time.sleep(0.1)
