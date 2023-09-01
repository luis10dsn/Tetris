from collections import OrderedDict #es un diccionario de subclase que recuerda el orden en que las teclas fueron insertadas
import random
from pygame import Rect#directorio que permite almacenar y manipular areas rectangulares
import pygame
import numpy as np #numpy trabaja con matrices

WINDOW_WIDTH, WINDOW_HEIGHT = 500,601
GRID_WIDTH, GRID_HEIGHT = 300, 600
TILE_SIZE = 30
def remove_empty_columns (arr, _x_offset=0, _keep_counting=True):
    # Elimina las columnas vacías de arr (es decir, las que están llenas de ceros).
    # El valor de retorno es (new_arr, x_offset), donde xx_offset es cuánto
    # es la cantidad de coordenadas x que hay que aumentar para mantener
    # la posición original del bloque.
    for colid, col in enumerate(arr.T):
        if col.max() == 0:
            if _keep_counting:
                _x_offset += 1
    # remueve la columna e intenta de nuevo
            arr, _x_offset = remove_empty_columns(
                np.delete(arr, colid, 1), _x_offset, _keep_counting)
            break
        else:
            _keep_counting = False
    return arr, _x_offset


class BottomReached(Exception):
    pass
class TopReached(Exception):
    pass
class Block(pygame.sprite.Sprite):
    
    @staticmethod
#Un decorador es una función Python permite que agregar funcionalidad a otra función,
#pero sin modificarla.
#También, esto es llamado meta-programación,
#por que parte del programa trata de modificar a otro al momento de compilar.
#Para llamar un decorador se utiliza el signo de arroba (@).
    def collide (block,group):
        # Comprueba si el bloque especificado colisiona con algún otro bloque en el grupo.
        for other_block in group:
            #ignora el actual bloque que siempre colisiona con él mismo
            if block == other_block:
                continue
            if pygame.sprite.collide_mask(block, other_block) is not None:
                return True
        return False
    
    def __init__(self):
        super().__init__()
#Esta función nos permite invocar y conservar un método o atributo de una clase padre (primaria)
#desde una clase hija (secundaria) sin tener que nombrarla explícitamente.
#Esto nos brinda la ventaja de poder cambiar el nombre de la clase padre (base) o hija (secundaria)
#cuando queramos y aún así mantener un código funcional, sencillo  y mantenible.

        self.color = random.choice((
            (200, 200, 200),
            (215, 133, 133),
            (30, 145, 255),
            (0, 170, 0),
            (180, 0, 140),
            (200, 200, 0))) #Genera un color aleatorio

        self.current=True
        self.struct=np.array(self.struct)
        #inicializa aleatoreamente el volteo y la rotación
        if random.randint(0,1): #volteo en el eje x
            self.struct= np.rot90(self.struct)
        if random.randint(0,1): #volteo en el eje Y
            self.struct= np.flip(self.struct, 0)
        self._draw()

    def _draw(self, x=4, y=0):
        width = len(self.struct[0]) * TILE_SIZE
        height = len(self.struct) * TILE_SIZE
        self.image = pygame.surface.Surface([width, height])
        self.image.set_colorkey((0, 0, 0))

#posición y tamaño
        self.rect = Rect(0, 0, width, height)
        self.x = x
        self.y = y
        for y, row in enumerate(self.struct):
            for x, col in enumerate(row):
                if col:
                    pygame.draw.rect(
                        self.image,
                        self.color,
                        Rect(x*TILE_SIZE + 1, y*TILE_SIZE + 1,
                             TILE_SIZE - 2, TILE_SIZE - 2)
                    )
        self._create_mask()

    def redraw(self):
        self._draw(self.x,self.y)

    def _create_mask(self):
#Cree el atributo de máscara(mask) a partir de la superficie principal.
#La máscara (mask)es necesaria para comprobar las colisiones. Esto debe ser llamado
#después de crear o actualizar la superficie.
        self.mask = pygame.mask.from_surface(self.image)
    
    def initial_draw(self):
        raise NotImplementedError # raise NotImplementedError  es un m[etodo que necesita ser definido
                                  # por una subclase, simulando una interface

                                  
        
    @property #decorador
    def group(self):
        return self.group()[0]
   
    @property
    def x (self):
        return self._x

    @x.setter # método qué establece valores de atributo privado en una clase
    def x(self, value):
        self._x = value
        self.rect.left = value*TILE_SIZE
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
        self.rect.top = value*TILE_SIZE
    
    def move_left(self, group):
        self.x -= 1
        # revisa si el argen izquierdo es alcanzado
        if self.x < 0 or Block.collide(self, group):
            self.x += 1

    def move_right(self, group):
        self.x += 1
    #revisa si se alcanzo el margen derecho o la colision con otro bloque
        if self.rect.right > GRID_WIDTH or Block.collide(self, group):
            self.x -= 1
    def move_down(self, group):
        self.y += 1

        if self.rect.bottom > GRID_HEIGHT or Block.collide(self, group):
            # Rollback to the previous position.
            self.y -= 1
            self.current = False
            raise BottomReached

    def rotate(self, group):
        self.image = pygame.transform.rotate(self.image, 90)
        #una vez rotados necesitamos actualizar la posiscion y el tamaño

        self.rect.width = self.image.get_width()
        self.rect.height = self.image.get_height()
        self._create_mask()
        #verifica que la nueva posición no exceda los limites o
        #el colisionador con otros bloques y los ajusta si es necesario

        while self.rect.right > GRID_WIDTH:
            self.x -= 1
        while self.rect.left < 0:
            self.x += 1
        while self.rect.bottom > GRID_HEIGHT:
            self.y -= 1
        while True:
            if not Block.collide(self, group):
                break
            self.y -= 1
        self.struct = np.rot90(self.struct)
    
    def update(self):
        if self.current:
            self.move_down()



