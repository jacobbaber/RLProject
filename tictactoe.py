import numpy as np
import json
import matplotlib.pyplot as plt

#Tic Tac Toe Board
#0 = Empty space, 1 = X's, 2 = O's


class State:
    def __init__(self, p1, p2):
        self.board = [0,0,0,0,0,0,0,0,0]
        self.p1 = p1
        self.p2 = p2
        self.gameOver = False
        self.boardHash = None
        self.playerSymbol = 1

    def printBoardState(self):
        print("-------------")
        print("| " + self.getSymbolAtIndex(0) + " | " + self.getSymbolAtIndex(1) + " | " + self.getSymbolAtIndex(2) + " |")
        print("-------------")
        print("| " + self.getSymbolAtIndex(3) + " | " + self.getSymbolAtIndex(4) + " | " + self.getSymbolAtIndex(5) + " |")
        print("-------------")
        print("| " + self.getSymbolAtIndex(6) + " | " + self.getSymbolAtIndex(7) + " | " + self.getSymbolAtIndex(8) + " |")
        print("-------------")

    def getHash(self):
          self.boardHash = str(self.board)
          return self.boardHash

    def getSymbolAtIndex(self, index):
        if self.board[index] == 0:
                return " "
        elif self.board[index] == 1:
                return "X"
        else:
                return "O"
        
    def availablePositions(self):
        positions = []
        for cell in range(len(self.board)):
                if self.board[cell] == 0:
                      positions.append(cell)
        return positions
    
    def updateState(self, index):
        self.board[index] = self.playerSymbol

        if self.playerSymbol == 1:
             self.playerSymbol = 2
        else:
             self.playerSymbol = 1

    def reset(self):
          self.board = [0,0,0,0,0,0,0,0,0]
          self.boardHash = None
          self.gameOver = False
          self.playerSymbol = 1

    def winner(self):
        # rows
        for row in range(3):
                if self.board[row*3] == self.board[row*3 + 1] == self.board[row*3+2] != 0:
                      self.gameOver = True
                      return self.board[row*3]
                
        # columns
        for col in range(3):
                if self.board[col] == self.board[col + 3] == self.board[col + 6] != 0:
                      self.gameOver = True
                      return self.board[col]
        
        # diagonals
        if (self.board[0] == self.board[4] == self.board[8] != 0) or (self.board[2] == self.board[4] == self.board[6] != 0):
              self.gameOver = True
              return self.board[4]
        
        if len(self.availablePositions()) == 0:
              self.gameOver = True
              return 0
        
        self.gameOver = False
        return None

    def giveReward(self):
        result = self.winner()

        if result == 1:
            self.p1.feedReward(1)
            self.p2.feedReward(-1)

        elif result == 2:
            self.p1.feedReward(-1)
            self.p2.feedReward(1)
        else:
              self.p1.feedReward(0)
              self.p2.feedReward(0)

    def playAgent(self, episodes = 100):
          for i in range(episodes):
                if i % 1000 == 0:
                      print("Rounds {}".format(i))
                while not self.gameOver:
                      # Player 1
                      positions = self.availablePositions()
                      p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
                      #take action and update board state
                      self.updateState(p1_action)
                      board_hash = self.getHash()
                      self.p1.addState(board_hash)

                      # check if game is over

                      win = self.winner()
                      if win is not None:
                            # self.showBoard()
                            # ended with p1 either win or draw
                            self.giveReward()
                            self.p1.reset()
                            self.p2.reset()
                            self.reset()
                            break
                      

                      else: 
                            # Player 2
                            positions = self.availablePositions()
                            p2_action = self.p2.chooseAction(positions, self.board, self.playerSymbol)
                            self.updateState(p2_action)
                            board_hash = self.getHash()
                            self.p2.addState(board_hash)


                            win = self.winner()
                            if win is not None:
                                  # ended with p2 either win or draw
                                  self.giveReward()
                                  self.p1.reset()
                                  self.p2.reset()
                                  self.reset()
                                  break
                            
    def playHuman(self):
          while not self.gameOver:
                # Player 1
                positions = self.availablePositions()
                p1_action = self.p1.chooseAction(positions, self.board, self.playerSymbol)
                # take action and update board state
                self.updateState(p1_action)
                board_hash = self.getHash()
                self.p1.addState(board_hash)
                self.printBoardState()
                
                win = self.winner()
                if win is not None:
                    if win == 1:
                        print(self.p1.name, "wins!")
                    elif win == 2:
                        print(self.p2.name, "wins!")
                    else:
                          print("Tie!")
                    self.giveReward()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break

                else:
                      #Player 2
                      positions = self.availablePositions()
                      p2_action = self.p2.chooseAction(positions)

                      self.updateState(p2_action)
                      
                      board_hash = self.getHash()
                      self.p2.addState(board_hash)
                      self.printBoardState()

                      win = self.winner()
                      if win is not None:
                            if win == 1:
                                print(self.p1.name, "wins!")
                            elif win == 2:
                                print(self.p2.name, "wins!")
                            else:
                                print("tie!")
                            self.giveReward()
                            self.p1.reset()
                            self.p2.reset()
                            self.reset()
                            break
                      

