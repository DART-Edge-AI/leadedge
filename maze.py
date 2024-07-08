import matplotlib.pyplot as plt
import numpy as np

def generate_maze(size, openings):
    # Initialize the maze grid with walls
    maze = np.ones((size, size))
    
    # Start from a random point
    start_x, start_y = np.random.randint(1, size-1, 2)
    maze[start_x][start_y] = 0
    stack = [(start_x, start_y)]
    
    # Possible movements
    movements = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up

    while stack:
        x, y = stack[-1]
        # Check possible directions
        np.random.shuffle(movements)
        for dx, dy in movements:
            nx, ny = x + 2*dx, y + 2*dy
            if 1 <= nx < size-1 and 1 <= ny < size-1 and maze[nx][ny] == 1:
                maze[nx][ny] = 0
                maze[x+dx][y+dy] = 0
                stack.append((nx, ny))
                break
        else:
            stack.pop()

    # Ensure the maze has the specified number of openings
    if openings == 2:
        add_openings(maze, size)

    return maze

def add_openings(maze, size):
    for _ in range(2):
        while True:
            x = np.random.randint(1, size-1)
            if maze[1][x] == 0:
                maze[0][x] = 0
                break

def plot_maze(maze):
    plt.figure(figsize=(10, 10))
    plt.imshow(maze, cmap='Greys', interpolation='nearest')
    plt.axis('off')
    plt.show()

def main():
    size = 41  # Must be odd to ensure proper path carving
    maze = generate_maze(size, 2)
    plot_maze(maze)

if __name__ == '__main__':
    main()