class SquareBlock(Block):
    struct = (
        (1, 1),
        (1, 1)
    )
class TBlock(Block):
    struct = (
        (1, 1, 1),
        (0, 1, 0)
    )
class LineBlock(Block):
    struct = (
        (1,),
        (1,),
        (1,),
        (1,)
    )
class LBlock(Block):
    struct = (
        (1, 1),
        (1, 0),
        (1, 0),
    )
class ZBlock(Block):
    struct = (
        (0, 1),
        (1, 1),
        (1, 0),
    )
class BlocksGroup(pygame.sprite.OrderedUpdates):
    
    @staticmethod #un método que no sabe nada de :la clase o instancia a la que se llama
    def get_random_block():
        return random.choice(
            (SquareBlock, TBlock, LineBlock, LBlock, ZBlock))()
    
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        #Esta función nos permite invocar y conservar un método o atributo de una clase padre (primaria)
        #desde una clase hija (secundaria) sin tener que nombrarla explícitamente.
        #Esto nos brinda la ventaja de poder cambiar el nombre de la clase padre (base) o hija (secundaria)
        #cuando queramos y aún así mantener un código funcional, sencillo  y mantenible.
 
        self._reset_grid()
        self._ignore_next_stop = False
        self.score = 0
        self.next_block = None
        self.stop_moving_current_block()
        self._create_new_block()
        
    def _check_line_completion(self):
        #revisa cada linea del grid(vector) y remueve las que estan completas

        #revision desde el fondo del grid

        for i, row in enumerate(self.grid[::-1]):
            if all(row):
                self.score += 5
                #obtiene los bloques afectados por linea y remueve los que están duplicados
                affected_blocks = list(
                    OrderedDict.fromkeys(self.grid[-1 - i]))
                
                for block, y_offset in affected_blocks:
                #remueve los bloques que pertenecen a la linea completa
                    block.struct = np.delete(block.struct, y_offset, 0)
                    if block.struct.any():
            #una vez removidas, revisa si hay ecolumnas vacías hasta que los bloques las llenen
                        block.struct, x_offset = \
                            remove_empty_columns(block.struct)
            #compensa los esácios borrados conb columnas


                       #mantiene la posicion original del bloque
                        block.x += x_offset
                       # fuerza una actualizacion de bloques
                        block.redraw()

                    else:
                        # si la estructura está vacía, entonces el bloque se va
                        self.remove(block)


            #revisa cuales bloques necesitan moverse
            # una vez la linea fue completada, mueve todas las demás

                for block in self:
                    #exceptúa el actual bloque
                    if block.current:
                        continue
            #empuja hacia abajo cada bloque hasta que alcance los limites o choque con otro bloque

                    while True:
                        try:
                            block.move_down(self)
                        except BottomReached:
                            break
                
                self.update_grid()
#desde que el grid ha sidoactualizado, el contador de i no es válid
# llamando la fucncion de nuevo y revisando si hay otras lineas completas en el grid
                self._check_line_completion()
                break
            
    def _reset_grid(self):
        self.grid = [[0 for _ in range(10)] for _ in range(20)]
                        

    def _create_new_block(self):
        new_block = self.next_block or BlocksGroup.get_random_block()
        if Block.collide(new_block, self):
            raise TopReached
        self.add(new_block)
        self.next_block = BlocksGroup.get_random_block()
        self.update_grid()
        self._check_line_completion()
    
    def update_grid(self):
        self._reset_grid()
        for block in self:
            for y_offset, row in enumerate(block.struct):
                for x_offset, digit in enumerate(row):
            #previene remplazar el bloque anterior
                    if digit == 0:
                        continue
                    rowid = block.y + y_offset
                    colid = block.x + x_offset
                    self.grid[rowid][colid] = (block, y_offset)

    @property
    def current_block(self):
        return self.sprites()[-1]
    
    def update_current_block(self):
        try:
            self.current_block.move_down(self)
        except BottomReached:
            self.stop_moving_current_block()
            self._create_new_block()
        else:
            self.update_grid()
    
    def move_current_block(self):
               #primero revisa si hay algo que mover
        if self._current_block_movement_heading is None:
            return
        action = {
            pygame.K_DOWN: self.current_block.move_down,
            pygame.K_LEFT: self.current_block.move_left,
            pygame.K_RIGHT: self.current_block.move_right
        }
        
        try:
        # cada funcion requiere de un grupo como el primer argumento para
        # revisar cualquier posible colisión
            action[self._current_block_movement_heading](self)
        except BottomReached:
            self.stop_moving_current_block()
            self._create_new_block()
        else:
            self.update_grid()
    
    def start_moving_current_block(self, key):
        if self._current_block_movement_heading is not None:
            self._ignore_next_stop = True
        self._current_block_movement_heading = key
    
    def stop_moving_current_block(self):
        if self._ignore_next_stop:
            self._ignore_next_stop = False
        else:
            self._current_block_movement_heading = None
    
    def rotate_current_block(self):
        # previene la rotacion de SquareBlocks
        if not isinstance(self.current_block, SquareBlock):
    #  isinstance es una funcion que retorna en True si el objeto es del tipo especificado
    # sino retorna en False, se usa  isinstance para verificar un tipo de valor de dato
            self.current_block.rotate(self)
            self.update_grid()
            
