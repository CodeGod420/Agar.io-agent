# small network game that has differnt blobs
# moving around the screen

from asyncio.windows_events import NULL
import contextlib
from distutils.command.build_scripts import first_line_re
from turtle import distance
from winreg import HKEY_LOCAL_MACHINE

from numpy import empty
with contextlib.redirect_stdout(None):
	import pygame
from client import Network
import random
import os
import math
pygame.font.init()

# Constants
PLAYER_RADIUS = 15
START_VEL = 9
BALL_RADIUS = 5
#AGENT_RANGE_SIGHT = 100

W, H = 1600, 830

NAME_FONT = pygame.font.SysFont("comicsans", 20)
TIME_FONT = pygame.font.SysFont("comicsans", 30)
SCORE_FONT = pygame.font.SysFont("comicsans", 26)

COLORS = [(255,0,0), (255, 128, 0), (255,255,0), (128,255,0),(0,255,0),(0,255,128),(0,255,255),(0, 128, 255), (0,0,255), (0,0,255), (128,0,255),(255,0,255), (255,0,128),(128,128,128), (0,0,0)]

# Dynamic Variables
players = {}
balls = []

# FUNCTIONS
def convert_time(t):
	"""
	converts a time given in seconds to a time in
	minutes

	:param t: int
	:return: string
	"""
	if type(t) == str:
		return t

	if int(t) < 60:
		return str(t) + "s"
	else:
		minutes = str(t // 60)
		seconds = str(t % 60)

		if int(seconds) < 10:
			seconds = "0" + seconds

		return minutes + ":" + seconds


def redraw_window(players, balls, game_time, score):
	"""
	draws each frame
	:return: None
	"""
	WIN.fill((255,255,255)) # fill screen white, to clear old frames
	
		# draw all the orbs/balls
	for ball in balls:
		pygame.draw.circle(WIN, ball[2], (ball[0], ball[1]), BALL_RADIUS)

	# draw each player in the list
	for player in sorted(players, key=lambda x: players[x]["score"]):
		p = players[player]
		pygame.draw.circle(WIN, p["color"], (p["x"], p["y"]), PLAYER_RADIUS + round(p["score"]))
		#pygame.draw.circle(WIN, (255,0,0) , (p["x"], p["y"]), AGENT_RANGE_SIGHT + round(p["score"]),2)
		# render and draw name for each player
		text = NAME_FONT.render(p["name"], 1, (0,0,0))
		WIN.blit(text, (p["x"] - text.get_width()/2, p["y"] - text.get_height()/2))

	# draw scoreboard
	sort_players = list(reversed(sorted(players, key=lambda x: players[x]["score"])))
	title = TIME_FONT.render("Scoreboard", 1, (0,0,0))
	start_y = 25
	x = W - title.get_width() - 10
	WIN.blit(title, (x, 5))

	ran = min(len(players), 3)
	for count, i in enumerate(sort_players[:ran]):
		text = SCORE_FONT.render(str(count+1) + ". " + str(players[i]["name"]), 1, (0,0,0))
		WIN.blit(text, (x, start_y + count * 20))

	# draw time
	text = TIME_FONT.render("Time: " + convert_time(game_time), 1, (0,0,0))
	WIN.blit(text,(10,10))
	# draw score
	text = TIME_FONT.render("Score: " + str(round(score)),1,(0,0,0))
	WIN.blit(text,(10,15 + text.get_height()))
############Codigo de Hill climbing #####################################333
def randomSolution(balls_distances):
	bolas = list(range(len(balls_distances)))
	solution = []

	for i in range(len(balls_distances)):
		randomBall = bolas[random.randint(0, len(bolas) - 1)]
		solution.append(randomBall)
		bolas.remove(randomBall)
	return solution

def routeLength(balls_distances, solution):
	routeLength = 0
	for i in range(len(solution)):
		routeLength += balls_distances[solution[i - 1]][solution[i]]
	return routeLength

def getNeighbours(solution):
	neighbours = []
	for i in range(len(solution)):
		for j in range(i + 1, len(solution)):
			neighbour = solution.copy()
			neighbour[i] = solution[j]
			neighbour[j] = solution[i]
			neighbours.append(neighbour)
	return neighbours

def getBestNeighbour(balls_distances, neighbours):
    bestRouteLength = routeLength(balls_distances, neighbours[0])
    bestNeighbour = neighbours[0]
    for neighbour in neighbours:
        currentRouteLength = routeLength(balls_distances, neighbour)
        if currentRouteLength < bestRouteLength:
            bestRouteLength = currentRouteLength
            bestNeighbour = neighbour
    return bestNeighbour, bestRouteLength

def hillClimbing(balls_distances):
    currentSolution = randomSolution(balls_distances)
    currentRouteLength = routeLength(balls_distances, currentSolution)
    neighbours = getNeighbours(currentSolution)
    bestNeighbour, bestNeighbourRouteLength = getBestNeighbour(balls_distances, neighbours)

    while bestNeighbourRouteLength < currentRouteLength:
        currentSolution = bestNeighbour
        currentRouteLength = bestNeighbourRouteLength
        neighbours = getNeighbours(currentSolution)
        bestNeighbour, bestNeighbourRouteLength = getBestNeighbour(balls_distances, neighbours)
	
    currentSolutionList = [currentSolution, currentRouteLength]
    return currentSolutionList

def main(name):
	"""
	function for running the game,
	includes the main loop of the game

	:param players: a list of dicts represting a player
	:return: None
	"""
	global players

	# start by connecting to the network
	server = Network()
	current_id = server.connect(name)
	balls, players, game_time = server.send("get")
	# setup the clock, limit to 30fps
	clock = pygame.time.Clock()
	run = True
	player = players[current_id]

	distances = []
	balls_distances = []
	'''
	for ball in balls:
		dist_P = math.sqrt((ball[0] - player["x"])**2 + (ball[1]-player["y"])**2)
		if dist_P < AGENT_RANGE_SIGHT:
			for ball_2 in balls:
				dist_P2 = math.sqrt((ball_2[0] - player["x"])**2 + (ball_2[1]-player["y"])**2)
				if dist_P2 < AGENT_RANGE_SIGHT:
					dist = math.sqrt((ball[0] - ball_2[0])**2 + (ball[1]-ball_2[1])**2)
					distances.append(round(dist))
			balls_distances.append(distances)
			distances = []
	'''
	for ball in balls:
		for ball_2 in balls:
			dist = math.sqrt((ball[0] - ball_2[0])**2 + (ball[1]-ball_2[1])**2)
			distances.append(round(dist))
		balls_distances.append(distances)
		distances = []
	
	ruta_candidata = hillClimbing(balls_distances)
	for i in range(5):	
		route = hillClimbing(balls_distances)
		if ruta_candidata[1] > route[1]:
			ruta_candidata = route
	
	for i in ruta_candidata[0]:
		next_ball = balls[i]
		dis = math.sqrt((next_ball[0] - player["x"])**2 + (next_ball[1]-player["y"])**2)
		while dis >= PLAYER_RADIUS + player["score"]:
			clock.tick(30) # 30 fps max
			player = players[current_id]
			vel = START_VEL - round(player["score"]/14)
			if vel <= 1:
				vel = 1
			
			if next_ball[0] - player["x"] > 0 and player["x"] - vel - PLAYER_RADIUS - player["score"] >= -100:
				player["x"] = player["x"] + vel
			elif next_ball[0] - player["x"] < 0 and player["x"] + vel + PLAYER_RADIUS + player["score"] <= W + 100:
				player["x"] = player["x"] - vel
			if next_ball[1] - player["y"] > 0 and player["y"] - vel - PLAYER_RADIUS - player["score"] >= -100:
				player["y"] = player["y"] + vel
			elif next_ball[1] - player["y"] < 0 and player["y"] + vel + PLAYER_RADIUS + player["score"] <= H + 100:
				player["y"] = player["y"] - vel
			
			data = ""
			data = "move " + str(player["x"]) + " " + str(player["y"])
			# send data to server and recieve back all players information
			balls_draw, players, game_time = server.send(data)
			for event in pygame.event.get():
				# if user hits red x button close window
				if event.type == pygame.QUIT:
					run = False
				if event.type == pygame.KEYDOWN:
					# if user hits a escape key close program
					if event.key == pygame.K_ESCAPE:
						run = False
			dis = math.sqrt((next_ball[0] - player["x"])**2 + (next_ball[1]-player["y"])**2)
			if run == False:
				break
			# redraw window then update the frame
			redraw_window(players, balls_draw, game_time, player["score"])
			pygame.display.update()
		data = ""
		data = "move " + str(player["x"]) + " " + str(player["y"])

		
	print("\n\n")
	print("Tiempo del agente: " ,game_time)
	print("\n\n")
	server.disconnect()
	pygame.quit()
	quit()



	
# get users name

name = "Hill_climbing"


# make window start in top left hand corner
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,30)

# setup pygame window
WIN = pygame.display.set_mode((W,H))
pygame.display.set_caption("Blobs")

# start game
main(name)