# -*- coding: utf-8 -*-
'''
Version 2.1
@author:Jake Wills
'''
import Tkinter as tk
import random as rand
import json


class Alien(object):
    def __init__(self):                                         #initialisation d'un alien
        self.id = None
        self.alive = True
    def getId(self):
        return self.id
    def install_in(self, canvas, x, y, image, tag):             #installation de l'alien dans le canvas
        self.id=canvas.create_image(x, y, image=image, tag=tag)
    def move_in(self,canvas, dx, dy):                           #déplacement de l'alien dans le canvas
        canvas.move(self.id, dx, dy)
    def animate_self(self, canvas, image, tag):
            x1,y1,x2,y2=canvas.bbox(self.id)
            canvas.delete(self.id)
            self.id=canvas.create_image((x1+x2)/2, (y2+y1)/2, image=image, tag=tag)
        
class Fleet(object):
    def __init__(self):                                         #initialisation de la flotte
        self.image1= tk.PhotoImage(file="alien.gif", format="gif -index 0")#frame 1 de l'animation alien
        self.image2= tk.PhotoImage(file="alien.gif", format="gif -index 1")#frame 2
        self.explosion= tk.PhotoImage(file="explosion.gif")
        self.aliens_lines = 5
        self.aliens_columns = 10
        self.aliens_inner_gap = 20
        self.alien_x_delta = 5
        self.alien_y_delta = 15
        self.alien_direction = 1
        self.explode = [None] * 8                                     #si une explosion est crée elle est stockée ici
        self.fleet_size = self.aliens_lines * self.aliens_columns
        self.aliens_fleet = [None] * self.fleet_size
        self.frame = 0
        self.fired_bullets = []#liste des projectile alien
        self.max_fired_bullets = 12#maximum 12 projectiles alien
    def getFleet(self):
        return self.aliens_fleet
    def getBullets(self):
        return self.fired_bullets
    def install_in(self,canvas):                                #installation de la flotte dans le canvas
        aliens = 0
        starty = 40
        for i in range(self.aliens_lines):
            startx = 40
            for j in range(self.aliens_columns):
               self.aliens_fleet[aliens]=Alien()
               self.aliens_fleet[aliens].install_in(canvas, startx, starty,self.image1, 'alien')
               startx+=(73+self.aliens_inner_gap)
               aliens+=1
            starty+=(53+self.aliens_inner_gap)
    def animate_fleet(self,canvas):#on passe à la prochaine frame
        if self.frame==0:
            image=self.image2
            self.frame=1
        else:
            image=self.image1
            self.frame=0
        for alien in self.aliens_fleet:#chaque alien va s'animer
            alien.animate_self(canvas, image, "alien")
    def move_in(self, canvas):                               #déplacer toute la flotte dans le canvas
        x1,y1,x2,y2=canvas.bbox('alien')
        if x1<=0:
            canvas.move('alien', 0, self.alien_y_delta)
            self.alien_direction= 1
        if x2>=(int(canvas.cget('width'))):
            canvas.move('alien', 0, self.alien_y_delta)
            self.alien_direction= -1
        canvas.move('alien', self.alien_x_delta*self.alien_direction, 0)
    def manage_touched_aliens_by(self,canvas,defender, scores):         #gérer les alien touchés par un projectile
        for bullet in defender.fired_bullets:
            x1,y1,x2,y2=canvas.bbox(bullet.id)
            alien_dead=canvas.find_overlapping(x1,y1,x2,y2)
            if len(alien_dead)>1 and any(canvas.gettags(unit)==('alien',) for unit in alien_dead):#si plus d'un objet est contenu dans la zone et au moins un des objets est un alien
                for e in alien_dead:
                    if(canvas.gettags(e))==('alien',):# si l'objet est un alien il est supprimé
                        for alien in self.aliens_fleet:
                            if alien.id == e:
                                self.aliens_fleet.remove(alien)
                                scores.add_score()#augmentation du score
                                break
                        canvas.delete(e)
                canvas.delete(bullet.id)#le bullet est supprimé
                defender.fired_bullets.remove(bullet)
                self.explode.append(canvas.create_image(x1, y1, image=self.explosion, tag='explosion'))#creaton d'explosion
    def fleet_fire(self, canvas):
        if len(self.fired_bullets) < self.max_fired_bullets:#si un alien peut tirer
            shooters=rand.choice(self.aliens_fleet)#un alien aléatoire va le faire
            self.fired_bullets.append(Bullet(shooters, "white", self.alien_y_delta, -8, "invader_bullet"))
            self.fired_bullets[-1].install_in(canvas)  
    def manage_bullets(self, canvas, defender):#gestion des bullet alien
        for alien_bullet in self.fired_bullets:
            x1,y1,x2,y2=canvas.bbox(alien_bullet.getId())
            hits=canvas.find_overlapping(x1,y1,x2,y2)
            if len(hits)>1 and any((canvas.gettags(unit)==("defender_bullet",) or canvas.gettags(unit)==("defender",) or canvas.gettags(unit)==("bunker",)) for unit in hits):#si le bullet alien touche un defender ou un bullet defender
                for target in hits:#pour chaque objet si c'est un defender_bullet il est supprimé, si c'est un defender ou bunker il perd une vie
                    if canvas.gettags(target)==("defender_bullet",):#c'est un bullet
                        for defender_bullet in defender.fired_bullets:
                            if defender_bullet.id == target:
                                defender.fired_bullets.remove(defender_bullet)
                                break
                        canvas.delete(target)
                    if canvas.gettags(target)==("defender",):#c'est un defender
                        defender.hit()
                    if canvas.gettags(target)==("bunker",):#c'est un bunker
                        for bunker in defender.bunker_list:
                            if bunker.id == target:
                                bunker.hit(canvas)
                canvas.delete(alien_bullet.id)#à la fin le bullet disparait
                self.fired_bullets.remove(alien_bullet)
                