def draw_grid(background):
    #dibuja el grid del background
    grid_color = 50,50,50
    # lineas verticales
    for i in range(11):
        x = TILE_SIZE * i
        pygame.draw.line(
            background, grid_color, (x, 0), (x, GRID_HEIGHT)
        )
        
    #lineas horizontales
    for i in range(21):
        y = TILE_SIZE * i
        pygame.draw.line(
            background, grid_color, (0, y), (GRID_WIDTH, y)
        )

def draw_centered_surface(screen, surface, y):
    screen.blit(surface, (400 - surface.get_width()/2, y))
            
def main():
    pygame.mixer.init()
    pygame.init()
    pygame.display.set_caption("TETRIS")
    sonido_fondo = pygame.mixer.Sound("loop.mp3")
    sonido_fondo1 = pygame.mixer.Sound("game over.mp3")

    pygame.mixer.Sound.play(sonido_fondo, -1)
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    run = True
    paused = False
    game_over = False
    # Crea el background.
    background = pygame.Surface(screen.get_size())
    bgcolor = (0, 0, 0)
    background.fill(bgcolor)
    # Dibuja el grid en la parte superior del background.
    draw_grid(background)
    # hace el blitting más rápido.
    #es una primitiva gráfica consistente en que dos mapas de bit son combinados en uno. Se trata de una de las primitivas gráficas más básicas y por tanto más utilizadas en gráficos 2D.
    #La mayoría de las tarjetas de vídeo la implementan en hardware (es una de la muchas operaciones de las que se encarga la GPU).
    background = background.convert()
    
    try:
        font = pygame.font.Font("Roboto-Regular.ttf", 20)
    except OSError:
        # Si el archivo no encuentra el font, utiliza uno predeterminado.
        pass
    next_block_text = font.render(
        "Siguiente bloque:", True, (255, 255, 255), bgcolor)
    score_msg_text = font.render(
        "Puntaje:", True, (255, 255, 255), bgcolor)
    game_over_text = font.render(
        "¡GAME OVER!", True, (255, 220, 0), bgcolor)

        
    # Constantes
    MOVEMENT_KEYS = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN
    EVENT_UPDATE_CURRENT_BLOCK = pygame.USEREVENT + 1
    EVENT_MOVE_CURRENT_BLOCK = pygame.USEREVENT + 2
    pygame.time.set_timer(EVENT_UPDATE_CURRENT_BLOCK, 1000)
    pygame.time.set_timer(EVENT_MOVE_CURRENT_BLOCK, 100)
    
    blocks = BlocksGroup()
    
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.KEYUP:
                if not paused and not game_over:
                    if event.key in MOVEMENT_KEYS:
                        blocks.stop_moving_current_block()
                    elif event.key == pygame.K_UP:
                        blocks.rotate_current_block()
                if event.key == pygame.K_p:# al presionar p se pausa el juego
                    paused = not paused
            
            # detiene los bloques si el juego estápausado o es game over
            if game_over or paused:
                
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key in MOVEMENT_KEYS:
                    blocks.start_moving_current_block(event.key)
            
            try:
                if event.type == EVENT_UPDATE_CURRENT_BLOCK:
                    blocks.update_current_block()
                elif event.type == EVENT_MOVE_CURRENT_BLOCK:
                    blocks.move_current_block()
            except TopReached:
                game_over = True
        
        #Dibuja el background en el grid
        screen.blit(background, (0, 0))
        # Bloques.
        blocks.draw(screen)
        # Barra lateral con la información extra
        draw_centered_surface(screen, next_block_text, 50)
        draw_centered_surface(screen, blocks.next_block.image, 100)
        draw_centered_surface(screen, score_msg_text, 240)
        score_text = font.render(
            str(blocks.score), True, (255, 255, 255), bgcolor)
        draw_centered_surface(screen, score_text, 270)
        if game_over:
            draw_centered_surface(screen, game_over_text, 360)
            pygame.mixer.Sound.play(sonido_fondo1, -1)
            pygame.mixer.Sound.stop(sonido_fondo)
        # actualiza
        pygame.display.flip()
    
    pygame.quit()
if __name__ == "__main__":
    main()