class Agent:
    def __init__(self, name, epsilon=.1):
            self.name = name
            self.states = []
            self.alpha = 0.1
            self.epsilon = epsilon
            self.gamma = 0.9
            self.states_value = {}
            self.numEpisodes = 0
            self.averageReward = []
            self.totalReward = 0



    def chooseAction(self, nextStates, current_board, symbol):
        if np.random.uniform(0, 1) <= self.epsilon:
                # take random action
            idx = np.random.choice(len(nextStates))
            action = nextStates[idx]
        else:
              max_value = -999
              for s in nextStates:
                    next_board = current_board.copy()
                    next_board[s] = symbol
                    next_boardHash = self.getHash(next_board)
                    if self.states_value.get(next_boardHash) is None:
                          value = 0
                    else:
                          value = self.states_value.get(next_boardHash)

                    if value >= max_value:
                          max_value = value
                          action = s
        
        return action
    
    def addState(self, state):
        self.states.append(state)

    def reset(self):
        self.states = []
    
    def feedReward(self, reward):
          self.numEpisodes = self.numEpisodes + 1
          self.totalReward = self.totalReward + reward

          self.averageReward.append(self.totalReward/self.numEpisodes)
      
          terminalState = True
          for s in reversed(self.states):
                if self.states_value.get(s) is None:
                    self.states_value[s] = 0
                if terminalState is True:
                  self.states_value[s] = self.states_value[s] + self.alpha * (reward - self.states_value[s])
                  terminalState = False
                else:
                     self.states_value[s] = self.states_value[s] + self.alpha * (self.gamma * reward - self.states_value[s])
                     
                reward = self.states_value[s]

    def getHash(self, board):
          boardHash = str(board)
          return boardHash

    def savePolicy(self):
          fw = open('policy_' + str(self.name) + '.json', 'w')
          json.dump(self.states_value, fw)
          fw.close()

    def loadPolicy(self, file):
          fr = open(file)
          self.states_value = json.load(fr)
          fr.close()


class RandomAgent:
    def __init__(self, name, epsilon=.1):
            self.name = name
            self.states = []
            self.alpha = 0.1
            self.epsilon = epsilon
            self.gamma = 0.9
            self.states_value = {}



    def chooseAction(self, nextStates, current_board, symbol):
            idx = np.random.choice(len(nextStates))
            action = nextStates[idx]
        
            return action
    
    def addState(self, state):
        self.states.append(state)

    def reset(self):
        self.states = []
    
    def feedReward(self, reward):
          pass

    def getHash(self, board):
          boardHash = str(board)
          return boardHash

    def savePolicy(self):
          pass

    def loadPolicy(self, file):
          pass

    
class HumanPlayer:
    def __init__(self, name):
        self.name = name

    def chooseAction(self, positions):
        while True:
              action = int(input("Enter your action"))
              if action in positions:
                    return action
              
    def addState(self, state):
          pass
    
    def feedReward(self, reward):
          pass
    
    def reset(self):
          pass
    
    def savePolicy(self):
         pass
    def loadPolicy(self):
         pass

agent = Agent("agent")

agent2 = Agent("agent2")

rando = RandomAgent("rando")

human = HumanPlayer("human")

st = State(rando, agent)

agent.loadPolicy('policy_agent.json')

st.playAgent(100000)

agent.savePolicy()

plt.plot(range(100000),agent.averageReward)

plt.xlabel("Episode")

plt.ylabel("Average total reward")

plt.xlim(10,100000)

plt.title("Average total reward of agent going first over 100,000 episodes versus random agent")
    
plt.show()                    
    
        


        
                
        
                      
                
                     

            
    
        
                
        

        


        



