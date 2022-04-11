import pygame
import random
import argparse

# define some global variables
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BOARD_SIZE = (6, 7)



class Full_colm_exception(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Slot():

    SIZE = 85

    def __init__(self, row_index, column_index, width, height, x1, y1):

        self.content = 0
        self.row_index = row_index
        self.column_index = column_index
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width * 2, height * 2))
        self.x_pos = x1
        self.y_pos = y1

    def get_location(self):

        return (self.row_index, self.column_index)

    def get_position(self):

        return (self.x_pos, self.y_pos)

    def set_coin(self, coin):

        self.content = coin.get_coin_type()

    def check_slot_fill(self):

        return (self.content != 0)

    def get_content(self):

        return self.content

    def draw(self, background):

        pygame.draw.rect(self.surface, GREEN, (0, 0, self.width, self.height))
        pygame.draw.rect(self.surface, WHITE, (1, 1, self.width - 2, self.height - 2))
        self.surface = self.surface.convert()
        background.blit(self.surface, (self.x_pos, self.y_pos))


class Board():

    x_margin = 300
    y_margin = 150

    def __init__(self, no_of_rows, no_of_colms):

        self.container = [[Slot(i, j, Slot.SIZE, Slot.SIZE,
                                j * Slot.SIZE + Board.x_margin,
                                i * Slot.SIZE + Board.y_margin) for j in range(no_of_colms)] for i in range(no_of_rows)]
        self.no_of_rows = no_of_rows
        self.no_of_colms = no_of_colms
        self.slots_no= no_of_rows * no_of_colms
        self.total_slots_filled = 0
        self.last_visited_nodes = []
        self.last_value = 0
        self.state = [[0 for j in range(no_of_colms)] for i in range(no_of_rows)]
        self.prev_state = None
        self.prev_move = (None, None, None)
        self.representation = [[SlotTrackerNode() for j in range(no_of_colms)] for i in range(no_of_rows)]
        for i in range(no_of_rows):
            index_of_prev_row = i - 1
            index_of_next_row = i + 1
            for j in range(no_of_colms):
                index_of_prev_colm = j - 1
                index_of_next_colm = j + 1
                current_node = self.representation[i][j]
                if index_of_prev_row >= 0 and index_of_prev_colm >= 0:
                    current_node.top_left = self.representation[index_of_prev_row][index_of_prev_colm]
                if index_of_prev_row >= 0:
                    current_node.top = self.representation[index_of_prev_row][j]
                if index_of_prev_row >= 0 and index_of_next_colm < no_of_colms:
                    current_node.top_right = self.representation[index_of_prev_row][index_of_next_colm]
                if index_of_prev_colm >= 0:
                    current_node.left = self.representation[i][index_of_prev_colm]

                if index_of_next_colm < no_of_colms:
                    current_node.right = self.representation[i][index_of_next_colm]
                if index_of_next_row < no_of_rows and index_of_prev_colm >= 0:
                    current_node.bottom_left = self.representation[index_of_next_row][index_of_prev_colm]

                if index_of_next_row < no_of_rows:
                    current_node.bottom = self.representation[index_of_next_row][j]
                if index_of_next_row < no_of_rows and index_of_next_colm < no_of_colms:
                    current_node.bottom_right = self.representation[index_of_next_row][index_of_next_colm]

    def draw(self, background):

        for i in range(self.no_of_rows):
            for j in range(self.no_of_colms):
                self.container[i][j].draw(background)

    def get_slot(self, row_index, column_index):

        return self.container[row_index][column_index]

    def check_column_fill(self, col_num):

        for i in range(len(self.container)):
            if not self.container[i][col_num].check_slot_fill():
                return False
        return True

    def insert_coin(self, coin, background, game_logic):

        col_num = coin.get_column()
        if not self.check_column_fill(col_num):
            row_index = self.insert_row(col_num)
            self.container[row_index][col_num].set_coin(coin)
            if (self.prev_move[0] == None):
                self.prev_state = [[0 for j in range(self.no_of_colms)] for i in range(self.no_of_rows)]
            else:
                (prev_row, prev_col, value) = self.prev_move
                self.prev_state[prev_row][prev_col] = value
            self.prev_move = (row_index, col_num, coin.get_coin_type())
            self.state[row_index][col_num] = coin.get_coin_type()
            self.update_slot_tracker(row_index, col_num, coin.get_coin_type())
            self.total_slots_filled += 1
            self.last_value = coin.get_coin_type()
            coin.drop(background, row_index)
        else:
            raise Full_colm_exception('Filled Column!')

        result = game_logic.check_game_over()

        return result

    def insert_row(self, col_num):

        for i in range(len(self.container)):
            if self.container[i][col_num].check_slot_fill():
                return (i - 1)

        return self.no_of_rows - 1

    def getdimension(self):

        return (self.no_of_rows, self.no_of_colms)

    def check_board(self):

        return (self.slots_no== self.total_slots_filled)

    def get_representation(self):

        return self.representation

    def get_available_actions(self):

        actions = []
        for i in range(self.no_of_colms):
            if (not self.check_column_fill(i)):
                actions.append(i)
        return actions

    def get_state(self):

        result = tuple(tuple(x) for x in self.state)

        return result

    def get_prev_state(self):

        result = tuple(tuple(x) for x in self.prev_state)

        return result

    def get_last_filled_information(self):

        return (self.last_visited_nodes, self.last_value)

    def update_slot_tracker(self, i, j, coin_type):

        self.last_visited_nodes = []
        start_node = self.representation[i][j]
        start_node.value = coin_type
        self.traverse(start_node, coin_type, i, j, self.last_visited_nodes)
        # reset all the nodes as if it hadn't been visited
        for indices in self.last_visited_nodes:
            self.representation[indices[0]][indices[1]].visited = False

    def traverse(self, current_node, desired_value, i, j, visited_nodes):

        current_node.visited = True
        visited_nodes.append((i, j))
        if current_node.top_left:
            top_left_node = current_node.top_left
            if top_left_node.value == desired_value:
                current_node.top_left_score = top_left_node.top_left_score + 1
                if not top_left_node.visited:
                    self.traverse(top_left_node, desired_value, i - 1, j - 1, visited_nodes)
        if current_node.top:
            top_node = current_node.top
            if top_node.value == desired_value:
                current_node.top_score = top_node.top_score + 1
                if not top_node.visited:
                    self.traverse(top_node, desired_value, i - 1, j, visited_nodes)
        if current_node.top_right:
            top_right_node = current_node.top_right
            if top_right_node.value == desired_value:
                current_node.top_right_score = top_right_node.top_right_score + 1
                if not top_right_node.visited:
                    self.traverse(top_right_node, desired_value, i - 1, j + 1, visited_nodes)

        if current_node.left:
            left_node = current_node.left
            if left_node.value == desired_value:
                current_node.left_score = left_node.left_score + 1
                if not left_node.visited:
                    self.traverse(left_node, desired_value, i, j - 1, visited_nodes)

        if current_node.right:
            right_node = current_node.right
            if right_node.value == desired_value:
                current_node.right_score = right_node.right_score + 1
                if not right_node.visited:
                    self.traverse(right_node, desired_value, i, j + 1, visited_nodes)

        if current_node.bottom_left:
            bottom_left_node = current_node.bottom_left
            if bottom_left_node.value == desired_value:
                current_node.bottom_left_score = bottom_left_node.bottom_left_score + 1
                if not bottom_left_node.visited:
                    self.traverse(bottom_left_node, desired_value, i + 1, j - 1, visited_nodes)

        if current_node.bottom:
            bottom_node = current_node.bottom
            if bottom_node.value == desired_value:
                current_node.bottom_score = bottom_node.bottom_score + 1
                if not bottom_node.visited:
                    self.traverse(bottom_node, desired_value, i + 1, j, visited_nodes)

        if current_node.bottom_right:
            bottom_right_node = current_node.bottom_right
            if bottom_right_node.value == desired_value:
                current_node.bottom_right_score = bottom_right_node.bottom_right_score + 1
                if not bottom_right_node.visited:
                    self.traverse(bottom_right_node, desired_value, i + 1, j + 1, visited_nodes)


