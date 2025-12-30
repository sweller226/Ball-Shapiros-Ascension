from time import sleep
from support import *
from player import *
from settings import *
import os

class Level:
    def __init__(self, levelData, surface):
        self.levelMode = "Menu"
        self.levelData = levelData
        self.display_surface = surface

        self.Menu = slide()
        Text(100, 100, 100, 100, """Ball Shapiros Ascension""", 70, self.Menu)
        Text(110, 210, 100, 100, """Made By Steven Weller""", 30, self.Menu, True)
        Button(SCREEN_WIDTH/2-110, 350, 300, 100, """Ascend""", 50, self.Menu)
        Button(SCREEN_WIDTH/2-130, 500, 300, 100, """Controls""", 50, self.Menu)

        # pause screen
        self.pauseScreen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.pauseScreen.set_alpha(10) 
        self.pauseScreen.fill((20,20,20))

        self.pause = slide()
        Text(475, 300, 100, 100, """Paused""", 70, self.pause)

        self.controls = slide()
        Text(450, 100, 100, 100, """Controls""", 70, self.controls)
        Text(240, 300, 100, 100, """Jump - Hold left click to jump, where you release your mouse will be the peak of your jump""", 30, self.controls, True)
        Text(325, 400, 100, 100, """Power Bar - How long you hold will determine % power of jump""", 30, self.controls, True)
        Text(350, 500, 100, 100, """Pause - Press 'p' to enter pause, press 'o' to exit pause""", 30, self.controls, True)

        Button(575, 600, 200, 100, """Back""", 40, self.controls)

    def run(self):
        match self.levelMode:
            case "Menu":
                self.mainMenu()
            case "Controls":
                self.draw_control()
            case "Game":
                self.timeKeeper()
                self.draw_level()
                self.player.update()
                self.endingTest()
                self.pauseTest()
                
            case "Ending":
                self.endScreen()
            
            case "Pause":
                self.pauseTest()
                self.draw_pauseScreen()
    
    def draw_control(self):
        mousePos = pygame.mouse.get_pos()
        for text in self.controls.textList:
            text.draw()
        for button in self.controls.buttonList:
            button.draw()
            if button.rect.collidepoint(mousePos) and pygame.mouse.get_pressed()[0]:
                self.levelMode = "Menu"                

    def pauseTest(self):
        if pygame.key.get_pressed()[pygame.K_p]:
            if self.levelMode == "Game":
                self.levelMode = "Pause"
        
        if pygame.key.get_pressed()[pygame.K_o]:
            if self.levelMode == "Pause":
                self.levelMode = "Game"

        
    def draw_pauseScreen(self):
        self.display_surface.blit(self.pauseScreen, (0, 0))

        for text in self.pause.textList:
            text.draw()


    def calculateTime(self):
        hours = math.floor(self.time/60**3)
        hoursRemainder = self.time%60**3

        minutes = math.floor(hoursRemainder/60**2)
        minutesRemainder = self.time%60**2

        seconds = math.floor(minutesRemainder/60)

        timeDisplay = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return timeDisplay
    
    def timeKeeper(self):
        self.time += 1
        self.saveTime()

        timeDisplay = self.calculateTime()
        debug(timeDisplay)
    
    def mainMenu(self):
        self.display_surface.fill("Black")
        mousePos = pygame.mouse.get_pos()
        for button in self.Menu.buttonList:
            button.draw()
            if button.rect.collidepoint(mousePos) and pygame.mouse.get_pressed()[0]:
                if button.info == "Ascend":
                        self.sprites = {}
                        self.backgroundColour = BACKGROUND_COL
                        self.gameRect = pygame.Rect(SCREEN_WIDTH*0.25, 0, WIDTH, HEIGHT)

                        for i in self.levelData:
                            self.sprites[i] = create_tile_group(import_csv_layout(self.levelData[i]), i)

                        self.player_Group = pygame.sprite.GroupSingle()
                        self.loadPlayer()
                        self.loadTime()

                        self.player_Group.add(self.player)
                        self.sprites["Player"] = self.player_Group

                        self.display_surface.fill("Black")
                        pygame.display.update()
                        sleep(1)
                        self.levelMode = "Game"
                if button.info == "Controls":
                    self.levelMode = "Controls"

    def loadTime(self):
        try:
            with open('./timedata.txt', 'x') as f:
                self.time = 0
                f.close()
        except:
            with open('./timedata.txt') as f:
                data = f.readlines()
                self.time = float(data[0])
                f.close()

    def saveTime(self):
        with open('./timedata.txt', 'w') as f:
            f.write(str(self.time) + "\n")
            f.close()
    
    def loadPlayer(self):
        try:
            with open('./playerData.txt') as f:
                data = f.readlines()
                self.player = Player(float(data[0]), float(data[1]), self.sprites, float(data[2]), float(data[3]))
                f.close()
        except:
            self.player = Player(level.playerSpawn[0], level.playerSpawn[1], self.sprites, 0, HEIGHT*0.6)
            

    def endScreen(self):
        self.display_surface.fill("Black")
        mousePos = pygame.mouse.get_pos()

        for text in self.end.textList:
            text.draw()
        for button in self.end.buttonList:
            button.draw()
            if button.info == "Restart":
                if button.rect.collidepoint(mousePos) and pygame.mouse.get_pressed()[0]:
                    self.time = 0
                    del self.player
                    os.remove("./playerData.txt")
                    os.remove("./timedata.txt")
                    self.sprites = {}
                    self.backgroundColour = BACKGROUND_COL

                    for i in self.levelData:
                        self.sprites[i] = create_tile_group(import_csv_layout(self.levelData[i]), i)

                    self.player_Group = pygame.sprite.GroupSingle()
                    self.loadPlayer()

                    self.player_Group.add(self.player)
                    self.sprites["Player"] = self.player_Group

                    self.display_surface.fill("Black")
                    pygame.display.update()
                    sleep(1)
                    self.levelMode = "Game"
        for image in self.end.imageList:
            image.draw()



    def endingTest(self):
        if self.player.playerHeight/TILE_SIZE < 350:
            self.endTransition()
            self.display_surface.fill("Black")
        elif self.player.playerHeight/TILE_SIZE < 392:
            self.player.gravity = 0.01
        else:
            self.player.gravity = 0.2


    def endTransition(self):
        self.levelMode = "Ending"
        self.end = slide()

        Text(210, 100, 100, 100, "You Have Ascended", 70, self.end)
        endTime = self.calculateTime()
        Text(SCREEN_WIDTH/2 - 150, 300, 100, 100, f"Your Time Was {endTime}", 30, self.end, True)
        # image(200, 400, "../Graphics/Placeholder/BenShapiro_Smug.jpg", self.end)
        Button(SCREEN_WIDTH/2 - 140, 400, 300, 100, f"Restart", 50, self.end)
    
    def draw_level(self):
        pygame.draw.rect(self.display_surface, BACKGROUND_COL, self.gameRect)

        for i in drawOrder:
            if i == "Player":
                self.player.trail()
                self.sprites[i].draw(self.display_surface)

            elif i == "D_Crystal":
                for crystal in self.sprites[i]:
                    crystal.draw(self.display_surface)
            
            elif i in ["Slime", "Decoration", "Decoration2", "Decoration3"]:
                self.sprites[i].draw(self.display_surface)


