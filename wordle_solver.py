#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 17:25:00 2022

@author: advaith
"""

import random

#%%

"""GLOBAL VARIABLES"""
max_score = 22222
round_score = 0
total_score = 0


def read_from_txt(word_list):
    #read from the textfile and store as a list. duplicate list
    with open("wordle_word.txt") as file:
        for line in file:
            word_list.append(line.rstrip())
    word_list.sort()
    return word_list, word_list

def find_letter_frequency(word_list):
    #first, combine the entire list to one big string. then find letter frequencies of the string
    letter_frequency = {}
    combined_string = "".join([str(word) for word in word_list])
    for char in combined_string:
        if char in letter_frequency: 
            letter_frequency[char] += 1
        else:
            letter_frequency[char] = 1
    #sort frequency in descending order
    letter_frequency = sorted(letter_frequency.items(), key = lambda kv: kv[1],reverse=True)
    return letter_frequency

def randomWord(min,max):
    temp_list = word_list
    for i in range(min,max):
        #use list comprehension to go through list and remove words which dont have the specified letters
        y = letter_frequency[i][0]
        temp_list = [x for x in temp_list if y in x]
    if len(temp_list) == 0:
        temp_list.append(randomWord(min,max-1))
    return random.choice(temp_list)


def game(updated_word_list, turn):
    round_score = 0
    global total_score
    if total_score <= 4 and len(updated_word_list) > 3:
        word_guess = randomWord(turn*5,(turn+1)*5)
    
    else:
        word_guess = random.choice(updated_word_list)
        
    confidence_value = confidence(updated_word_list)
    print("The computer's guess is: \n {}\n Confidence Value: {}%".format(word_guess, round((confidence_value),2)))
    round_score = input("Enter result of guess (grey = 0, yellow = 1, green = 2, Ex. 11002): ")
    for i in range(0,5):
        total_score += int(round_score[i])
    
    # print("Total score is {}".format(total_score))
    return word_guess, str(round_score)

def update_word_list(updated_word_list, word_guess, round_score):
    for i in range(0,5):
        no_repeat_status = True
        # print(round_score)
        letter_score = int(round_score[i])
        letter_guess = word_guess[i]
        #grey, letter_score = 0
        if letter_score == 0:
            for j in range(0,5):
                if j != i:
                    if letter_guess == word_guess[j]:
                        no_repeat_status = False
            if no_repeat_status == True:
                updated_word_list = [x for x in updated_word_list if letter_guess not in x]
        
        #yellow, letter_score = 1
        if letter_score == 1:
            updated_word_list = [x for x in updated_word_list if (letter_guess in x and letter_guess not in x[i])]
        
        #green, letter_score = 2
        if letter_score == 2:
            updated_word_list = [x for x in updated_word_list if (letter_guess in x and letter_guess in x[i])]

    return updated_word_list



#%%

def confidence(updated_word_list):
    
    confidence_value = 100 / len(updated_word_list)
    
    return confidence_value

#%%
if __name__ == '__main__':
    turn = 0
    print("Time to guess today's Wordle!\n")
    win_status = False
    word_list = []
    updated_word_list = []
    word_list, updated_word_list = read_from_txt(word_list)
    # print("Total Score is {}".format(total_score))
    letter_frequency = find_letter_frequency(word_list)   
    for turn in range(0,6):
        #print(updated_word_list)
        word_guess, round_score = game(updated_word_list, turn)
        if int(round_score) == max_score:
            win_status = True
            break
        updated_word_list = update_word_list(updated_word_list, word_guess, round_score)
        # print(len(updated_word_list))
        # print(updated_word_list)
    
    if win_status == True:
        print("Computer wins! The final word was:\n\n{}".format(word_guess))
    else:
        print("That was hard! Congratulations you won")
   

        
#%%
        
"""DEBUGGING"""
def debugging():
    win_status = False
    word_list = []
    updated_word_list = []
    word_list, updated_word_list = read_from_txt(word_list)
    # print("Total Score is {}".format(total_score))
    letter_frequency = find_letter_frequency(word_list)   
    updated_word_list = update_word_list(updated_word_list, "those", "00200")
    updated_word_list = update_word_list(updated_word_list, "brain", "00000")
    updated_word_list = update_word_list(updated_word_list, "brunt", "00000")
    updated_word_list = update_word_list(updated_word_list, "lumpy", "10000")
    updated_word_list = update_word_list(updated_word_list, "lease", "10000")
    print(len(updated_word_list))
    print(updated_word_list)

#debugging()
        
    
#%%
    


        