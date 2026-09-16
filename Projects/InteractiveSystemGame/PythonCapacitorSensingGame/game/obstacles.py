import pygame
import random


# =====================================================
# COLORS
# =====================================================

OBSTACLE_COLOR = (180, 50, 50)
FINISH_COLOR = (50, 180, 80)


# =====================================================
# COURSE 1
# =====================================================

def create_course_1():

    obstacles = [

        # Bottom section
        pygame.Rect(
            0, 520, 650, 35
        ),

        # Second section
        pygame.Rect(
            350, 430, 650, 35
        ),

        # Third section
        pygame.Rect(
            0, 340, 600, 35
        ),

        # Fourth section
        pygame.Rect(
            300, 250, 700, 35
        ),

        # Fifth section
        pygame.Rect(
            0, 160, 700, 35
        ),

        # Top obstacle
        pygame.Rect(
            200, 90, 250, 30
        ),
    ]

    return obstacles


# =====================================================
# COURSE 2
# =====================================================

def create_course_2():

    obstacles = [

        # Bottom
        pygame.Rect(
            300, 550, 700, 35
        ),

        # Second
        pygame.Rect(
            0, 450, 650, 35
        ),

        # Third
        pygame.Rect(
            350, 350, 650, 35
        ),

        # Fourth
        pygame.Rect(
            0, 250, 650, 35
        ),

        # Fifth
        pygame.Rect(
            300, 150, 700, 35
        ),

        # Top
        pygame.Rect(
            0, 70, 450, 30
        ),
    ]

    return obstacles


# =====================================================
# COURSE 3
# =====================================================

def create_course_3():

    obstacles = [

        # Bottom section
        pygame.Rect(
            0, 540, 500, 35
        ),

        # Creates a more central corridor
        pygame.Rect(
            600, 460, 400, 35
        ),

        # Middle left
        pygame.Rect(
            0, 380, 550, 35
        ),

        # Middle right
        pygame.Rect(
            450, 300, 550, 35
        ),

        # Upper left
        pygame.Rect(
            0, 220, 500, 35
        ),

        # Upper right
        pygame.Rect(
            500, 140, 500, 35
        ),

        # Small center obstacle
        pygame.Rect(
            250, 80, 250, 30
        ),
    ]

    return obstacles


# =====================================================
# FINISH LINE
# =====================================================

def create_finish_line():

    return pygame.Rect(
        0,
        30,
        1000,
        30
    )


# =====================================================
# RANDOM COURSE
# =====================================================

def get_random_course():

    courses = [
        create_course_1,
        create_course_2,
        create_course_3
    ]

    selected_course = random.choice(courses)

    return selected_course()


# =====================================================
# DRAW COURSE
# =====================================================

def draw_course(screen, obstacles, finish_line):

    # Draw obstacles
    for obstacle in obstacles:

        pygame.draw.rect(
            screen,
            OBSTACLE_COLOR,
            obstacle
        )

    # Draw finish line
    pygame.draw.rect(
        screen,
        FINISH_COLOR,
        finish_line
    )