class Bunker(object):
    def __init__(self):
        self.lives = 3
        self.id = None
        self.image1 = tk.PhotoImage(file="bunker.gif", format="gif -index 0")
        self.image2 = tk.PhotoImage(file="bunker.gif", format="gif -index 1")
        self.image3 = tk.PhotoImage(file="bunker.gif", format="gif -index 2")
        self.image4 = tk.PhotoImage(file="bunker.gif", format="gif -index 3")
    def getId(self):
        return self.id
    def getLives(self):
        return self.lives
    def hit(self, canvas):
        self.lives = self.lives -1
        x1,y1,x2,y2=canvas.bbox(self.id)
        if self.lives == 2:
            canvas.delete(self.id)
            self.id = canvas.create_image((x1+x2)/2, (y2+y1)/2, image=self.image2, tag="bunker")
        if self.lives == 1:
            canvas.delete(self.id)
            self.id = canvas.create_image((x1+x2)/2, (y2+y1)/2, image=self.image3, tag="bunker")
        if self.lives < 1:
            canvas.delete(self.id)
            self.id = canvas.create_image((x1+x2)/2, (y2+y1)/2, image=self.image4, tag="explosion")
    def install_in(self, canvas, posX):
        if self.id != None: return
        posY = (int(canvas.cget('height')))/10*9
        self.id=canvas.create_image(posX, posY, image=self.image1, tag="bunker")

