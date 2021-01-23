
#@author: medoug7

import keras
from keras.layers import Dense, Activation, Dropout
from keras.models import Sequential, load_model
from keras.optimizers import Adam
import numpy as np

# guarda info dos estados, memória, recompensa
class Replay(object):
	# tamanho da memória, shape do ambiente, nº ações, espaço de ações discreto ou cotínuo
	def __init__(self, max_size, input_shape, n_actions, discrete=False):
		self.mem_size = max_size
		self.mem_ct = 0
		self.discrete = discrete
		# estado atual
		self.state_mem = np.zeros((self.mem_size, input_shape))
		# próximo estado
		self.new_state = np.zeros((self.mem_size, input_shape))
		
		dtype = np.int8 if self.discrete else np.float32
		# memória das ações
		self.act_mem = np.zeros((self.mem_size, n_actions), dtype=dtype)
		# recompensas
		self.rew_mem = np.zeros(self.mem_size)
		# memória do último estado
		self.termin_memory = np.zeros(self.mem_size, dtype=dtype)

	# função pra adicionar as coisas na memória
	def keep(self, state, action, reward, n_state, done):
		i = self.mem_ct % self.mem_size
		self.state_mem[i] = state
		self.new_state[i] = n_state
		self.rew_mem[i] = reward
		self.termin_memory[i] = 1 - int(done)
		if self.discrete:
			# salvar a ação como vetor one-hot
			actions = np.zeros(self.act_mem.shape[1])
			actions[action] = 1.0
			self.act_mem[i] = actions
		else:
			self.act_mem[i] = action
		self.mem_ct += 1

	# pega uma amostra aloeatória da memória para o treino
	def sample(self, batch_size):
		max_mem = min(self.mem_ct, self.mem_size)
		batch = np.random.choice(max_mem, batch_size)

		states = self.state_mem[batch]
		n_states = self.new_state[batch]
		rewards = self.rew_mem[batch]
		actions = self.act_mem[batch]
		terminal = self.termin_memory[batch]

		return states,actions,rewards,n_states,terminal


# construir a rede
def build_dqn(lr, n_actions, input_dim, fc1_dim, fc2_dim, fc3_dim):
	model = Sequential([
				Dense(fc1_dim, input_shape=(input_dim, )),
				Activation('linear'),
				Dropout(0.1),
				Dense(fc2_dim),
				Activation('relu'),
				Dropout(0.1),
				Dense(fc3_dim),
				Activation('relu'),
				Dense(n_actions)
				])

	model.compile(optimizer=Adam(lr=lr), loss='mse')

	return model


# o agente e o treino
class Agent(object):
	def __init__(self, lr, gamma, n_actions, batch_size,
					input_dim, eps, eps_dec=0.996, eps_min=0.01,
					mem_size=100000, fname='dqn_model.h5'):
		self.action_space = [i for i in range(n_actions)]
		self.lr = lr
		self.gamma = gamma
		self.eps = eps
		self.eps_dec = eps_dec
		self.eps_min = eps_min
		self.batch_size = batch_size
		self.file = fname

		# camadas
		self.input_dim = input_dim
		self.fc1_dim = 32
		self.fc2_dim = 16
		self.fc3_dim = 8
		self.n_actions = n_actions


		# memória
		self.mem = Replay(mem_size, input_dim, n_actions, discrete=True)
		# rede neural
		self.q_eval = build_dqn(lr, n_actions, input_dim, self.fc1_dim, self.fc2_dim, self.fc3_dim)
		# rede neural previsão
		self.q_aim = build_dqn(lr, n_actions, input_dim, self.fc1_dim, self.fc2_dim, self.fc3_dim)
		

	# guarda na memória
	def remember(self, state, action, reward, n_state, done):
		self.mem.keep(state, action, reward, n_state, done)

	# age
	def choose(self, state):
		# reshape pra acomodar o batch_size
		state = state[np.newaxis, :]
		rand = np.random.random()
		# explore or exploit
		if rand < self.eps:
			action = np.random.choice(self.action_space)
		else:
			q = self.q_eval.predict(state)
			action = np.argmax(q)

		return action

	# treina Double Deep-Q Network
	def learn_D(self):
		# espera a memória encher um batch
		if self.mem.mem_ct < self.batch_size:
			return
		
		# pega as info
		state, action, reward, n_state, not_done = self.mem.sample(self.batch_size)

		# vetor
		action_v = np.array(self.action_space, dtype=np.int8)
		# indice
		action_i = np.dot(action, action_v)

		# prever melhor ação pro próximo estado
		q_eval = self.q_eval.predict(n_state)
		q_next = self.q_aim.predict(n_state)

		# prever melhor ação pro estado atual
		q_pred = self.q_eval.predict(state)

		max_actions = np.argmax(q_eval, axis=1)
		
		batch_i = np.arange(self.batch_size, dtype=np.int32)
		
		# ação alvo que leva em conta recompensa futura
		q_target = q_pred
		q_target[batch_i, action_i] = reward + self.gamma*q_next[batch_i, max_actions.astype(int)]*not_done

		# realiza o treino
		_ = self.q_eval.fit(state, q_target, verbose=0)

		# diminui a exploração
		self.eps = max(self.eps_min, self.eps_dec*self.eps)


	# atualizar a rede alvo
	def update_aim(self, tau=0.01):
		# espera a memória encher um batch
		if self.mem.mem_ct < self.batch_size:
			return

		eval_w = np.array(self.q_eval.get_weights(), dtype=object)
		aim_w = np.array(self.q_aim.get_weights(), dtype=object)

		# novos pesos são uma "media ponderada"
		new_w = tau*eval_w + (1-tau)*aim_w
		self.q_aim.set_weights(new_w)


	# função pra atualizar a taxa de aprendizagem
	def update_lr(self, new_lr):
		weights = np.array(self.q_eval.get_weights(), dtype=object)

		# reseta a rede neural com nova lr
		self.q_eval = build_dqn(new_lr, self.n_actions, self.input_dim, self.fc1_dim, self.fc2_dim, self.fc3_dim)
		self.q_aim.set_weights(weights)
		self.lr = new_lr

		

	def save(self):
		self.q_eval.save(self.file)

	def load(self):
		self.q_eval = load_model(self.file)


