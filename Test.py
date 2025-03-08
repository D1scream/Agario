import pygame
import math

# Инициализация Pygame
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Circle Collision and Sliding")
clock = pygame.time.Clock()

# Параметры круга
class Circle:
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        self.pos = pygame.math.Vector2(x, y)  # Позиция круга
        self.radius = radius  # Радиус круга
        self.color = color  # Цвет круга
        self.speed = pygame.math.Vector2(speed_x, speed_y)  # Скорость движения круга

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

    def update(self):
        self.pos += self.speed  # Обновление позиции круга

    def check_collision(self, other_circle):
        """Проверка на столкновение с другим кругом"""
        distance = self.pos.distance_to(other_circle.pos)
        if distance <= self.radius + other_circle.radius:
            return True
        return False

    def resolve_collision(self, other_circle):
        """Решение столкновения (отражение от поверхности)"""
        # Вектор от центра одного круга к другому
        normal = other_circle.pos - self.pos
        normal_length = normal.length()

        # Нормализуем вектор нормали
        normal.normalize_ip()

        # Отражение скорости вдоль нормали
        relative_velocity = self.speed - other_circle.speed
        speed_along_normal = relative_velocity.dot(normal)

        # Если скорость вдоль нормали отрицательная (круги приближаются), выполняем отражение
        if speed_along_normal < 0:
            return

        # Массируем момент столкновения
        restitution = 1  # Коэффициент восстановления (1 — идеальный отскок)
            # Скорости отражаются относительно нормали
        impulse = 2 * speed_along_normal / (self.radius + other_circle.radius)
        self.speed -= impulse * other_circle.radius * normal
        other_circle.speed += impulse * self.radius * normal

# Создаем два круга
circle1 = Circle(200, 300, 50, (255, 0, 0), 2, 0)  # Красный круг
circle2 = Circle(300, 300, 50, (0, 255, 0), -2, 0)  # Зеленый круг

running = True
while running:
    screen.fill((255, 255, 255))  # Очистка экрана

    # Обновляем позиции кругов
    circle1.update()
    circle2.update()

    # Проверка столкновения
    if circle1.check_collision(circle2):
        # Разрешаем столкновение
        circle1.resolve_collision(circle2)

    # Отрисовываем круги
    circle1.draw(screen)
    circle2.draw(screen)

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()  # Обновление экрана
    clock.tick(60)  # Ограничение по частоте кадров (60 FPS)

pygame.quit()
