'''Snake game.
20/04/2020
Last Edited : 27/04/2020
author = Andrei '''

#Import the libraries :

import pygame
import random
import time
import os

pygame.init()
'''Set up the main window and it's properties'''
WIDTH = 512
HEIGHT = 608
pygame.display.set_caption('snek')
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.font.init()

ORANGE = pygame.image.load(os.path.join('imgs','orange.png'))

main_font = pygame.font.SysFont('arial', 40)
lost_font = pygame.font.SysFont('arial', 70)
lost_label = lost_font.render('You lose!',1 ,(255,255,255))

'''Set up the squares'''
color_square1= (48, 176, 105)
color_square2=(88, 191, 82)

class Square:
	def __init__(self, x, y, direction = ''):
		self.x = x
		self.y = y
		self.direction = direction #this will be the last direction the head snake had when passing through the square
	
	def draw(self, window, color_square):
		pygame.draw.rect(window,(color_square),(self.x,self.y, 32, 32))

	def empty(self, snake_head, snake_bodies): #check if square is empty. Will be needed to add the food, but also to train the algorithm
		if snake_head.x == self.x and snake_head.y == self.y:
			return False
		else:	
			for snake_body in snake_bodies:
				if snake_body.x == self.x and snake_body.y == self.y:
					return False
		return True


'''A method to set the direction instruction of the square = to the direction the snake head last had when passinig through it'''
def set_square_direction(squares, snake):
	for sq in squares:
	    if snake.x ==sq.x and snake.y ==sq.y: 
	        sq.direction = snake.direction


'''A method to pass the square direction to the snake body'''
def pass_to_snake(squares, snake):
	for sq in squares:
	    if snake.x == sq.x and snake.y == sq.y: 
	        snake.direction = sq.direction



'''Set up the Board'''
def draw_board(window):

	squares=[]
	for i in range(0,16):
		for j in range(2,19):
			sq = Square(i*32, j*32)
			squares.append(sq)

	c = 0 #use this variable to alternate between square colors
	for sq in squares:
		if c ==0:
			sq.draw(window, color_square1)
			c=1
		else:
			sq.draw(window, color_square2)
			c=0

	for sq in squares:
		if sq.y == 2*32:
			pygame.draw.rect(window, (86, 83, 237), (sq.x, sq.y, 32, 32))
			squares.remove(sq)
	return squares


'''Set up a snake class'''
class Snake_Head:
	COOLDOWN = 6
	def __init__(self, x, y, direction):
		self.x = x
		self.y = y
		self.cool_down_counter = 0
		self.direction = direction

	def draw(self, window):
		pygame.draw.rect(window, (255,255,255), (self.x, self.y, 31, 31))

	# the snake moves to the next square according to its direction
	def move(self, squares):
		self.cooldown()
		if self.cool_down_counter == 0:  
			if self.direction == 'up':
				self.y -= 32
			elif self.direction == 'down':
				self.y += 32
			elif self.direction == 'right':
				self.x += 32
			elif self.direction == 'left':
				self.x -= 32


	#the cooldown function sets how quickly the snake moves			
	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter >= 0: 
			self.cool_down_counter += 1


#class for the snake body which follows the snake head
class Snake_Body:
	COOLDOWN = 6

	def __init__(self, x, y, direction = ''):
		self.x = x
		self.y = y
		self.cool_down_counter = 0
		self.direction = direction
		self.x_old = x
		self.y_old = y
		

	def set_self_direction(self, squares):
		for sq in squares:
			if self.x == sq.x and self.y == sq.y: 
				self.direction = sq.direction
				self.square = sq

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN:
			self.cool_down_counter = 0
		elif self.cool_down_counter >= 0: 
			self.cool_down_counter += 1

	def move(self,squares, snake_head, snake_bodies):
		self.set_self_direction(squares)
		self.cooldown()
		if self.cool_down_counter == 0:  
			if self.direction == 'up':
				if Square(self.x, self.y -32).empty(snake_head, snake_bodies):
					self.y_old = self.y #this is needed to move the snake by remembering the path the snake is taking
					self.x_old = self.x
					self.y -= 32
			elif self.direction == 'down':
				if Square(self.x, self.y +32).empty(snake_head, snake_bodies):
					self.y_old = self.y
					self.x_old = self.x
					self.y += 32
			elif self.direction == 'right':
				if Square(self.x +32, self.y).empty(snake_head, snake_bodies):
					self.x_old = self.x
					self.y_old = self.y
					self.x += 32
			elif self.direction == 'left':
				if Square(self.x -32, self.y).empty(snake_head, snake_bodies):
					self.x_old = self.x
					self.y_old = self.y
					self.x -= 32

	def draw(self, window):
		pygame.draw.rect(window, (4, 71, 32), (self.x, self.y, 31, 31))

# the purpose of this class is avoiding collision issues between the head and the first body object, while keeping the snake appearence smooth
class Snake_Head_Extension(Snake_Body): 
		#Define Player's class own initialization method
	def __init__(self, x, y, direction):
		#Inherit initialization from the superclass
		super().__init__(x, y, direction)


