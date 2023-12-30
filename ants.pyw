import random,colorsys,pygame,sys,json,win32ui,os,win32gui,win32con
class World:
    def __init__(self, *args, **kwargs):
        self.width = kwargs.get('width', 100)
        self.height = kwargs.get('height', 100)
        self.antpos = kwargs.get('antpos', (self.width//2, self.height//2))
        self.antdir = kwargs.get('antdir', 0)
        self.rule = kwargs.get('rule', 'RL')
        self.index = 0
        self.steps = 0
        if 'colors' in kwargs:  self.colors = kwargs['colors']
        else:
            self.colors = []
            for i in range(len(self.rule)):
                col = colorsys.hsv_to_rgb(i/len(self.rule), 1, 1)
                self.colors.append((int(col[0]*255), int(col[1]*255), int(col[2]*255)))
            random.shuffle(self.colors)
        if 'grid' in kwargs:    self.grid = [[self.colors[kwargs['grid'][y*self.width+x]] for x in range(self.width)] for y in range(self.height)]
        else:   self.grid = [[self.colors[0] for x in range(self.width)] for y in range(self.height)]

    def save(self, filename, withGrid=True):
        with open(filename, 'w') as f:
            out = {'width':self.width, 'height':self.height, 'antpos':self.antpos, 'antdir':self.antdir, 'rule':self.rule, 'colors':self.colors}
            if withGrid:
                grid = [self.colors.index(self.grid[y][x]) for y in range(self.height) for x in range(self.width)]
                out['grid'] = grid
            json.dump(out, f, indent=4)
        
    def get(self, x, y):
        return self.grid[y%self.height][x%self.width]
    
    def set(self, x, y, val):
        self.grid[y%self.height][x%self.width] = val

    def step(self):
        color = self.get(*self.antpos)
        index = self.colors.index(color)
        rule = self.rule[index]
        if rule == 'R': self.antdir += 1
        elif rule == 'L': self.antdir -= 1
        elif rule == 'T': self.antdir += 2
        elif rule == 'K': self.antdir -= 2
        self.antdir %= 4
        self.set(*self.antpos, self.colors[(index+1)%len(self.colors)])
        if self.antdir == 0:    self.antpos = (self.antpos[0], self.antpos[1]-1)
        elif self.antdir == 1:  self.antpos = (self.antpos[0]+1, self.antpos[1])
        elif self.antdir == 2:  self.antpos = (self.antpos[0], self.antpos[1]+1)
        elif self.antdir == 3:  self.antpos = (self.antpos[0]-1, self.antpos[1])

        self.index += 1
        self.index %= len(self.rule)
        self.steps += 1
    
def openFile(world):
    filedlg = win32ui.CreateFileDialog(1, None, None, 4096, 'JSON Files (*.json)|*.json|All Files (*.*)|*.*|')
    if filedlg.DoModal() == 1:
        filename = filedlg.GetPathName()
    else:
        filename = None
    if filename:
        with open(filename, 'r') as f:
            return World(**json.load(f))
    return world

def saveFile(world, withGrid):
    filedlg = win32ui.CreateFileDialog(0, None, None, 0, 'JSON Files (*.json)|*.json|All Files (*.*)|*.*|')
    filedlg.SetOFNInitialDir(f'{os.getcwd()}')
    if filedlg.DoModal() == 1:
        filename = filedlg.GetPathName()
        if not filename.endswith('.json'):
            filename += '.json'
    else:
        mb = win32gui.MessageBox(0, 'Save with default name?', 'Save', win32con.MB_YESNO)
        if mb == win32con.IDYES:
            filename = f'save_{random.randint(0, 1000000)}.json'
        else:
            filename = None
    if filename:
        world.save(filename, withGrid=withGrid)

def render(screen, world, pixelsize):
    for y in range(world.height):
        for x in range(world.width):
            col = world.get(x, y)
            pygame.draw.rect(screen, col, (x*pixelsize, y*pixelsize, pixelsize, pixelsize))

if __name__ == '__main__':
    pygame.init()
    SCREENSIZE = 500
    screen = pygame.display.set_mode((SCREENSIZE, SCREENSIZE), pygame.RESIZABLE)
    SELECTED = None
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            world = World(**json.load(f))
            GRIDSIZE = world.width
    else:
        GRIDSIZE = 100
        world = World(width=GRIDSIZE, height=GRIDSIZE, rule='LRRRRRLLR')
    clock = pygame.time.Clock()
    pixelsize = SCREENSIZE//GRIDSIZE
    paused = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                SCREENSIZE = min(event.w, event.h)
                screen = pygame.display.set_mode((SCREENSIZE, SCREENSIZE), pygame.RESIZABLE)
                pixelsize = SCREENSIZE//GRIDSIZE
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    saveFile(world, withGrid=False)
                elif event.key == pygame.K_s:
                    saveFile(world, withGrid=True)
                elif event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif event.key == pygame.K_o:
                    world = openFile(world)
                    if world:
                        pixelsize = SCREENSIZE//GRIDSIZE
                        paused = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_RETURN:
                    world.step()
                    render(screen, world, pixelsize)
                elif event.key == pygame.K_r:
                    font = pygame.font.SysFont('Consolas', 30)
                    text = font.render(world.rule, True, (255, 255, 255))
                    textRect = text.get_rect()
                    textRect.center = (textRect.width//2+10, textRect.height//2+10)
                    col = world.colors[0]
                    pygame.draw.rect(screen, (col[0]//2,col[1]//2,col[2]//2), (0, 0, textRect.width+20, textRect.height+20))
                    screen.blit(text, textRect)
                    for i in range(len(world.colors)):
                        col = world.colors[i]
                        pygame.draw.rect(screen, col, (0, textRect.height+20+i*30, 30, 30))
                        cid = font.render(str(i), True, (255, 255, 255))
                        cidRect = cid.get_rect()
                        cidRect.center = (15, textRect.height+35+i*30)
                        screen.blit(cid, cidRect)
                    pygame.display.update()
                    pygame.time.wait(1000)
                elif event.key == pygame.K_h:
                    win32gui.MessageBox(0, 'Controls:\n\nSpace:\tPause\nEnter:\tStep\nR:\tShow Rule\nClick:\tSet color (cycles through rule colors)\nG:\tSave without grid\nS:\tSave with grid\nO:\tOpen\nEsc:\tQuit', 'Help', win32con.MB_OK)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    SELECTED = pygame.mouse.get_pos()
                    SELECTED = (SELECTED[0]//pixelsize, SELECTED[1]//pixelsize)
                    world.set(*SELECTED, world.colors[(world.colors.index(world.get(*SELECTED))+1)%len(world.colors)])
                    render(screen, world, pixelsize)
                    SELECTED = None
        if not paused:  
            world.step()
            render(screen, world, pixelsize)
        else:
            font = pygame.font.SysFont('Consolas', 30)
            text = font.render('Paused', True, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = (textRect.width//2+10, textRect.height//2+10)
            col = world.colors[0]
            pygame.draw.rect(screen, (col[0]//2,col[1]//2,col[2]//2), (0, 0, textRect.width+20, textRect.height+20))
            screen.blit(text, textRect)
            pygame.display.update()

        pygame.display.flip()
        pygame.display.set_caption(f'Ants: {world.steps} steps' + (' (Paused)' if paused else ''))
