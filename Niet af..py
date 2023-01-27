#  Module Imports
import pygame
import random       

#  Module Initialization
pygame.init()


#  Game Assets and Objects
class Ship:
    def __init__(self, name, img, pos, size, numGuns=0, gunPath=None, gunsize=None, gunCoordsOffset=None):
        self.name = name
        self.pos = pos
        #  Load the Vertical image
        self.vFoto = loadImage(img, size)
        self.vFotoWidth = self.vFoto.get_width()
        self.vFotoHeight = self.vFoto.get_height()
        self.vFotoRect = self.vFoto.get_rect()
        self.vFotoRect.topleft = pos
        #  Load the Horizontal image
        self.hFoto = pygame.transform.rotate(self.vFoto, -90)
        self.hFotoWidth = self.hFoto.get_width()
        self.hFotoHeight = self.hFoto.get_height()
        self.hFotoRect = self.hFoto.get_rect()
        self.hFotoRect.topleft = pos
        #  Image and Rectangle
        self.image = self.vFoto
        self.rect = self.vFotoRect
        self.rotation = False
        #  Ship is current selection
        self.active = False
        #  Load gun Images
        self.gunslist = []
        if numGuns > 0:
            self.gunCoordsOffset = gunCoordsOffset
            for num in range(numGuns):
                self.gunslist.append(
                    Guns(gunPath,
                         self.rect.center,
                         (size[0] * gunsize[0],
                          size[1] * gunsize[1]),
                         self.gunCoordsOffset[num])
                )


    def selectShipAndMove(self):
        """Selects the ship and moves it according to the mouse position"""
        while self.active == True:
            self.rect.center = pygame.mouse.get_pos()
            updateGameScreen(GAMESCREEN)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.checkForCollisions(pFleet):
                        if event.button == 1:
                            self.hFotoRect.center = self.vFotoRect.center = self.rect.center
                            self.active = False

                    if event.button == 3:
                        self.rotateShip()


    def rotateShip(self, doRotation=False):
        """switch ship between vertical and horizontal"""
        if self.active or doRotation == True:
            if self.rotation == False:
                self.rotation = True
            else:
                self.rotation = False
            self.switchImageAndRect()


    def switchImageAndRect(self):
        """Switches from Horizontal to Vertical and vice versa"""
        if self.rotation == True:
            self.image = self.hFoto
            self.rect = self.hFotoRect
        else:
            self.image = self.vFoto
            self.rect = self.vFotoRect
        self.hFotoRect.center = self.vFotoRect.center = self.rect.center


    def checkForCollisions(self, shiplist):
        """Check to make sure the ship is not colliding with any of the other ships"""
        slist = shiplist.copy()
        slist.remove(self)
        for item in slist:
            if self.rect.colliderect(item.rect):
                return True
        return False


    def checkForRotateCollisions(self, shiplist):
        """Check to make sure the ship is not going to collide with any other ship before rotating"""
        slist = shiplist.copy()
        slist.remove(self)
        for ship in slist:
            if self.rotation == True:
                if self.vFotoRect.colliderect(ship.rect):
                    return True
            else:
                if self.hFotoRect.colliderect(ship.rect):
                    return True
        return False


    def returnToDefaultPosition(self):
        """Returns the ship to its default position"""
        if self.rotation == True:
            self.rotateShip(True)

        self.rect.topleft = self.pos
        self.hFotoRect.center = self.vFotoRect.center = self.rect.center


    def snapToGridEdge(self, gridCoords):
        if self.rect.topleft != self.pos:

            #  Check to see if the ships position is outside of the grid:
            if self.rect.left > gridCoords[0][-1][0] + 50 or \
                    self.rect.right < gridCoords[0][0][0] or \
                    self.rect.top > gridCoords[-1][0][1] + 50 or \
                    self.rect.bottom < gridCoords[0][0][1]:
                self.returnToDefaultPosition()

            elif self.rect.right > gridCoords[0][-1][0] + 50:
                self.rect.right = gridCoords[0][-1][0] + 50
            elif self.rect.left < gridCoords[0][0][0]:
                self.rect.left = gridCoords[0][0][0]
            elif self.rect.top < gridCoords[0][0][1]:
                self.rect.top = gridCoords[0][0][1]
            elif self.rect.bottom > gridCoords[-1][0][1] + 50:
                self.rect.bottom = gridCoords[-1][0][1] + 50
            self.vFotoRect.center = self.hFotoRect.center = self.rect.center


    def snapToGrid(self, gridCoords):
        for rowX in gridCoords:
            for cell in rowX:
                if self.rect.left >= cell[0] and self.rect.left < cell[0] + CELLSIZE \
                        and self.rect.top >= cell[1] and self.rect.top < cell[1] + CELLSIZE:
                    if self.rotation == False:
                        self.rect.topleft = (cell[0] + (CELLSIZE - self.image.get_width()) // 2, cell[1])
                    else:
                        self.rect.topleft = (cell[0], cell[1] + (CELLSIZE - self.image.get_height()) // 2)

        self.hFotoRect.center = self.vFotoRect.center = self.rect.center


    def draw(self, window):
        """Draw the ship to the screen"""
        window.blit(self.image, self.rect)
        # pygame.draw.rect(window, (255, 0, 0), self.rect, 1)
        for guns in self.gunslist:
            guns.draw(window, self)


class Guns:
    def __init__(self, imgPath, pos, size, offset):
        self.orig_image = loadImage(imgPath, size, True)
        self.image = self.orig_image
        self.offset = offset
        self.rect = self.image.get_rect(center=pos)


    def update(self, ship):
        """Updating the Guns Positions on the ship"""
        self.rotateGuns(ship)
        if ship.rotation == False:
            self.rect.center = (ship.rect.centerx, ship.rect.centery + (ship.image.get_height()//2 * self.offset))
        else:
            self.rect.center = (ship.rect.centerx + (ship.image.get_width()//2 * -self.offset), ship.rect.centery)


    def _update_image(self, angle):
        self.image = pygame.transform.rotate(self.orig_image, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)


    def rotateGuns(self, ship):
        """Rotates the guns in relation to direction of the mouse cursor"""
        direction = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.rect.center)
        radius, angle = direction.as_polar()
        if not ship.rotation:
            if self.rect.centery <= ship.vFotoRect.centery and angle <= 0:
                self._update_image(angle)
            if self.rect.centery >= ship.vFotoRect.centery and angle > 0:
                self._update_image(angle)
        else:
            if self.rect.centerx <= ship.hFotoRect.centerx and (angle <= -90 or angle >= 90):
                self._update_image(angle)
            if self.rect.centerx >= ship.hFotoRect.centerx and (angle >= -90 and angle <= 90):
                self._update_image(angle)


    def draw(self, window, ship):
        self.update(ship)
        window.blit(self.image, self.rect)

class Button:
    def __init__(self, image, size, pos, msg):
        self.name = msg
        self.image = image
        self.imageLarger = self.image
        self.imageLarger = pygame.transform.scale(self.imageLarger, (size[0] + 10, size[1] + 10))  
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.radarUsed = 0
        self.active = False

        self.msg = self.addTekst(msg)
        self.msgRect = self.msg.get_rect(center = self.rect.center)
        
    def addTekst(self, msg):
        # voeg font toe aan de button

        font = pygame.font.SysFont('Arial', 22)
        message = font.render(msg, 1, (255, 255, 255))
        return message
    
    def focusOnButton(self, window):
        """Brings attention to which button is being focussed on"""
        if self.active:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                window.blit(self.imageLarger, (self.rect[0] - 5, self.rect[1] - 5, self.rect[2], self.rect[3]))
            else:
                window.blit(self.image, self.rect)


    def actionOnPress(self):
        """Which actions to take according to button selected"""
        if self.active:
            if self.name == 'Random Grid':
                self.randomizeShipPositions(pFleet, pGameGrid)
                self.randomizeShipPositions(cFleet, cGameGrid)
            elif self.name == 'Reset':
                self.resetShips(pFleet)
            elif self.name == 'Deploy':
                self.deploymentPhase()
            elif self.name == 'Redeploy':
                self.restartTheGame()

    
    def randomizeShipPositions(self, shiplist, gameGrid):
        """Calls the randomize ships function"""
        if DEPLOYMENT == True:
            randomizeShipPositions(shiplist, gameGrid)


    def resetShips(self, shiplist):
        """Resets the ships to their default positions"""
        if DEPLOYMENT == True:
            for ship in shiplist:
                ship.returnToDefaultPosition()


    def deploymentPhase(self):
        pass




    def draw(self, window):
        self.focusOnButton(window)
        window.blit(self.msg, self.msgRect)

class Player:
    def __init__(self):
        self.turn = True


    def makeAttack(self, grid, logicgrid):
        """When its the player's turn, the player must make an attacking selection within the computer grid."""
        posX, posY = pygame.mouse.get_pos()
        if posX >= grid[0][0][0] and posX <= grid[0][-1][0] + 50 and posY >= grid[0][0][1] and posY <= grid[-1][0][1] + 50:
            for i, rowX in enumerate(grid):
                for j, colX in enumerate(rowX):
                    if posX >= colX[0] and posX < colX[0] + 50 and posY >= colX[1] and posY <= colX[1] + 50:
                        if logicgrid[i][j] != ' ':
                            if logicgrid[i][j] == 'O':
                                TOKENS.append(Tokens(REDTOKEN, grid[i][j], 'Hit', None, None, None))
                                logicgrid[i][j] = 'T'
                                self.turn = False
                        else:
                            logicgrid[i][j] = 'X'
                            TOKENS.append(Tokens(GREENTOKEN, grid[i][j], 'Miss', None, None, None))
                            self.turn = False

class EasyComputer:
    def __init__(self):
        self.turn = False
        self.status = self.computerStatus('Thinking')
        self.name = 'Easy Computer'


    def computerStatus(self, msg):
        image = pygame.font.SysFont('Stencil', 22)
        message = image.render(msg, 1, (0, 0, 0))
        return message


    def makeAttack(self, gamelogic):
      rowX = random.randint(0, 9)
      rowY = random.randint(0, 9)
      if gamelogic[rowX][rowY] == ' ' or gamelogic[rowX][rowY] == 'O':
                        validChoice = True

      if gamelogic[rowX][rowY] == 'O':
                    TOKENS.append(
                        Tokens(REDTOKEN, pGameGrid[rowX][rowY], 'Hit', None))
                    gamelogic[rowX][rowY] = 'T'
                    self.generateMoves((rowX, rowY), gamelogic)
                    self.turn = False
      else:  
            gamelogic[rowX][rowY] = 'X'
            TOKENS.append(Tokens(BLUETOKEN, pGameGrid[rowX][rowY], 'Miss', None, None, None))
            self.turn = False

    def draw(self, window):
        if self.turn:
            window.blit(self.status, (cGameGrid[0][0][0] - CELLSIZE, cGameGrid[-1][-1][1] + CELLSIZE))

class Tokens:
    def __init__(self, image, pos, action, imageList=None, explosionList=None, soundFile=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        self.imageList = imageList
        self.explosionList = explosionList
        self.action = action
        self.soundFile = soundFile
        self.timer = pygame.time.get_ticks()
        self.imageIndex = 0
        self.explosionIndex = 0
        self.explosion = False


    def animate_Explosion(self):
        """Animating the Explosion sequence"""
        self.explosionIndex += 1
        if self.explosionIndex < len(self.explosionList):
            return self.explosionList[self.explosionIndex]
        else:
            return self.animate_fire()


   

    def draw(self, window):
        """Draws the tokens to the screen"""
        if not self.imageList:
            window.blit(self.image, self.rect)
        else:
            self.image = self.animate_Explosion()
            self.rect = self.image.get_rect(topleft=self.pos)
            self.rect[1] = self.pos[1] - 10
            window.blit(self.image, self.rect)

#  Game Utility Functions

def createGameGrid(rows, cols, cellsize, pos):
    """Creates a game grid with coordinates for each cell"""
    startX = pos[0]
    startY = pos[1]
    coordGrid = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append((startX, startY))
            startX += cellsize
        coordGrid.append(rowX)
        startX = pos[0]
        startY += cellsize
    return coordGrid


def createGameLogic(rows, cols):
    """Updates the game grid with logic, ie - spaces and X for ships"""
    gamelogic = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append(' ')
        gamelogic.append(rowX)
    return gamelogic

def updateGameLogic(coordGrid, shiplist, gamelogic):
    """Updates the game grid with the position of the ships"""
    for i, rowX in enumerate(coordGrid):
        for j, colX in enumerate(rowX):
            if gamelogic[i][j] == 'T' or gamelogic[i][j] == 'X':
                continue
            else:
                gamelogic[i][j] = ' '
                for ship in shiplist:
                    if pygame.rect.Rect(colX[0], colX[1], CELLSIZE, CELLSIZE).colliderect(ship.rect):
                        gamelogic[i][j] = 'O'

def showGridOnScreen(window, cellsize, playerGrid, computerGrid):
    """Draws the player and computer grids to the screen"""
    gamegrids = [playerGrid, computerGrid]
    for grid in gamegrids:
        for row in grid:
            for col in row:
                pygame.draw.rect(window, (255, 255, 255), (col[0], col[1], cellsize, cellsize), 1)


def printGameLogic():
    """prints to the terminal the game logic"""
    print('Player Grid'.center(50, '#'))
    for _ in pGameLogic:
        print(_)
    print('Computer Grid'.center(50, '#'))
    for _ in cGameLogic:
        print(_)


def loadImage(path, size, rotate=False):
    """A function to import the images into memory"""
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    if rotate == True:
        img = pygame.transform.rotate(img, -90)
    return img


def createFleet():
    """Creates the fleet of ships"""
    fleet = []
    for name in FLEET.keys():
        fleet.append(
            Ship(name,
                 FLEET[name][1],
                 FLEET[name][2],
                 FLEET[name][3],
                 FLEET[name][4],
                 FLEET[name][5],
                 FLEET[name][6],
                 FLEET[name][7])
        )
    return fleet


def sortFleet(ship, shiplist):
    """Rearranges the list of ships"""
    shiplist.remove(ship)
    shiplist.append(ship)


def randomizeShipPositions(shiplist, gamegrid):
    # Kiest een random locatie op de grid voor alle schepen
    placedShips = []
    for i, ship in enumerate(shiplist):
        validPosition = False
        while validPosition == False:
            ship.returnToDefaultPosition()
            rotateShip = random.choice([True, False])
            if rotateShip == True:
                yAxis = random.randint(0, 9)
                xAxis = random.randint(0, 9 - (ship.hFoto.get_width()//50))
                ship.rotateShip(True)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            else:
                yAxis = random.randint(0, 9 - (ship.vFoto.get_height()//50))
                xAxis = random.randint(0, 9)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            if len(placedShips) > 0:
                for item in placedShips:
                    if ship.rect.colliderect(item.rect):
                        validPosition = False
                        break
                    else:
                        validPosition = True
            else:
                validPosition = True
        placedShips.append(ship)
    

def takeTurns(player1, player2):
        if player1.turn == True:
            player2.turn = False
        else:
            player2.turn = True
        if not player2.makeAttack(pGameLogic):
            player1.turn = True
    

def updateGameScreen(window):
    window.fill((0, 0, 0))

    #  Draws the player and computer grids to the screen
    showGridOnScreen(window, CELLSIZE, pGameGrid, cGameGrid)

    #  Draw ships to screen
    for ship in pFleet:
        ship.draw(window)
        ship.snapToGridEdge(pGameGrid)
        ship.snapToGrid(pGameGrid)

    for ship in cFleet:
        ship.draw(window)
        ship.snapToGridEdge(cGameGrid)
        ship.snapToGrid(cGameGrid)

    for button in BUTTONS:
        button.draw(window)

    computer.draw(window)

    updateGameLogic(pGameGrid, pFleet, pGameLogic)
    updateGameLogic(cGameGrid, cFleet, cGameLogic)
    pygame.display.update()


#  Game Settings and Variables
SCREENWIDTH = 1290
SCREENHEIGHT = 1080
ROWS = 10
COLS = 10
CELLSIZE = 50
DEPLOYMENT = True
TURNTIMER = pygame.time.get_ticks()

#  Colors


#  Pygame Display Initialization
GAMESCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Battle Ship')


#  Game Lists/DIctionaries
FLEET = {
    'battleship': ['battleship', 'assets/images/ships/battleship/battleship.png', (125, 600), (40, 195),
                   4, 'assets/images/ships/battleship/battleshipgun.png', (0.4, 0.125), [-0.525, -0.34, 0.67, 0.49]],
    'cruiser': ['cruiser', 'assets/images/ships/cruiser/cruiser.png', (200, 600), (40, 195),
                2, 'assets/images/ships/cruiser/cruisergun.png', (0.4, 0.125), [-0.36, 0.64]],
    'destroyer': ['destroyer', 'assets/images/ships/destroyer/destroyer.png', (275, 600), (30, 145),
                  2, 'assets/images/ships/destroyer/destroyergun.png', (0.5, 0.15), [-0.52, 0.71]],
    'patrol boat': ['patrol boat', 'assets/images/ships/patrol boat/patrol boat.png', (425, 600), (20, 95),
                    0, '', None, None],
    'submarine': ['submarine', 'assets/images/ships/submarine/submarine.png', (350, 600), (30, 145),
                  1, 'assets/images/ships/submarine/submarinegun.png', (0.25, 0.125), [-0.45]],
    'carrier': ['carrier', 'assets/images/ships/carrier/carrier.png', (50, 600), (45, 245),
                0, '', None, None],
    'rescue ship': ['rescue ship', 'assets/images/ships/rescue ship/rescue ship.png', (500, 600), (20, 95),
                    0, '', None, None]
}

#  Loading Game Variables
pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (50, 50))
pGameLogic = createGameLogic(ROWS, COLS)
pFleet = createFleet()

cGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (SCREENWIDTH - (ROWS * CELLSIZE), 50))
cGameLogic = createGameLogic(ROWS, COLS)
cFleet = createFleet()
randomizeShipPositions(cFleet, cGameGrid)
printGameLogic()
#  Loading Game Sounds and Images
buttonFoto = loadImage('assets/images/buttons/button.png', (150, 50))
BUTTONS = [
    Button(buttonFoto, (150, 50), (25, 900), 'Random grid'),
    
    Button(buttonFoto, (150, 50), (200, 900), 'reset'),
    Button(buttonFoto, (150, 50), (375, 900), 'Deploy'),
]

REDTOKEN = loadImage('assets/images/tokens/redtoken.png', (CELLSIZE, CELLSIZE))
GREENTOKEN = loadImage('assets/images/tokens/greentoken.png', (CELLSIZE, CELLSIZE))
BLUETOKEN = loadImage('assets/images/tokens/bluetoken.png', (CELLSIZE, CELLSIZE))

TOKENS = []
#  Initialize Players
player1 = Player()
computer = EasyComputer()

#  Main Game Loop
RUNGAME = True
while RUNGAME:

    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNGAME = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                
                if DEPLOYMENT == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(pygame.mouse.get_pos()):
                            ship.active = True
                            sortFleet(ship, pFleet)
                            ship.selectShipAndMove()
                    else:
                        if player1.turn == True:
                            player1.makeAttack(cGameGrid, cGameLogic)


                    for button in BUTTONS:
                        if button.rect.collidepoint(pygame.mouse.get_pos()):
                            button.actionOnPress()
                            if button.name == 'Deploy':
                               status = button.deploymentPhase()
                               DEPLOYMENT = status
                               print(DEPLOYMENT)


            elif event.button == 2:
                printGameLogic()


            elif event.button == 3:
               if DEPLOYMENT == True:
                for ship in pFleet:
                    if ship.rect.collidepoint(pygame.mouse.get_pos()) and not ship.checkForRotateCollisions(pFleet):
                        ship.rotateShip(True)

    updateGameScreen(GAMESCREEN)

    takeTurns(player1, computer)
pygame.quit()