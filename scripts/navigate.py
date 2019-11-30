from nav_env import NavEnv
from screwpipe import PipeGraspEnv
from agent import Agent
from pipe_agent import PipeAgent
import numpy as np

GOAL_THRESHOLD = 0.08
def test_cluster_one_simple():
    agent = Agent()
    agent.collect_planning_history()
    #TODO after this synthesize planning history
    agent.cluster_planning_history(k=1) #here the agent clusters trajectories to put them in the DMP
    goal = np.array((1,0.7))
    ne = NavEnv(start=np.array((0.2, 0.12)), goal = goal)
    imitation_path = agent.dmp_plan(ne.get_pos(), goal)
    ne.plot_path(imitation_path)
    agent.follow_path(ne, imitation_path)
    print("goal distance", np.linalg.norm(ne.get_pos()-goal))
    assert(np.linalg.norm(ne.get_pos()-goal) < GOAL_THRESHOLD)

def test_cluster_one_through_obstacles():
    agent = Agent()
    goal = np.array((1,1.4))
    agent.collect_planning_history(goals = (goal,))
    #TODO after this synthesize planning history
    agent.cluster_planning_history() #here the agent clusters trajectories to put them in the DMP
    ne = NavEnv(start=np.array((0.2, 0.12)), goal = goal)
    imitation_path = agent.dmp_plan(ne.get_pos(), goal)
    ne.plot_path(imitation_path)
    agent.follow_path(ne, imitation_path)
    print("goal distance", np.linalg.norm(ne.get_pos()-goal))
    assert(np.linalg.norm(ne.get_pos()-goal) < GOAL_THRESHOLD)


def test_cluster_two_simple():
    agent = Agent()
    agent.collect_planning_history(starts = (np.array((0.1,0.2)),np.array((0.05, 0.06))))
    #TODO after this synthesize planning history
    agent.cluster_planning_history(k=2) #here the agent clusters trajectories to put them in the DMP
    goal = np.array((1,0.67))
    ne = NavEnv(start=np.array((0.05, 0.06)), goal = goal)
    imitation_path = agent.dmp_plan(ne.get_pos(), goal)
    ne.plot_path(imitation_path)
    agent.follow_path(ne, imitation_path)
    print("goal distance", np.linalg.norm(ne.get_pos()-goal))
    assert(np.linalg.norm(ne.get_pos()-goal) < GOAL_THRESHOLD)

def test_cluster_many():
    agent = Agent(show_training=True)
    n_starts = 5
    goal = np.array((1.05,1.15))
    agent.collect_planning_history(starts = np.random.uniform(size=(n_starts, 2), low = 0, high = 0.7), goals = (goal,))
    #TODO after this synthesize planning history
    agent.cluster_planning_history(k=7) #here the agent clusters trajectories to put them in the DMP
    ne = NavEnv(start=np.array((0.05, 0.06)), goal = goal)
    imitation_path = agent.dmp_plan(ne.get_pos(), goal)
    ne.plot_path(imitation_path)
    agent.follow_path(ne, imitation_path)
    print("goal distance", np.linalg.norm(ne.get_pos()-goal))
    assert(np.linalg.norm(ne.get_pos()-goal) < GOAL_THRESHOLD)

def test_cluster_one_pipe_simple():
    agent = PipeAgent()
    agent.collect_planning_history()
    #TODO after this synthesize planning history
    agent.cluster_planning_history(k=1) #here the agent clusters trajectories to put them in the DMP
    import ipdb; ipdb.set_trace()
    pge = PipeGraspEnv(visualize=True)
    goal = np.array([0,0,0.1])
    imitation_path = agent.dmp_plan(pge.get_pos(), goal)
    agent.follow_path(pge, imitation_path)
    assert(pge.is_pipe_in_hole())

test_cluster_one_pipe_simple()

