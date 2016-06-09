import sys
import copy
import math
import random as r

def initMap(w,h, config):
	Matrix = [["empty" for x in range(w)] for y in range(h)]
	i = 0
	for row in Matrix:
		j = 0
		for column in row:
			if [i, j] in config['zombies']:
				Matrix[i][j] = "PIT"
			elif [i, j] in config['walls']:
	   			Matrix[i][j] = "WALL"
			elif [i, j] in config['goal']:
	   			Matrix[i][j] = "GOAL"
			else:
				Matrix[i][j] = "0"
			j += 1
		i += 1
	emptyMap = [[0 for x in range(w)] for y in range(h)]
	i = 0
	for row in emptyMap:
		j = 0
		for column in row:
			if [i, j] in config['zombies']:
				emptyMap[i][j] = config['reward_for_hitting_zomb']
			elif [i, j] in config['goal']:
				emptyMap[i][j] = config['reward_for_reaching_goal']
			elif [i, j] in config['walls']:
				emptyMap[i][j] = config['reward_for_hitting_wall']
			j += 1
		i += 1
	return Matrix, emptyMap

def changeMap(config):
	i = 0
	iter_stop =len(config['zombies'])
	config['goal'].pop()
	while (i < iter_stop):
		config['zombies'][i] = decide_move(config['zombies'][i], config)
		i += 1
	return config

def decide_move(old_pos, config):
	rand = r.random()
	w, h = config['map_size'][0], config['map_size'][1]
	new_pos = [0,0]
	new_pos[0], new_pos[1] = old_pos[0], old_pos[1]
	right, left, up, down = config['prob_z_right'], config['prob_z_left'], config['prob_z_up'], config['prob_z_down']
	if (rand < right):
		new_pos[1] += 1
	elif (rand < right+left):
		new_pos[1] -= 1
	elif (rand < right+left+up):
		new_pos[0] -= 1
	elif (rand < right+left+up+down):
		new_pos[0] += 1
	else:
		new_pos = old_pos
	if (new_pos in config['goal'] or new_pos in config['walls'] or new_pos in config['zombies']):
		new_pos = old_pos
	if (new_pos[0] < 0 or new_pos[0] >= w or new_pos[1] < 0 or new_pos[1] >= h):
		new_pos = old_pos 

	return new_pos

def preProcessVals(config, w, h):
	predict_map = [[0 for x in range(w)] for y in range(h)]
	i = 0
	for row in predict_map:
		j = 0
		for column in row:
			if [i, j] in config['zombies']:
				predict_map[i][j] += config['reward_for_hitting_zomb'] * config['prob_z_stay']
				if (i + 1 < w):
					predict_map[i+1][j] += config['reward_for_hitting_zomb'] * config['prob_z_right']
				if (i - 1 > 0): 
					predict_map[i-1][j] += config['reward_for_hitting_zomb'] * config['prob_z_left']
				if (j + 1 < h):
					predict_map[i][j+1] += config['reward_for_hitting_zomb'] * config['prob_z_down']
				if (j - 1 > 0):
					predict_map[i][j-1] += config['reward_for_hitting_zomb'] * config['prob_z_up']
			elif [i, j] in config['goal']:
				predict_map[i][j] = config['reward_for_reaching_goal']
			elif [i, j] in config['walls']:
				predict_map[i][j] = config['reward_for_hitting_wall']
			j += 1
		i += 1
	return predict_map


def myFunction(config):
	w, h = config['map_size'][1], config['map_size'][0]
	Matrix, emptyMap = initMap(w,h, config)
	toReturn = []
	l = 0
	steps = len(config['goal'])
	while (l < steps):
		# pre-process map values for future iterations
		predict_map = preProcessVals(config, w, h)
		k = 0
		while (k < config['max_iterations']):
			orig_emptyMap = emptyMap
			i = 0
			temp_sum = 0
			for row in emptyMap:
				j = 0
				for column in row:
					curr_val = emptyMap[i][j]
					if [i, j] not in config['zombies'] and [i, j] not in config['walls'] and [i,j] not in config['goal']:
						result = helper(orig_emptyMap, i, j, config, predict_map)
						Matrix[i][j] = result[0] #direction
						emptyMap[i][j] = result[1] #value
						temp_sum += abs(curr_val - result[1])
					j += 1
				i += 1
			k += 1
			toReturn.append(sum(Matrix, []))
			if temp_sum < config['threshold_difference']: #converged
				break
		config = changeMap(config)
		Matrix, emptyMap = initMap(w,h, config)
		l += 1
	return toReturn
			
