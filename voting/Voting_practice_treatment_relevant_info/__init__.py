from otree.api import *
import random
import json


doc = """
Voting_practice_treatment_relevant_info
"""


class C(BaseConstants):
    NAME_IN_URL = 'Voting_practice_treatment_relevant_info'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 5
    AMOUNT_SHARED_IF_WIN = 15
    AMOUNT_SHARED_IF_LOSE = 2
    CHOICES = [
        ('R', 'RED Box'),
        ('B', 'BLUE Box')
    ]
    STATES = ['R', 'B']
    QUALITIES = ['h', 'l']
    MAJORITY_B_4 = ['send to a player who got B', 'send to a player who got R', 'do not send to anyone']
    MAJORITY_R_4 = ['send to a player who got R', 'send to a player who got B', 'do not send to anyone']
    MAJORITY_B_3 = ['send to a player who got B', 'send to a player who got R', 'do not send to anyone']
    MAJORITY_R_3 = ['send to a player who got R', 'send to a player who got B', 'do not send to anyone']
    MINORITY_B_1 = ['send to a player who got R', 'do not send to anyone']
    MINORITY_R_1 = ['send to a player who got B', 'do not send to anyone']
    MINORITY_B_2 = ['send to a player who got B', 'send to a player who got R', 'do not send to anyone']
    MINORITY_R_2 = ['send to a player who got R', 'send to a player who got B', 'do not send to anyone']
    ALL_R = ['send to a player who got R', 'do not send to anyone']
    ALL_B = ['send to a player who got B', 'do not send to anyone']


class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly()


class Group(BaseGroup):
    state = models.StringField()
    r_count = models.IntegerField(initial=0)
    b_count = models.IntegerField(initial=0)
    chosen_player_id = models.IntegerField()
    chosen_player_vote = models.StringField()
    def set_payoffs(self):
        chosen_player = random.choice(self.get_players())
        self.chosen_player_id = chosen_player.id_in_group
        self.chosen_player_vote = chosen_player.vote
        if chosen_player.vote == self.state:
            payoff_record = C.AMOUNT_SHARED_IF_WIN
        else:
            payoff_record = C.AMOUNT_SHARED_IF_LOSE
        for p in self.get_players():
            p.payoff_record = payoff_record

    def calculate_signals(self):
        r_count = 0
        b_count = 0
        for p in self.get_players():
            if p.signals == 'r':
                r_count += 1
            elif p.signals == 'b':
                b_count += 1
        self.r_count = r_count
        self.b_count = b_count


class Player(BasePlayer):
    timeSpent1 = models.FloatField()
    timeSpent2 = models.FloatField()
    decision = models.StringField()
    payoff_record = models.IntegerField(initial=0)
    info_from_whom = models.StringField()
    chosen_receiver = models.IntegerField(null=True)
    vote = models.StringField(widget=widgets.RadioSelect, choices=C.CHOICES)
    state = models.StringField()
    qualities = models.StringField()
    signals = models.CharField()
    selected_round = models.IntegerField()
    r_count = models.IntegerField()
    b_count = models.IntegerField()

    def get_decision_options(self):
        if self.r_count == 0:
            options = list(C.ALL_B)
        elif self.r_count == 1:
            if self.signals == 'b':
                options = list(C.MAJORITY_B_4)
            else:  # signals == 'r'
                options = list(C.MINORITY_R_1)
        elif self.r_count == 2:
            if self.signals == 'b':
                options = list(C.MAJORITY_B_3)
            else:  # signals == 'r'
                options = list(C.MINORITY_R_2)
        elif self.r_count == 3:
            if self.signals == 'b':
                options = list(C.MINORITY_B_2)
            else:  # signals == 'r'
                options = list(C.MAJORITY_R_3)
        elif self.r_count == 4:
            if self.signals == 'b':
                options = list(C.MINORITY_B_1)
            else:  # signals == 'r'
                options = list(C.MAJORITY_R_4)
        else:  # r_count = 5
            options = list(C.ALL_R)

        random.shuffle(options)
        return options

