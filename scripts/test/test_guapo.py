from env.nav_env import NavEnv, line_world_obstacles
from scipy.stats import multivariate_normal as mvn
from agent.agent import Agent
import numpy as np


def test_lineworld():
    goal = np.array((0.4, 0.5))
    ne = NavEnv(start=np.array((0.1, 0.1)), goal=goal, obstacles=line_world_obstacles(goal))
    ne.render()


def test_achieve_goal():
    agent = Agent(show_training=True)
    goal = np.array((0.4, 0.5))
    start=np.array((0.1, 0.1))
    agent, ne = make_agent_and_ne(start=start, goal=goal)
    agent.achieve_goal(ne, goal, N=10)


def test_model_based_traj():
    agent = Agent(show_training=True)
    goal = np.array((0.4, 0.5))
    start=np.array((0.1, 0.1))
    agent, ne = make_agent_and_ne(start=start, goal=goal)
    nsteps = 40
    s0 = np.concatenate([ne.get_pos(), ne.get_vel()])
    mb_xs = agent.model_based_trajectory(s0, ne, nsteps=nsteps)
    ne.plot_path(mb_xs.T)


def test_model_based_policy():
    agent = Agent(show_training=True)
    goal = np.array((0.4, 0.5))
    start=np.array((0.85, 0.1))
    agent, ne = make_agent_and_ne(goal=goal, start=start)
    nsteps = 40
    s0 = np.concatenate([ne.get_pos(), ne.get_vel()])
    s = s0
    agent.model_based_policy(s, ne, nsteps=40, recompute_rmp=True)
    for i in range(nsteps):
        action = agent.model_based_policy(s, ne, recompute_rmp=False)
        print(action, "action")
        ne.step(action)
    ne.render(flip=True)
    resp = input("confirm looks good: \n")
    assert ("y" in resp)


def test_get_obs():
    goal = np.array((0.1, 0.3))
    obstacles = line_world_obstacles(goal)
    ne = NavEnv(start=np.array((0.1, 0.28)), goal=goal, obstacles=obstacles)
    ne.render()
    grid = ne.get_obs()
    from PIL import Image
    im = Image.fromarray(grid)
    im.resize((400, 400)).show()
    resp = input("confirm looks good: \n")
    assert ("y" in resp)


def test_model_free():
    goal = np.array((0.1, 0.3))
    start = np.array((0.1, 0.25))
    agent, ne = make_agent_and_ne(goal=goal, start=start)
    nsteps = 40
    agent.model_free_policy(ne, n_epochs=40, train=True)
    ne.reset()
    ne.setup_visuals()
    for i in range(nsteps):
        action = agent.model_free_policy( ne, n_epochs=1, train=False)
        ne.step(action)
        if i % 10 == 0:
            print("action", action)
            print("goal distance", ne.goal_distance())
            print("position", ne.agent.position)
            ne.render_start_goal()
    print("goal distance", ne.goal_distance())
    assert (ne.goal_condition_met())
    ne.render()
    print("Test passed")


def test_mb_mf_switch():
    goal = np.array((0.1, 0.4))
    agent, ne = make_agent_and_ne(goal=goal)
    ne.reset()
    ne.setup_visuals()
    agent.achieve_goal(ne, goal,  N = 200)
    print("goal distance", ne.goal_distance())
    assert (ne.goal_condition_met())
    print("Test passed")

def test_collect_autoencoder_data():
    agent, ne = make_agent_and_ne()
    samples = agent.collect_autoencoder_data(ne, n_data=3)
    from PIL import Image
    for sample in samples:
        print("sample shape", sample.shape)
        img = Image.fromarray(sample).resize((300,300))
        img.show()
        resp = input("Does the image look reasonably useful?")
        assert ("y" in resp)

def test_autoencoder_training():
    agent, ne = make_agent_and_ne()
    agent.train_autoencoder(ne, n_data = 80, n_epochs=2000)
    return agent, ne

def test_encoder_online():
    agent, ne = make_agent_and_ne()
    res_far = agent.autoencode(ne.get_obs())
    while not agent.is_in_s_uncertain(ne):
        action = agent.model_based_policy(ne.get_state(),ne)
        ne.step(action)
    res_near = agent.autoencode(ne.get_obs())
    assert not np.allclose(res_far, res_near)
    action = agent.random_policy(ne)
    ne.step(action, dt = 0.5)
    res_random = agent.autoencode(ne.get_obs())
    print(res_random, "res_random")
    print(res_near, "res_near")
    assert not np.allclose(res_random, res_near)


def make_agent_and_ne(goal=None, start = None):
    goal = np.array((0.1, 0.4)) if goal is None else goal
    obstacles = line_world_obstacles(goal)
    obs_center = [obstacles[0].origin[0] + obstacles[0].x / 2.0, obstacles[0].origin[1]]
    cov = 0.001
    goal_prior = mvn(mean=goal, cov=cov)  # prior on the center of the line in xy space
    agent = Agent(show_training=True)
    agent.belief.in_s_uncertain = goal_prior
    start = np.array((0.1, 0.1)) if start is None else start
    ne = NavEnv(start=start, goal=goal, obstacles=obstacles, gridsize=[10 * 50, 10 * 70], visualize=False)
    return agent, ne
test_model_free()
#test_encoder_online()