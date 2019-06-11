import random
import numpy as np
import pandas as pd

#==================================================
#生成一副不带大小王的扑克
card_type = ['A','B','C','D']
card_num = range(2,15)
cards_all = []
for type in card_type:
    for num in card_num:
        cards_all.append((type,num))
#生成所有顺子组合
strgs = [({14,2,3,4,5},5)]
for i in range(2,11):
    strgs.append((set(range(i,i+5)),i+4))


#==================================================
#计算最大牌型组合
def hand_score(hand):
    #准备工作1：预设好所需的参数
    hand_max = [0]*6
    hand_type = [card[0] for card in hand]
    hand_num = [card[1] for card in hand]
    hand_df = pd.DataFrame({'type':hand_type,'num':hand_num}).sort_values(['type','num'],ascending=[True,False])
    straight = False
    straight_head = np.nan
    sequence = False
    strg_and_seq = False
    strg_and_seq_head = np.nan
    #准备工作2：生成type分组和num分组的df
    hand_gb_type = hand_df.groupby('type').agg({'num': ['count', 'first']})
    hand_gb_type.columns = hand_gb_type.columns.droplevel(0)
    hand_gb_type.sort_values('count', ascending=False, inplace=True)
    hand_gb_num = hand_df.groupby('num',as_index=False).agg('count')
    hand_gb_num.columns = ['num','count']
    hand_gb_num.sort_values(['count','num'], ascending=[False,False], inplace=True)
    #0.1、顺子判断
    for strg in strgs:
        if strg[0] & set(hand_num) == strg[0]:
            straight = True
            straight_head = strg[1]
    #0.2、同花判断
    if hand_gb_type.iloc[0,0] >=5:
        sequence = True
    #0.3、同花顺判断
    if straight and sequence:
        sequence_num = set(hand_df.set_index('type')['num'][hand_gb_type.index[0]])
        for strg in strgs:
            if strg[0] & sequence_num == strg[0]:
                strg_and_seq = True
                strg_and_seq_head = strg[1]
    #9、同花顺判断（既同花又顺子未必是同花顺，要另作判断）
    if strg_and_seq:
        hand_max[0] = 9
        hand_max[1] = strg_and_seq_head
    #8、金刚判断
    elif hand_gb_num.iloc[0,1] == 4:
        hand_max[0] = 8
        hand_max[1] = hand_gb_num.iloc[0,0]
        hand_max[2] = hand_gb_num.iloc[1,0]
    #7、葫芦判断
    elif hand_gb_num.iloc[0,1] == 3 and hand_gb_num.iloc[1,1] == 2:
        hand_max[0] = 7
        hand_max[1] = hand_gb_num.iloc[0, 0]
        hand_max[2] = hand_gb_num.iloc[1, 0]
    #6、同花判断
    elif sequence == True:
        hand_max[0] = 6
        hand_max[1] = hand_gb_type.iloc[0,1]
    #5、顺子判断
    elif straight == True:
        hand_max[0] = 5
        hand_max[1] = straight_head
    #4、三条判断
    elif hand_gb_num.iloc[0,1] == 3:
        hand_max[0] = 4
        hand_max[1] = hand_gb_num.iloc[0, 0]
        hand_max[2] = hand_gb_num.iloc[1, 0]
        hand_max[3] = hand_gb_num.iloc[2, 0]
    #3、两对判断（注意此处的踢脚牌不能直接按排序取，因为有可能有三对）
    elif hand_gb_num.iloc[0,1] == 2 and hand_gb_num.iloc[1,1] == 2:
        hand_max[0] = 3
        hand_max[1] = hand_gb_num.iloc[0, 0]
        hand_max[2] = hand_gb_num.iloc[1, 0]
        hand_max[3] = max(hand_gb_num['num'][2:])
    #2、一对判断
    elif hand_gb_num.iloc[0, 1] == 2:
        hand_max[0] = 2
        hand_max[1] = hand_gb_num.iloc[0, 0]
        hand_max[2] = hand_gb_num.iloc[1, 0]
        hand_max[3] = hand_gb_num.iloc[2, 0]
        hand_max[4] = hand_gb_num.iloc[3, 0]
    #1、高牌
    else:
        hand_max[1] = hand_gb_num.iloc[0, 0]
        hand_max[2] = hand_gb_num.iloc[1, 0]
        hand_max[3] = hand_gb_num.iloc[2, 0]
        hand_max[4] = hand_gb_num.iloc[3, 0]
        hand_max[5] = hand_gb_num.iloc[4, 0]
    #生成分数并返回
    score = sum([hand_max[5-i] * (100**i) for i in range(len(hand_max))])
    return score

#比较各人手牌
def compare(hands):
    scores = [hand_score(hands[i]) for i in range(len(hands))]
    if scores[0] == max(scores):
        return 1 / scores.count(scores[0])
    else:
        return 0