class slide():
    def __init__(self):
        self.buttonList = []
        self.textList = []
        self.imageList = []


class Button:
    def __init__(self, x, y, sizeX, sizeY, text, fontSize, slide):
        self.rect = pygame.rect.Rect(x, y, sizeX, sizeY)
        self.info = text
        self.bgCol = "Black"
        self.textFont = pygame.font.Font("./Graphics/Fonts/streamer-font/StreamerSlantDemo-WyrX4.otf", fontSize)
        self.text = self.textFont.render(self.info, True, "White", self.bgCol)
        slide.buttonList.append(self)
        self.slide = slide
    
    def draw(self):
        self.text = self.textFont.render(self.info, True, "White", self.bgCol)
        mousePos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mousePos):
            self.text = self.textFont.render(self.info, True, "Yellow", self.bgCol)
        pygame.display.get_surface().blit(self.text, self.rect)

class Text(Button):
    def __init__(self, x, y, sizeX, sizeY, text, fontSize, slide, num = False):
        super().__init__(x, y, sizeX, sizeY, text, fontSize, slide)
        if num:
            self.textFont = pygame.font.SysFont('freesansbold.ttf', fontSize)
        slide.textList.append(self)
    
    def draw(self):
        self.text = self.textFont.render(self.info, True, "White", self.bgCol)
        pygame.display.get_surface().blit(self.text, self.rect)


class image():
    def __init__(self, x, y, image, slide):
        self.image = pygame.image.load(image).convert()
        self.pos = [x, y]
        self.rect = pygame.rect.Rect(x, y, 100, 100)
        slide.imageList.append(self)
    def draw(self):
        pygame.display.get_surface().blit(self.image, self.rect)


        

    



