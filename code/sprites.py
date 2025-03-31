from settings import * 
from random import choice, uniform

class Paddle(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)

        # image 
        self.image = pygame.Surface(SIZE['paddle'], pygame.SRCALPHA)
        pygame.draw.rect(self.image, COLORS['paddle'], pygame.FRect((0,0), SIZE['paddle']), 0, 5)
        #drawing on surface which is 40/100 pixels  circle needs - color, position x & y, size width & height, 

        #shadow_surf
        self.shadow_surf = self.image.copy()
        pygame.draw.rect(self.shadow_surf, COLORS['paddle shadow'], pygame.FRect((0,0), SIZE['paddle']), 0, 5)
        
        # rect & movement
        self.rect = self.image.get_frect(center = pos)  
        self.old_rect = self.rect.copy()
        self.direction = 0
        
    def move(self, dt):
        self.rect.centery += self.direction * self.speed * dt 
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
    
    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.get_direction()
        self.move(dt)


class Player(Paddle):
    def __init__(self, pos, groups):
        super().__init__(pos, groups)
        self.speed = SPEED['player']

    def get_direction(self):
        keys = pygame.key.get_pressed()
        self.direction = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP]) #+1 to height if down, -1 to height if up

class Opponent(Paddle):
    def __init__(self, pos, ball, groups):
        super().__init__(pos, groups)
        self.speed = SPEED['opponent']
        self.ball = ball

    def get_direction(self):
        if self.rect.centery < self.ball.rect.centery:
            self.direction = 1
        else:
            self.direction = -1

class Ball(pygame.sprite.Sprite):
    def __init__(self, groups, paddle_sprites, update_score):
        super().__init__(groups)
        self.paddle_sprites = paddle_sprites
        self.update_score = update_score
        # image 
        self.image = pygame.Surface(SIZE['ball'], pygame.SRCALPHA)
        pygame.draw.circle(self.image, COLORS['ball'], (SIZE['ball'][0] / 2,SIZE['ball'][1] / 2), SIZE['ball'][0] / 2)
        #drawing on surface which is 30/30 pixels  circle needs - color, position x & y, radius
        

        #shadow_surf
        self.shadow_surf = self.image.copy() 
        pygame.draw.circle(self.shadow_surf, COLORS['ball shadow'], (SIZE['ball'][0] / 2,SIZE['ball'][1] / 2), SIZE['ball'][0] / 2)

        # rect & movement
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.old_rect = self.rect.copy()
        self.direction = pygame.Vector2(choice((1,-1)), uniform(0.7, 0.8) *choice((-1,1)))
        self.speed = SPEED['ball']
        self.speed_modifier = 0

        #time
        self.start_time = pygame.time.get_ticks()
        self.duration = 1200

    def move(self, dt):
        self.rect.x += self.direction.x * self.speed * dt * self.speed_modifier
        self.collision("horizontal")
        self.rect.y += self.direction.y * self.speed * dt * self.speed_modifier
        self.collision("vertical")

    def collision(self, direction):
        #COLLISION BETWEEN 2 MOVING OBJECTS
        for sprite in self.paddle_sprites:
            if sprite.rect.colliderect(self.rect):
                if direction == "horizontal":
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                        self.direction.x *= -1 #change direction
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                        self.direction.x *= -1 #change direction
                else:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                        self.direction.y *= -1
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                        self.direction.y *= -1

    def wall_collision(self):
        if self.rect.top <= 0:
            self.rect.top = 0
            self.direction.y *= -1
        
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.direction.y *= -1

        if self.rect.right >= WINDOW_WIDTH or self.rect.left <= 0:
            self.update_score('player' if self.rect.x < WINDOW_WIDTH /2 else 'opponent')
            self.reset()
            
    def reset(self):
        
        self.rect.center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        self.direction = pygame.Vector2(choice((1,-1)), uniform(0.7, 0.8) *choice((-1,1)))
        self.start_time = pygame.time.get_ticks()

    def timer(self):
        if pygame.time.get_ticks() - self.start_time >= self.duration:
            self.speed_modifier = 1
        else:
            self.speed_modifier = 0

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.timer()
        self.move(dt)
        self.wall_collision()