class Food():
	def __init__(self):
		self.x=0
		self.y=0
	def draw(self, window):
		window.blit(ORANGE, (self.x,self.y))

	def add_food(self, squares, snake_head, snake_bodies, snake_head_extension):
		x=[] # initalize lists which will append all empty squares  
		y=[]
		#the line below is required to avoid spawning food in the head's extension square, becauase this object makes the square register as empty
		for sq in squares:
			if snake_head_extension.x != sq.x and snake_head_extension.y != sq.y: 
				'''because the snake body is constantly moving, for a split second the squares are empty; so wait for 1/20th of a sec and check again'''
				if sq.empty(snake_head, snake_bodies): #check for empty squares
					x.append(sq.x)
					y.append(sq.y)
		
		self.x = random.choice(x) #assign random coordinates for the food object from the list of empty squares
		self.y = random.choice(y)




def main():
	#Set up the game's FPS
	FPS = 60
	clock = pygame.time.Clock()
	
	directions = ['down','left','right','up']
	#when the game starts, pick a random direction:
	direction=random.choice(directions)
	#initialize the snake head object and start in the middle of the screen:
	snake_head = Snake_Head(WIDTH/2,WIDTH/2 +64, direction)
	#create a list to store the snake's body and append the first block
	squares = draw_board(win)
	snake_bodies = []

	#create the extension
	extension = Snake_Head_Extension(snake_head.x, snake_head.y, snake_head.direction)
	
	snake_head.move(squares)
	extension.draw(win)
	extension.move(squares, snake_head, snake_bodies)
	
	#Create the food object. This will be only one object that moves off screen when eaten and immediately respawns in a new random empty square
	food = Food()
	food.add_food(squares, snake_head, snake_bodies, extension)	

	score = 0

	run = True
	start_time = time.time()
	while run: #The main game loop
		clock.tick(FPS)#tick every 1/fps of a second


		for event in pygame.event.get(): #for loop that allows the user to close the game at any time
			if event.type == pygame.QUIT:
				run = False

		#draw the board
		win.fill ((86, 83, 237))
		draw_board(win)
		food.draw(win)


		#draw and move the snake head
		
		set_square_direction(squares, snake_head) #remember the direction in which the snake is moving in each square it passes
		snake_head.move(squares)

		extension.move(squares, snake_head, snake_bodies)
		extension.draw(win)
		snake_head.draw(win)
		
		
		'''if the snake_head interesects the food, move it away from the screen and append a snake_body object to the end of the snake_bodies list'''
		if snake_head.x == food.x and food.y == snake_head.y: 
			food.x = 1000
			food.y = 0 
		
			if snake_bodies == []:
				if snake_head.direction =='up':
					tail_new = Snake_Body(snake_head.x, snake_head.y+32, snake_head.direction)
				if snake_head.direction =='down':
					tail_new = Snake_Body(snake_head.x, snake_head.y-32, snake_head.direction)
				if snake_head.direction =='left':
					tail_new = Snake_Body(snake_head.x +32, snake_head.y, snake_head.direction)
				if snake_head.direction =='right':
					tail_new = Snake_Body(snake_head.x -32, snake_head.y, snake_head.direction)


			else:
				'''The snake needs to move, and then the tail can be appended in the position of the previous tail'''

				tail_new = Snake_Body(snake_bodies[-1].x_old, snake_bodies[-1].y_old, snake_bodies[-1].direction)

			food.add_food(squares, snake_head, snake_bodies, extension)
			snake_bodies.append(tail_new)
			score+=1
			


		#draw and move the snake body
		for snake_body in snake_bodies:
			pass_to_snake(squares, snake_body)
			set_square_direction(squares, snake_body)
			snake_body.draw(win)
			snake_body.move(squares, snake_head, snake_bodies)

			
			

		#design the lost condition
		if snake_head.x > WIDTH -32 or snake_head.x < 0 or snake_head.y > HEIGHT-32 or snake_head.y < 96:
			win.blit(lost_label, (156, 316))
			
			main_label = main_font.render(f'Final score: {score}', 1, (255,255,255)) #show the final score
			win.blit(main_label, (156, 416))

			pygame.display.update()
			time.sleep(1)
			run = False
		else:
			for snake_body in snake_bodies:
				if snake_body.x == snake_head.x and snake_body.y == snake_head.y: 
					win.blit(lost_label, (156, 316))

					main_label = main_font.render(f'Final score: {score}', 1, (255,255,255)) #show the final score
					win.blit(main_label, (156, 416))

					pygame.display.update()
					time.sleep(1)
					run = False

		
		#Set the key controls:
		keys = pygame.key.get_pressed()

		kz =[k for k in keys if k==True] #don't allow more than one key input to be taken at once
		if len(kz) >1:
			snake_head.direction = snake_head.direction
		
		else:
			if keys[pygame.K_a] and snake_head.direction != 'right': 
				snake_head.direction = 'left'
				#snake_head.move(squares)
			if keys[pygame.K_d] and snake_head.direction != 'left':
				snake_head.direction = 'right'
				#snake_head.move(squares)
			if keys[pygame.K_w] and snake_head.direction !='down':
				snake_head.direction = 'up'
				#snake_head.move(squares)
			if keys[pygame.K_s] and snake_head.direction !='up':
				snake_head.direction = 'down'
				#snake_head.move(squares)



		elapsed_time = time.time() - start_time
		mins = time.strftime("%M:%S", time.gmtime(elapsed_time))
		time_label = main_font.render(f'Time elapsed:{mins}', 1, (255,255,255)) #show elapsed time
		win.blit(time_label, (222, 0))

		main_label = main_font.render(f'Score: {score}', 1, (255,255,255)) #Set the score counter
		win.blit(main_label, (0, 0))

		#update the display
		pygame.display.update()
		


if __name__ == '__main__':
	main()