class StartRoundWaitPage(WaitPage):
    wait_for_all_groups = True
    @staticmethod
    def after_all_players_arrive(subsession):
        subsession.group_randomly()
        for group in subsession.get_groups():
            chosen_state = random.choice(C.STATES)
            group.state = chosen_state
            for player in group.get_players():
                player.state = chosen_state
                qualities = random.choice(C.QUALITIES)
                player.qualities = qualities

                if player.state == 'R':
                    if player.qualities == 'h':
                        player.signals = 'r' if random.random() < 7 / 8 else 'b'
                    else:  # 'l'
                        player.signals = 'r' if random.random() < 4 / 7 else 'b'
                else:  # 'B'
                    if player.qualities == 'h':
                        player.signals = 'r' if random.random() < 1 / 7 else 'b'
                    else:  # 'l'
                        player.signals = 'r' if random.random() < 3 / 7 else 'b'

            group.calculate_signals()
            for player in group.get_players():
                player.r_count = group.r_count
                player.b_count = group.b_count


class Welcome(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class General_Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Main_Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Practice(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class ResultsWaitPage1(WaitPage):
    wait_for_all_groups = True


class Info_and_decision(Page):
    form_model = 'player'
    form_fields = ['timeSpent1','decision']
    @staticmethod
    def vars_for_template(player):
        if player.qualities == 'l':
            quality_display = "Box B"
        else:
            quality_display = "Box A"

        if player.signals == 'r':
            player_signal_color = "red"
        else:  # 'b'
            player_signal_color = "blue"

        player_signal_style = f"height: 1.2em; width: 1.2em; background-color: {player_signal_color}; border-radius: 50%; display: inline-block; vertical-align: middle; margin: 0 5px;"

        other_signals_info = []
        for p in player.group.get_players():
            if p.id_in_group != player.id_in_group:
                if p.signals == 'r':
                    signal_color = "red"
                else:  # 'b'
                    signal_color = "blue"

                other_signals_info.append({
                    'player_id': p.id_in_group,
                    'signal_style': f"height: 1.2em; width: 1.2em; background-color: {signal_color}; border-radius: 50%; display: inline-block; vertical-align: middle; margin: 0 5px;",
                })

        return dict(
            quality=quality_display,
            player_signal_style=player_signal_style,
            other_signals_info=other_signals_info,
        )


class ResultsWaitPage2(WaitPage):
    wait_for_all_groups = True

    def after_all_players_arrive(self):
        groups = self.subsession.get_groups()

        for group in groups:
            group_players = group.get_players()

            for player in group_players:
                player.info_from_whom = str(player.id_in_group)

            for participant in group_players:
                if participant.decision == 'send to a player who got B':
                    eligible_players = [p for p in group_players if p.signals == 'b' and p.id_in_group != participant.id_in_group]
                    if eligible_players:
                        chosen_receiver = random.choice(eligible_players)
                        chosen_receiver.info_from_whom += f",{participant.id_in_group}"
                        participant.chosen_receiver = chosen_receiver.id_in_group
                elif participant.decision == 'send to a player who got R':
                    eligible_players = [p for p in group_players if p.signals == 'r' and p.id_in_group != participant.id_in_group]
                    if eligible_players:
                        chosen_receiver = random.choice(eligible_players)
                        chosen_receiver.info_from_whom += f",{participant.id_in_group}"
                        participant.chosen_receiver = chosen_receiver.id_in_group


class network_and_voting(Page):
    form_model = 'player'
    form_fields = ['timeSpent2','vote']

    @staticmethod
    def vars_for_template(player):
        all_players = player.group.get_players()
        participants_info = []

        info_sources = set(map(int, player.info_from_whom.split(',')))

        for participant in all_players:
            if participant.signals == 'r':
                player_signal_color = "red"
            else:  # b
                player_signal_color = "blue"

            player_signal_style = f"height: 1.2em; width: 1.2em; background-color: {player_signal_color}; border-radius: 50%; display: inline-block; vertical-align: middle; margin: 0 5px;"
            all_info = participant.info_from_whom

            if participant.qualities == 'l':
                quality_representation = "Box B"
            else:
                quality_representation = "Box A"

            box_info = quality_representation if participant.id_in_group in info_sources else 'Unknown'

            participants_info.append({
                'id_in_group': participant.id_in_group,
                'quality_representation': quality_representation,
                'player_signal_style': player_signal_style,
                'is_self': participant.id_in_group == player.id_in_group,
                'box_info': box_info,
                'all_info': all_info
            })

        participants_info = sorted(participants_info, key=lambda x: not x['is_self'])

        return {
            'participants_info': participants_info
        }


class ResultsWaitPage3(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()


class ResultsWaitPage4(WaitPage):
    wait_for_all_groups = True


class ResultsWaitPage5(WaitPage):
    def is_displayed(player:Player):
        return player.round_number==C.NUM_ROUNDS

    def after_all_players_arrive(self):
        selected_round = random.randint(1, C.NUM_ROUNDS)
        for player in self.group.get_players():
            player_in_selected_round = player.in_round(selected_round)
            player.selected_round = selected_round
            player.payoff = player_in_selected_round.payoff_record

class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    def vars_for_template(player):
        return {
            'selected_round': player.in_round(5).selected_round,

            'vote_round_1': 'RED' if player.in_round(1).vote == 'R' else 'BLUE',
            'state_round_1': 'RED' if player.in_round(1).state == 'R' else 'BLUE',
            'payoff_record_round_1': player.in_round(1).payoff_record,
            'selected_voter_round_1': player.group.in_round(1).chosen_player_id,
            'selected_vote_round_1': 'RED' if player.group.in_round(1).chosen_player_vote == 'R' else 'BLUE',

            'vote_round_2': 'RED' if player.in_round(2).vote == 'R' else 'BLUE',
            'state_round_2': 'RED' if player.in_round(2).state == 'R' else 'BLUE',
            'payoff_record_round_2': player.in_round(2).payoff_record,
            'selected_voter_round_2': player.group.in_round(2).chosen_player_id,
            'selected_vote_round_2': 'RED' if player.group.in_round(2).chosen_player_vote == 'R' else 'BLUE',

            'vote_round_3': 'RED' if player.in_round(3).vote == 'R' else 'BLUE',
            'state_round_3': 'RED' if player.in_round(3).state == 'R' else 'BLUE',
            'payoff_record_round_3': player.in_round(3).payoff_record,
            'selected_voter_round_3': player.group.in_round(3).chosen_player_id,
            'selected_vote_round_3': 'RED' if player.group.in_round(3).chosen_player_vote == 'R' else 'BLUE',

            'vote_round_4': 'RED' if player.in_round(4).vote == 'R' else 'BLUE',
            'state_round_4': 'RED' if player.in_round(4).state == 'R' else 'BLUE',
            'payoff_record_round_4': player.in_round(4).payoff_record,
            'selected_voter_round_4': player.group.in_round(4).chosen_player_id,
            'selected_vote_round_4': 'RED' if player.group.in_round(4).chosen_player_vote == 'R' else 'BLUE',

            'vote_round_5': 'RED' if player.in_round(5).vote == 'R' else 'BLUE',
            'state_round_5': 'RED' if player.in_round(5).state == 'R' else 'BLUE',
            'payoff_record_round_5': player.in_round(5).payoff_record,
            'selected_voter_round_5': player.group.in_round(5).chosen_player_id,
            'selected_vote_round_5': 'RED' if player.group.in_round(5).chosen_player_vote == 'R' else 'BLUE',

        }

page_sequence = [StartRoundWaitPage, Welcome, General_Instructions, Main_Instructions, Practice, ResultsWaitPage1, Info_and_decision, ResultsWaitPage2, network_and_voting, ResultsWaitPage3, ResultsWaitPage4, ResultsWaitPage5, Results]
