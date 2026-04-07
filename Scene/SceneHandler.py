"""
SceneHandler — manages scene transitions and global game state.
"""
from Scene.MainScene import MainScene


class SceneHandler:
    def __init__(self, screen_h, screen_w):
        self.screen_h = screen_h
        self.screen_w = screen_w
        self.score  = 0
        self.banana = 0
        self.go("MAIN_SCENE")

    def go(self, scene_name):
        if scene_name == "MAIN_SCENE":
            self.scene = MainScene()
        elif scene_name == "PLAY_SCENE":
            from Scene.PlayScene import PlayScene
            self.scene = PlayScene(self.screen_w, self.screen_h)
        else:
            # Fall back to main menu for any unknown scene
            self.scene = MainScene()
        self.scene.handler = self
