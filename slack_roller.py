from __future__ import print_function

import json
import re
import random
import urlparse

from copy import copy

help_msg = '''rollbot usage
/roll <count>d<sides>[dl<drop_low>][dh<drop_high>][r<reroll>][modifier]

ex: 
/roll 2d20dh1 -> rolls 2d20, drops the highest 1
/roll 4d6dl1 -> rolls 4d6, drops the lowest 1
/roll 2d6r2 -> rolls 2d6, rerolling 1s and 2s
'''

def parse_roll_cmd(roll_cmd):
    '''
    Parses the roll command
    '''
    roll_re = re.compile(r'(?P<count>\d+)d(?P<sides>\d+)(dl(?P<drop_low>\d+)|dh(?P<drop_high>\d+)|r(?P<reroll>\d+))*(?P<modifier>\+\d+|-\d+)?')
    
    roll_match = roll_re.match(roll_cmd)
    
    if roll_match is None:
        return None
    
    modifier = roll_match.group('modifier')
    drop_high = roll_match.group('drop_high')
    drop_low = roll_match.group('drop_low')
    reroll = roll_match.group('reroll')
        
    parsed_roll = {
        'count': int(roll_match.group('count')), 
        'sides': int(roll_match.group('sides')),
        'modifier': int(modifier if modifier else '0'),
        'drop_high': int(drop_high if drop_high else '0'),
        'drop_low': int(drop_low if drop_low else '0'),
        'reroll': int(reroll if reroll else '0')}
        
    return parsed_roll

def roll_dice(parsed_roll):
    '''
    Takes the parsed roll information and calculates the result
    '''
    count = parsed_roll['count']
    sides = parsed_roll['sides']
    drop_high = parsed_roll['drop_high']
    drop_low = parsed_roll['drop_low']
    reroll = parsed_roll['reroll']
    
    rolls = []
    full_results = ''
    
    try:
    
        for i in range(count):
            rolls.append(random.randint(1, sides))
    
        full_results = repr(rolls)
    
        # copy the rolls before making any modifications
        original_rolls = copy(rolls)
        
        # reroll any results lower than or equal to reroll
        if reroll:
            for i,x in enumerate(rolls):
                if x <= reroll:
                    rolls[i] = random.randint(1, sides)
                    
            full_results += '\n=> {!r}'.format(rolls)
        
        # drop highest and lowest, if requested
        if drop_high or drop_low:
            for i in range(drop_high):
                try:
                    rolls.remove(max(rolls))
                except:
                    break

            for i in range(drop_low):
                try:
                    rolls.remove(min(rolls))
                except:
                    break
                
            full_results += '\n=> {!r}'.format(rolls)
        
        total = sum(rolls)
        
        if parsed_roll['modifier']:
            total += parsed_roll['modifier']
    except:
        return None,None
    return total, repr(rolls) if rolls == original_rolls else full_results

def roll(event, context):
    '''
    roll is the handler called by the slack_roller API. It grabs
    the roll request from the POST params, parses it, then calculates the
    result. The result is then formatted and returned back to slack.
    '''
    # parse the params sent from slack
    try:
        form_params = urlparse.parse_qs(event.get('formparams'))
    except:
        return {"text": "I couldn't parse your request."}
    
    if form_params is None:
        return {"text": "I couldn't parse your request."}
    
    user_name = form_params.get('user_name')[0]
    user_id = form_params.get('user_id')[0]
       
    # the text param contains the dice roll request
    roll_cmd = form_params.get('text')
    
    # roll_cmd is either None (empty text) or a list of one element
    # which contains our string
    if roll_cmd is None:
        roll_cmd = '1d20'
    elif roll_cmd == 'help':
        return {'text': help_msg}
    else:
        roll_cmd = roll_cmd[0]
    
    parsed_roll = parse_roll_cmd(roll_cmd)
    
    # If the parsed_roll is None, then something was wrong
    if parsed_roll is None:
        return {'text': 'I couldn\'t parse your request "{}".'.format(roll_cmd)}
    
    result, full_results = roll_dice(parsed_roll)
    
    if result is None:
        return {'text': 'Stop trying to break rollbot!'}
    
    # format the response
    response = {
        'response_type': 'in_channel', 
        'text': '<@{}>  rolled {}'.format(user_id, roll_cmd),
        'attachments': [
            {
                'text': '{} = {}\n{}'.format(roll_cmd, result, full_results)
            }
        ]
    }
    
    return response