class ViewGame(object):


    def __init__(self, width=640, height=400, frames_sec=40):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.clock = pygame.time.Clock()
        self.frames_sec = frames_sec
        self.time_play = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        self.Comptrain = None
        self.win_list = [0, 0]

    def init_game_var(self, game_mode):

        self.board_game = Board(BOARD_SIZE[0], BOARD_SIZE[1])
        (self.board_rows, self.board_cols) = self.board_game.getdimension()
        self.game_logic = Logic_game(self.board_game)
        firstcoin = random.randint(1, 2)
        secondcoin = 2 if firstcoin == 1 else 1

        if game_mode == "single":
            self.p1 = HumanPlayer(firstcoin)
            if (self.Comptrain == None):
                self.p2 = ComputerPlayer(secondcoin, "qlearner")
                self.Comptrain = self.p2
            else:
                self.Comptrain.set_coin_type(secondcoin)
                self.p2 = self.Comptrain
        elif game_mode == "two_player":
            self.p1 = HumanPlayer(firstcoin)
            self.p2 = HumanPlayer(secondcoin)
        else:
            self.Comptrain = None
            self.win_list = [0, 0]
            self.p1 = ComputerPlayer(firstcoin, "qlearner")
            self.p2 = ComputerPlayer(secondcoin, "qlearner")

    def main_menu(self, iterations=20):

        main_menu = True
        play_game = False
        self.background.fill(WHITE)
        self.draw_menu()

        while main_menu:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.rect1.collidepoint(pos):
                        play_game = True
                        main_menu = False
                        game_mode = "two_player"

                    elif self.rect2.collidepoint(pos):
                        play_game = True
                        main_menu = False
                        game_mode = "single"

                    elif self.rect3.collidepoint(pos):
                        play_game = True
                        main_menu = False
                        game_mode = "train"

                    elif self.rect4.collidepoint(pos):
                        main_menu = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        main_menu = False

            milliseconds = self.clock.tick(self.frames_sec)
            self.time_play += milliseconds / 1000.0
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

        if not play_game:
            pygame.quit()

        elif game_mode == "train":
            self.run(game_mode, iterations)

        else:
            self.run(game_mode)

    def run(self, game_mode, iterations=1):

        while (iterations > 0):
            self.init_game_var(game_mode)
            self.background.fill(BLACK)
            self.board_game.draw(self.background)
            game_over = False
            turn_ended = False
            uninitialized = True
            current_type = random.randint(1, 2)
            if game_mode == "single":
                human_turn = (self.p1.get_coin_type() == current_type)

            elif game_mode == "two_player":
                human_turn = True

            else:
                human_turn = False

            p1_turn = (self.p1.get_coin_type() == current_type)

            (first_slot_X, first_slot_Y) = self.board_game.get_slot(0, 0).get_position()
            coin = Coin(current_type)
            completed_screen = False
            while not game_over:

                if uninitialized:
                    coin = Coin(current_type)
                    coin.set_position(first_slot_X, first_slot_Y - Slot.SIZE)
                    coin.set_column(0)
                    uninitialized = False
                    insertcoin = False

                coin.draw(self.background)

                current_player = self.p1 if p1_turn else self.p2

                if not human_turn:
                    game_over = current_player.complete_move(coin, self.board_game, self.game_logic, self.background)
                    insertcoin = True
                    uninitialized = True

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_over = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            game_over = True
                        if event.key == pygame.K_RIGHT and human_turn:
                            if (coin.get_column() + 1 < self.board_cols):
                                coin.move_right(self.background)

                        elif event.key == pygame.K_LEFT and human_turn:
                            if (coin.get_column() - 1 >= 0):
                                coin.move_left(self.background)

                        elif event.key == pygame.K_RETURN and human_turn and not insertcoin:
                            try:
                                game_over = self.board_game.insert_coin(coin, self.background, self.game_logic)
                                current_player.complete_move()
                                uninitialized = True
                                insertcoin = True

                            except Full_colm_exception as e:
                                pass

                if game_over:
                    winner = self.game_logic.determine_winner_name()
                    winner_value = self.game_logic.get_winner()
                    if (winner_value > 0 and game_mode == "train"):
                        self.win_list[winner_value - 1] += 1
                    completed_screen = True

                if insertcoin:
                    if game_mode == "single":
                        human_turn = not human_turn
                    current_type = 1 if current_type == 2 else 2
                    p1_turn = not p1_turn

                milliseconds = self.clock.tick(self.frames_sec)
                self.time_play += milliseconds / 1000.0
                pygame.display.flip()
                self.screen.blit(self.background, (0, 0))

            iterations -= 1

        if game_mode == "train":
            index = self.win_list.index(max(self.win_list))
            self.Comptrain = self.p1 if index == 0 else self.p2
            self.main_menu()

        else:
            self.game_over_view(winner)

    def draw_menu(self):

        font = pygame.font.SysFont('comicsansms', 90, bold=True)
        self.title_surface = font.render('CONNECT-4', True, BLACK)
        fw, fh = font.size('CONNECT 4')
        self.background.blit(self.title_surface, ((self.width - fw) // 2, 150))
        two_player_text = 'Two Player Mode'
        computer_player_text = 'Play with Computer'
        train_text = 'Train Computer'
        quit_text = 'Quit'
        font = pygame.font.SysFont('calibri', 40, bold=True)

        self.play_surface = font.render(two_player_text, True, RED)
        fw, fh = font.size(two_player_text)
        self.rect1 = self.play_surface.get_rect(topleft=((self.width - fw) // 2, 350))
        self.background.blit(self.play_surface, ((self.width - fw) // 2, 350))

        computer_play_surface = font.render(computer_player_text, True, BLUE)
        fw, fh = font.size(computer_player_text)
        self.rect2 = computer_play_surface.get_rect(topleft=((self.width - fw) // 2, 400))
        self.background.blit(computer_play_surface, ((self.width - fw) // 2, 400))

        self.train_surface = font.render(train_text, True, WHITE)
        fw, fh = font.size(train_text)
        self.rect3 = self.train_surface.get_rect(topleft=((self.width - fw) // 2, 700))
        self.background.blit(self.train_surface, ((self.width - fw) // 2, 700))

        self.quit_surface = font.render(quit_text, True, RED)
        fw, fh = font.size(quit_text)
        self.rect4 = self.quit_surface.get_rect(topleft=((self.width - fw) // 2, 450))
        self.background.blit(self.quit_surface, ((self.width - fw) // 2, 450))

    def game_over_view(self, winner):

        completed_screen = True
        main_menu = False
        self.background.fill(WHITE)
        self.draw_game_over(winner)

        while completed_screen:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.rect1.collidepoint(pygame.mouse.get_pos()):
                        main_menu = True
                        completed_screen = False

                    elif self.rect2.collidepoint(pygame.mouse.get_pos()):
                        completed_screen = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        completed_screen = False

            milliseconds = self.clock.tick(self.frames_sec)
            self.time_play += milliseconds / 1000.0
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

        if not main_menu:
            pygame.quit()

        else:
            self.main_menu()

    def draw_game_over(self, winner):
        """
        Draw the elements for the game over screen
        """
        font = pygame.font.SysFont('comicsansms', 80, bold=True)
        game_over_text = 'GAME OVER'
        self.title_surface = font.render(game_over_text, True, BLACK)
        fw, fh = font.size(game_over_text)
        self.background.blit(self.title_surface, ((self.width - fw) // 2, 150))
        play_again_text = 'Return to Main Menu'
        quit_text = 'Quit'
        if winner != 'Draw':
            winner_text = winner + " wins!"
        else:
            winner_text = "It was a " + winner + "!"
        font = pygame.font.SysFont('calibri', 40, bold=True)
        winner_surface = font.render(winner_text, True, BLACK)
        fw, fh = font.size(winner_text)
        self.background.blit(winner_surface, ((self.width - fw) // 2, 320))

        font = pygame.font.SysFont('calibri', 40, bold=False)
        self.play_surface = font.render(play_again_text, True, BLACK)
        fw, fh = font.size(play_again_text)
        self.rect1 = self.play_surface.get_rect(topleft=((self.width - fw) // 2, 400))
        self.background.blit(self.play_surface, ((self.width - fw) // 2, 400))

        self.quit_surface = font.render(quit_text, True, BLACK)
        fw, fh = font.size(quit_text)
        self.rect2 = self.quit_surface.get_rect(topleft=((self.width - fw) // 2, 480))
        self.background.blit(self.quit_surface, ((self.width - fw) // 2, 480))


class Player():


    def __init__(self, coin_type):

        self.coin_type = coin_type

    def complete_move(self):

        pass

    def get_coin_type(self):

        return self.coin_type

    def set_coin_type(self, coin_type):

        self.coin_type = coin_type


class HumanPlayer(Player):


    def __init__(self, coin_type):

        Player.__init__(self, coin_type)


class ComputerPlayer(Player):


    def __init__(self, coin_type, player_type):

        if (player_type == "random"):
            self.player = RandomPlayer(coin_type)
        else:
            self.player = QLearningPlayer(coin_type)

    def complete_move(self, coin, board, game_logic, background):

        actions = board.get_available_actions()
        state = board.get_state()
        chosen_action = self.choose_action(state, actions)
        coin.move_right(background, chosen_action)
        coin.set_column(chosen_action)
        game_over = board.insert_coin(coin, background, game_logic)
        self.player.learn(board, actions, chosen_action, game_over, game_logic)

        return game_over

    def get_coin_type(self):

        return self.player.get_coin_type()

    def choose_action(self, state, actions):

        return self.player.choose_action(state, actions)


class RandomPlayer(Player):


    def __init__(self, coin_type):

        Player.__init__(self, coin_type)

    def choose_action(self, state, actions):

        return random.choice(actions)

    def learn(self, board, action, game_over, game_logic):

        pass


class QLearningPlayer(Player):


    def __init__(self, coin_type, epsilon=0.2, alpha=0.3, gamma=0.9):

        Player.__init__(self, coin_type)
        self.q = {}
        self.epsilon = epsilon  # e-greedy chance of random exploration
        self.alpha = alpha  # learning rate
        self.gamma = gamma  # discount factor for future rewards

    def getQ(self, state, action):

        if self.q.get((state, action)) is None:
            self.q[(state, action)] = 1.0
        return self.q.get((state, action))

    def choose_action(self, state, actions):
        chosen_action = random.choice(actions)
        return chosen_action

    def learn(self, board, actions, chosen_action, game_over, game_logic):

        reward = 0
        if (game_over):
            win_value = game_logic.get_winner()
            if win_value == 0:
                reward = 0.5
            elif win_value == self.coin_type:
                reward = 1
            else:
                reward = -2
        prev_state = board.get_prev_state()
        prev = self.getQ(prev_state, chosen_action)
        result_state = board.get_state()
        maxqnew = max([self.getQ(result_state, a) for a in actions])
        self.q[(prev_state, chosen_action)] = prev + self.alpha * ((reward + self.gamma * maxqnew) - prev)


class Coin():


    RADIUS = 30

    def __init__(self, coin_type):

        self.coin_type = coin_type
        self.surface = pygame.Surface((Slot.SIZE - 3, Slot.SIZE - 3))
        if (self.coin_type == 1):
            self.color = YELLOW
        else:
            self.color = RED

    def set_position(self, x1, y1):

        self.x_pos = x1
        self.y_pos = y1

    def set_column(self, col):

        self.col = col

    def get_column(self):

        return self.col

    def set_row(self, row):

        self.row = row

    def get_row(self):

        return self.row

    def move_right(self, background, step=1):

        self.set_column(self.col + 1)
        self.surface.fill((0, 0, 0))
        background.blit(self.surface, (self.x_pos, self.y_pos))
        self.set_position(self.x_pos + step * Slot.SIZE, self.y_pos)
        self.draw(background)

    def move_left(self, background):

        self.set_column(self.col - 1)
        self.surface.fill((0, 0, 0))
        background.blit(self.surface, (self.x_pos, self.y_pos))
        self.set_position(self.x_pos - Slot.SIZE, self.y_pos)
        self.draw(background)

    def drop(self, background, row_num):

        self.set_row(row_num)
        self.surface.fill((0, 0, 0))
        background.blit(self.surface, (self.x_pos, self.y_pos))
        self.set_position(self.x_pos, self.y_pos + ((self.row + 1) * Slot.SIZE))
        self.surface.fill((255, 255, 255))
        background.blit(self.surface, (self.x_pos, self.y_pos))
        self.draw(background)

    def get_coin_type(self):

        return self.coin_type

    def draw(self, background):

        pygame.draw.circle(self.surface, self.color, (Slot.SIZE // 2, Slot.SIZE // 2), Coin.RADIUS)
        self.surface = self.surface.convert()
        background.blit(self.surface, (self.x_pos, self.y_pos))


class Logic_game():

    WIN_SEQUENCE_LENGTH = 4

    def __init__(self, board):

        self.board = board
        (no_of_rows, no_of_colms) = self.board.getdimension()
        self.board_rows = no_of_rows
        self.board_cols = no_of_colms
        self.winner_value = 0

    def check_game_over(self):

        (last_visited_nodes, player_value) = self.board.get_last_filled_information()
        representation = self.board.get_representation()
        player_won = self.search_win(last_visited_nodes, representation)
        if player_won:
            self.winner_value = player_value

        return (player_won or self.board.check_board())

    def search_win(self, last_visited_nodes, representation):

        for indices in last_visited_nodes:
            current_node = representation[indices[0]][indices[1]]
            if (current_node.top_left_score == Logic_game.WIN_SEQUENCE_LENGTH or
                    current_node.top_score == Logic_game.WIN_SEQUENCE_LENGTH or
                    current_node.top_right_score == Logic_game.WIN_SEQUENCE_LENGTH or
                    current_node.left_score == Logic_game.WIN_SEQUENCE_LENGTH or
                    current_node.right_score == Logic_game.WIN_SEQUENCE_LENGTH or
                    current_node.bottom_left_score == Logic_game.WIN_SEQUENCE_LENGTH or
                    current_node.bottom_score == Logic_game.WIN_SEQUENCE_LENGTH or
                    current_node.bottom_right_score == Logic_game.WIN_SEQUENCE_LENGTH):
                return True

        return False

    def determine_winner_name(self):

        if (self.winner_value == 1):
            return "BLUE"
        elif (self.winner_value == 2):
            return "RED"
        else:
            return "TIE"

    def get_winner(self):

        return self.winner_value


class SlotTrackerNode():


    def __init__(self):

        self.top_left = None
        self.top_right = None
        self.top = None
        self.left = None
        self.right = None
        self.bottom_left = None
        self.bottom = None
        self.bottom_right = None
        self.top_left_score = 1
        self.top_right_score = 1
        self.top_score = 1
        self.left_score = 1
        self.right_score = 1
        self.bottom_left_score = 1
        self.bottom_score = 1
        self.bottom_right_score = 1
        self.value = 0
        self.visited = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('iterations', nargs='?', default=20, action="store",
                        help="Store the number of iterations to train computer")
    args = parser.parse_args()

    ViewGame(1200, 760).main_menu(int(args.iterations))