#==================================================
#主程序
player_count = int(input('请输入玩家人数（2-9）\n'))
test_times = int(input('请输入测试次数\n'))
while True:
    cards = cards_all[:]
    print('len cards:',len(cards))
    #round 1
    print('\nround 1\n')
    num1_me = int(input('请输入第一张手牌的号码（2-14）\n'))
    style1_me = input('请输入第一张手牌的花色（A-D，方块为A）\n')
    num2_me = int(input('请输入第二张手牌的号码（2-14）\n'))
    style2_me = input('请输入第二张手牌的花色（A-D，方块为A）\n')
    me_initial = [(style1_me,num1_me),(style2_me,num2_me)]
    cards.remove(me_initial[0])
    cards.remove(me_initial[1])
    win_times = 0
    test_or_not = input('回车进入测试，输入N进入下一round\n')
    if test_or_not != 'N':
        for test_time in range(test_times):
            random.shuffle(cards)
            hands_initial = [me_initial] + [[cards[player_num],cards[player_num + player_count - 1]] for player_num in range(player_count - 1)]
            hands_public = cards[player_count * 2:player_count * 2+5]
            hands = [i + hands_public for i in hands_initial]
            win_times += compare(hands)
            print('{} times completed'.format(test_time + 1))
        print('result for round 1')
        print('me_initial: ',me_initial)
        print('win times: ',win_times)
        print('win rate: ',win_times/test_times * 100,'%')
    #round 2
    how = input('回车进入下一round，输入C进入下一局，输入Q退出游戏\n')
    if how == 'C':
        continue
    if how == 'Q':
        break
    print('\nround 2\n')
    num1_public = int(input('请输入第一张公共牌的号码（2-14）\n'))
    style1_public = input('请输入第一张公共牌的花色（A-D，方块为A）\n')
    num2_public = int(input('请输入第二张公共牌的号码（2-14）\n'))
    style2_public = input('请输入第二张公共牌的花色（A-D，方块为A）\n')
    num3_public = int(input('请输入第三张公共牌的号码（2-14）\n'))
    style3_public = input('请输入第三张公共牌的花色（A-D，方块为A）\n')
    hands_public_2 = [(style1_public,num1_public),(style2_public,num2_public),(style3_public,num3_public)]
    cards.remove(hands_public_2[0])
    cards.remove(hands_public_2[1])
    cards.remove(hands_public_2[2])
    test_or_not = input('回车进入测试，输入N进入下一round\n')
    if test_or_not != 'N':
        for test_time in range(test_times):
            random.shuffle(cards)
            hands_initial = [me_initial] + [[cards[player_num],cards[player_num + player_count - 1]] for player_num in range(player_count - 1)]
            hands_public = hands_public_2 + cards[player_count * 2:player_count * 2+2]
            hands = [i + hands_public for i in hands_initial]
            win_times += compare(hands)
            print('{} times completed'.format(test_time + 1))
        print('result for round 2')
        print('me_initial: ', me_initial)
        print('hands_public_2 ',hands_public_2)
        print('win times: ',win_times)
        print('win rate: ',win_times/test_times * 100,'%')
    #round 3
    how = input('直接回车进入下一round，输入C进入下一局，输入Q退出游戏\n')
    if how == 'C':
        continue
    if how == 'Q':
        break
    print('\nround 3\n')
    num4_public = int(input('请输入第四张公共牌的号码（2-14）\n'))
    style4_public = input('请输入第四张公共牌的花色（A-D，方块为A）\n')
    hands_public_3 = hands_public_2 + [(style4_public,num4_public)]
    cards.remove(hands_public_3[3])
    test_or_not = input('回车进入测试，输入N进入下一round\n')
    if test_or_not != 'N':
        for test_time in range(test_times):
            random.shuffle(cards)
            hands_initial = [me_initial] + [[cards[player_num],cards[player_num + player_count - 1]] for player_num in range(player_count - 1)]
            hands_public = hands_public_3 + cards[player_count * 2:player_count * 2+1]
            hands = [i + hands_public for i in hands_initial]
            win_times += compare(hands)
            print('{} times completed'.format(test_time + 1))
        print('result for round 3')
        print('me_initial: ', me_initial)
        print('hands_public_3 ', hands_public_3)
        print('win times: ',win_times)
        print('win rate: ',win_times/test_times * 100,'%')
    #round 4
    how = input('直接回车进入下一round，输入C进入下一局，输入Q退出游戏\n')
    if how == 'C':
        continue
    if how == 'Q':
        break
    print('\nround 4\n')
    num5_public = int(input('请输入第五张公共牌的号码（2-14）\n'))
    style5_public = input('请输入第五张公共牌的花色（A-D，方块为A）\n')
    hands_public_4 = hands_public_3 + [(style5_public,num5_public)]
    cards.remove(hands_public_4[4])
    for test_time in range(test_times):
        random.shuffle(cards)
        hands_initial = [me_initial] + [[cards[player_num],cards[player_num + player_count - 1]] for player_num in range(player_count - 1)]
        hands_public = hands_public_4
        hands = [i + hands_public for i in hands_initial]
        win_times += compare(hands)
        print('{} times completed'.format(test_time + 1))
    print('result for round 4')
    print('me_initial: ', me_initial)
    print('hands_public_4 ', hands_public_4)
    print('win times: ',win_times)
    print('win rate: ',win_times/test_times * 100,'%')
    how = input('直接回车进入下一局，输入Q退出游戏\n')
    if how == 'Q':
        break