def helper(emptyMap, i, j, config, future_map):
	reward_right = 0
	reward_left = 0
	reward_up = 0
	reward_down = 0
	vk_right = 0
	vk_left = 0
	vk_down = 0
	vk_up = 0
	vf_right = 0
	vf_left = 0
	vf_up = 0
	vf_down = 0
	
	#right
	if [i, j+1] in config['walls'] or j+1>config['map_size'][1]-1:
		reward_right = config['reward_for_hitting_wall']
		vk_right = emptyMap[i][j]
		vf_right = future_map[i][j]
	elif [i, j+1] in config['goal']:
		reward_right = config['reward_for_reaching_goal']
		vk_right = emptyMap[i][j+1]
		vf_right = future_map[i][j+1]
	elif [i, j+1] in config['zombies']:
		reward_right = config['reward_for_hitting_zomb']
		vk_right = emptyMap[i][j+1]
		vf_right = future_map[i][j+1]
	else:
		reward_right = config['reward_for_each_step']
		vk_right = emptyMap[i][j+1]
		vf_right = future_map[i][j+1]
		
		
	#left
	if [i, j-1] in config['walls'] or j-1<0:
		reward_left = config['reward_for_hitting_wall']
		vk_left = emptyMap[i][j]
		vf_left = future_map[i][j]
	elif [i, j-1] in config['goal']:
		reward_left = config['reward_for_reaching_goal']
		vk_left = emptyMap[i][j-1]
		vf_left = future_map[i][j-1]
	elif [i, j-1] in config['zombies']:
		reward_left = config['reward_for_hitting_zomb']
		vk_left = emptyMap[i][j-1]
		vf_left = future_map[i][j-1]
	else:
		reward_left = config['reward_for_each_step']
		vk_left = emptyMap[i][j-1]
		vf_left = future_map[i][j-1]
		
	#south or down
	if [i+1, j] in config['walls'] or i+1>config['map_size'][0]-1:
		reward_down = config['reward_for_hitting_wall']
		vk_down = emptyMap[i][j]
		vf_down = future_map[i][j]
	elif [i+1, j] in config['goal']:
		reward_down = config['reward_for_reaching_goal']
		vk_down = emptyMap[i+1][j]
		vf_down = future_map[i+1][j]
	elif [i+1, j] in config['zombies']:
		reward_down = config['reward_for_hitting_zomb']
		vk_down = emptyMap[i+1][j]
		vf_down = future_map[i+1][j]
	else:
		reward_down = config['reward_for_each_step']
		vk_down = emptyMap[i+1][j]
		vf_down = future_map[i+1][j]
		
	#north or up
	if [i-1, j] in config['walls'] or i-1<0:
		reward_up = config['reward_for_hitting_wall']
		vk_up = emptyMap[i][j]
		vf_up = future_map[i][j]
	elif [i-1, j] in config['goal']:
		reward_up = config['reward_for_reaching_goal']
		vk_up = emptyMap[i-1][j]
		vf_up = future_map[i-1][j]
	elif [i-1, j] in config['zombies']:
		reward_up = config['reward_for_hitting_zomb']
		vk_up = emptyMap[i-1][j]
		vf_up = future_map[i-1][j]
	else:
		reward_up = config['reward_for_each_step']
		vk_up = emptyMap[i-1][j]
		vf_up = future_map[i-1][j]
	
	
	#action = right and right
	r_right = config['prob_move_forward']*(reward_right + config['discount_factor']*vk_right+ config['predict_factor']*vf_right)
	#action = right and left
	r_left = config['prob_move_backward']*(reward_left + config['discount_factor']*vk_left+config['predict_factor']*vf_left)
	#action = right and south
	r_down = config['prob_move_right']*(reward_down + config['discount_factor']*vk_down+config['predict_factor']*vf_down)
	#action = right and north
	r_up = config['prob_move_left']*(reward_up + config['discount_factor']*vk_up+config['predict_factor']*vf_up)
	r_action = r_right + r_left + r_down + r_up
	
	#action = left and left
	l_left = config['prob_move_forward']*(reward_left + config['discount_factor']*vk_left+config['predict_factor']*vf_left)
	#action = left and right
	l_right = config['prob_move_backward']*(reward_right + config['discount_factor']*vk_right+config['predict_factor']*vf_right)
	#action = left and south
	l_down = config['prob_move_left']*(reward_down + config['discount_factor']*vk_down+config['predict_factor']*vf_down)
	#action = left and north
	l_up = config['prob_move_right']*(reward_up + config['discount_factor']*vk_up+config['predict_factor']*vf_up)
	l_action = l_right + l_left + l_down + l_up
	
	#action = south and south
	s_down = config['prob_move_forward']*(reward_down + config['discount_factor']*vk_down+config['predict_factor']*vf_down)
	#action = south and north
	s_up = config['prob_move_backward']*(reward_up + config['discount_factor']*vk_up+config['predict_factor']*vf_up)
	#action = south and left
	s_left = config['prob_move_left']*(reward_right + config['discount_factor']*vk_right+config['predict_factor']*vf_right)
	#action = south and right
	s_right = config['prob_move_right']*(reward_left + config['discount_factor']*vk_left+config['predict_factor']*vf_left)
	s_action = s_right + s_left + s_down + s_up
	
	#action = north and north
	n_up = config['prob_move_forward']*(reward_up + config['discount_factor']*vk_up+config['predict_factor']*vf_up)
	#action = north and south
	n_down = config['prob_move_backward']*(reward_down + config['discount_factor']*vk_down+config['predict_factor']*vf_down)
	#action = north and left
	n_left = config['prob_move_left']*(reward_left + config['discount_factor']*vk_left+config['predict_factor']*vf_left)
	#action = north and right
	n_right = config['prob_move_right']*(reward_right + config['discount_factor']*vk_right+config['predict_factor']*vf_right)
	n_action = n_right + n_left + n_down + n_up
	
	possible_action = [r_action, l_action, s_action, n_action]
	res = max(possible_action)
	direction = ""
	if res == l_action:
		direction = "W"
	elif res == r_action:
		direction = "E"
	elif res == s_action:
		direction = "S"
	else:
		direction = "N"
		
	return [direction, res]