class Defender(object):
    def __init__(self): #defender taille 20x20, se déplace de 20, peut tirer 8 projectiles
        self.width = 20
        self.height = 20
        self.move_delta = 10
        self.id = None
        self.max_fired_bullets = 8
        self.fired_bullets = []
        self.bunker_list = []
        self.lives = 3
        self.lives_display = None
    def getFired(self):
        return self.fired_bullets
    def getId(self):
        return self.id
    def getLives(self):
        return self.lives
    def install_in(self, canvas):
        if self.id != None: return #si defender n'éxiste pas déjà, créer defender
        positionX = int(canvas.cget('width'))/2 + self.width/2 #defender place au centre de la fenêtre
        positionY = int(canvas.cget('height')) - self.height - 10
        self.id = canvas.create_rectangle(positionX, positionY, positionX + self.width, positionY + self.height, fill="white", outline="blue", tag="defender") #stockage de l'id du defender
        for i in range (3):
            self.bunker_list.append(Bunker())
            posX =  (int(canvas.cget("width")))/3
            self.bunker_list[-1].install_in(canvas,i * posX + posX/2)
        self.lives_display = canvas.create_text(int(canvas.cget("width"))-50,int(canvas.cget('height'))-20, text=("Lives:", self.lives), font=("Comic Sans", 10), fill="red", tags="text")
    def move_in(self, canvas, dx):
        canvas.move(self.id, dx, 0)
    def fire(self, canvas):
        if len(self.fired_bullets)<self.max_fired_bullets: #si le nb de projectile < max(8) alors ajouter un projectile sinon rien
            self.fired_bullets.append(Bullet(self, "red", -1*self.height, 8, "defender_bullet"))
            self.fired_bullets[-1].install_in(canvas)
            #for e in canvas.find_withtag("alien"):#nuke --- tuer tout les alien pour tester
                #canvas.delete(e)
    def hit(self):
        self.lives = self.lives - 1

class Bullet(object):
    def __init__(self, shooter, color, offset, speed, tag):#les projectiles sont de rayon 5 avec vitesse 8
        self.radius = 5
        self.color = color
        self.speed = speed
        self.id = None
        self.shooter = shooter
        self.offset = offset
        self.tag=tag
    def getShooter(self):
        return self.shooter
    def getId(self):
        return self.id
    def install_in(self, canvas):
        x1,y1,x2,y2=canvas.bbox(self.shooter.id)
        positionX = (x1 + x2)/2-self.radius/2
        positionY = y2 - self.radius*2 + self.offset
        self.id = canvas.create_oval(positionX, positionY, positionX+self.radius, positionY+self.radius, fill=self.color, tag=self.tag)
    def move_in(self, canvas):
        canvas.move(self.id, 0, self.speed*(-1))

class Score(object):
    def __init__(self):
        self.id = None
        self.alien_value = 100
        self.current_score = 0
    def getCurrent(self):
        return self.current_score
    @classmethod
    def getScore(cls, path):#on recupere le score depuis le fichier passé en parametre
        score_file = open(path, mode="r")
        scores=json.load(score_file)
        score_file.close()
        return scores
    @classmethod
    def saveScore(cls, player, score, path):#on ajoute le couple joueur/score au fichier passé en parametre
        try:
            scores = Score.getScore(path)
        except:
            scores = {}
        score_file = open(path, mode="w")
        if player in scores.keys():#on si le joueur est deja dans le fichier, on ecrit le score seulement si il est meilleur que celui qui est deja present
            if score>scores[player]:
                scores[player]=score
        else:
            scores[player]=score
        json.dump(scores, score_file)
        score_file.close()
    def install_in(self, canvas):
        self.id = canvas.create_text(50,int(canvas.cget('height'))-20, text=("Score", 42069), font=("Comic Sans", 10), fill="red", tags="text")
    def add_score(self):
        self.current_score = self.current_score + self.alien_value

class Game(object):
    def __init__(self, frame):
        self.frame = frame
        self.fleet = Fleet()
        self.defender = Defender()
        self.height = 800
        self.width = 1000
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height, bg="black")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.defender.install_in(self.canvas)
        self.fleet.install_in(self.canvas)
        self.scores = Score()
        self.score_path = "SpaceInvader_scores.json"
        self.scores.install_in(self.canvas)
    def keypress(self, event):
        if event.keysym == 'Left': 
            self.defender.move_in(self.canvas, -30)
        elif event.keysym == 'Right': 
            self.defender.move_in(self.canvas, 30)
        elif event.keysym == 'space':
            self.defender.fire(self.canvas)
    def animation(self):
        if self.canvas.find_withtag("explosion"):                   #si une explosion existe, on la supprime
            for splosion in self.canvas.find_withtag("explosion"):
                self.canvas.delete(splosion)                        #de cette façon l'explosion ne s'affiche que pendant 300ms
        self.move_bullets()                                         #déplacement des projectiles
        self.collisions()                                           #détection de collision
        if(self.canvas.find_withtag("alien")):                      #si il reste au moins un alien déplacer la flotte
            self.move_aliens_fleet()
        else:
            self.canvas.after(300, self.end_game())                 #sinon fin jeu
        self.fleet.fleet_fire(self.canvas)                          #un alien tire
        self.fleet.animate_fleet(self.canvas)                       #animation des alien
        if(self.defender.lives > 0):                       
            self.canvas.after(300, self.animation)
        else:
            self.canvas.after(300, self.end_game())
        self.canvas.itemconfig(self.scores.id, text=("Score:",self.scores.getCurrent()))#mise à jour de l'affichage du score
        self.canvas.itemconfig(self.defender.lives_display, text=("Lives:",self.defender.getLives()))#mise à jour de l'affichage des vies
        self.canvas.tag_raise("invader_bullet")#les bullet des alien sont déssinés par dessus tout
    def end_game(self):
        for e in self.canvas.find_withtag("alien")+self.canvas.find_withtag("invader_bullet")+self.canvas.find_withtag("defender_bullet")+self.canvas.find_withtag("bunker")+self.canvas.find_withtag("defender")+self.canvas.find_withtag("explosion"):
            self.canvas.delete(e)#on cherche tout les éléments de jeu pour les supprimer. je laisse score et vies ca peut etre interessant à voir
        player=tk.StringVar()
        zone_text = tk.Entry(self.frame, bg="green", textvariable=player, font=("Comic Sans",15))
        button = tk.Button(self.frame, text="Submit player name",font=("Comic Sans",15), width=40, command= lambda: self.submitScore(zone_text.get()))
        self.canvas.create_window(int(self.canvas.cget("width"))/2, int(self.canvas.cget("height"))/2-40, window=zone_text, tag="window")
        self.canvas.create_window(int(self.canvas.cget("width"))/2, int(self.canvas.cget("height"))/2, window=button, tag="window")
    def submitScore(self, player):
        windows=self.canvas.find_withtag("window")#on supprime les fenetres d'entrées
        for window in windows:
            self.canvas.delete(window)
        Score.saveScore(player, self.scores.current_score, self.score_path)
        score_list=[]
        score_dict=self.scores.getScore(self.score_path)
        for key in score_dict:
            score_list.append((key, score_dict[key]))
        score_list=sorted(score_list,   key = lambda tup: tup[1], reverse=True)
        self.canvas.create_text(int(self.canvas.cget("width"))/2,40, text=("High Scores"), font=("Comic Sans", 50), fill="green", tags="text")
        deltaY=90
        for tup in score_list:
            self.canvas.create_text(int(self.canvas.cget("width"))/2,20+deltaY, text=(tup[0],tup[1]), font=("Comic Sans", 30), fill="blue", tags="text")
            deltaY = deltaY + 50    
    def start_animation(self):
        self.canvas.after(300, self.animation)
    def move_bullets(self):
        for bullet in self.defender.getFired():
            x1,y1,x2,y2=self.canvas.bbox(bullet.getId())
            if y2<=10:
                self.canvas.delete(bullet.getId())
                self.defender.fired_bullets.remove(bullet)
            else:
                bullet.move_in(self.canvas)
        for bullet in self.fleet.getBullets():
            x1,y1,x2,y2=self.canvas.bbox(bullet.getId())
            if y2>=790:
                self.canvas.delete(bullet.getId())
                self.fleet.fired_bullets.remove(bullet)
            else:
                bullet.move_in(self.canvas)
    def move_aliens_fleet(self):
        self.fleet.move_in(self.canvas)
    def collisions(self):
        self.fleet.manage_touched_aliens_by(self.canvas, self.defender, self.scores)
        self.fleet.manage_bullets(self.canvas, self.defender)

class SpaceInvaders(object):
    '''
    MAIN GAME CLASS
    '''
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        self.frame = tk.Frame(self.root)
        self.frame.pack(side="top", fill="both")
        self.game = Game(self.frame)
    def play(self):
        print("Space Invaders")
        self.root.bind("<Key>", self.game.keypress)
        self.game.start_animation()
        self.root.mainloop()


test=SpaceInvaders()
test.play()

