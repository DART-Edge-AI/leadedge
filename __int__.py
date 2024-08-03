bl_info = {
    "name": "Lead Edge Maze Ash Creator",
    "blender": (4, 2, 0),
    "category": "Object",
    "version": (1, 0, 0),
    "maintainer": "Radical Deepscale",
    "description": "Generates and solves 3D mazes within Blender"
}

# Lead Edge Maze Ash Creator by: Justin Venable CEO @ Radical Deepscale LLC. v1.0.a

import bpy
import bmesh
import random

# Global dictionary to store maze data
maze_data = {
    "grid": None,
    "start": None,
    "end": None
}

class MazePanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Lead Edge"
    bl_idname = "OBJECT_PT_lead_edge"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lead Edge'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "maze_width")
        layout.prop(scene, "maze_height")
        layout.prop(scene, "maze_unit_size")
        layout.prop(scene, "maze_wall_height")

        layout.operator("mesh.generate_maze", text="Create Lead Edge Ash")
        layout.operator("mesh.solve_maze", text="(InDev!) Solve Lead Edge Ash")

def create_grid(width, height):
    return [[{'top': True, 'right': True, 'bottom': True, 'left': True} for _ in range(width)] for _ in range(height)]

def get_unvisited_neighbors(x, y, visited, width, height):
    neighbors = []
    if x > 0 and not visited[y][x-1]:
        neighbors.append((x-1, y))
    if x < width - 1 and not visited[y][x+1]:
        neighbors.append((x+1, y))
    if y > 0 and not visited[y-1][x]:
        neighbors.append((x, y-1))
    if y < height - 1 and not visited[y+1][x]:
        neighbors.append((x, y+1))
    return neighbors

def remove_wall(x1, y1, x2, y2, grid):
    if x1 == x2:
        if y1 > y2:
            grid[y1][x1]['top'] = False
            grid[y2][x2]['bottom'] = False
        else:
            grid[y1][x1]['bottom'] = False
            grid[y2][x2]['top'] = False
    else:
        if x1 > x2:
            grid[y1][x1]['left'] = False
            grid[y2][x2]['right'] = False
        else:
            grid[y1][x1]['right'] = False
            grid[y2][x2]['left'] = False

def generate_maze(width, height):
    grid = create_grid(width, height)
    start = get_random_perimeter_cell(width, height)
    exit = get_random_perimeter_cell(width, height, exclude_cell=start)
    stack = [start]
    visited = [[False] * width for _ in range(height)]
    visited[start[1]][start[0]] = True

    while stack:
        x, y = stack[-1]
        neighbors = get_unvisited_neighbors(x, y, visited, width, height)
        if neighbors:
            next_x, next_y = random.choice(neighbors)
            remove_wall(x, y, next_x, next_y, grid)
            stack.append((next_x, next_y))
            visited[next_y][next_x] = True
        else:
            stack.pop()

    return grid, start, exit  # Return the grid and start/end points

def get_random_perimeter_cell(width, height, exclude_cell=None):
    """Selects a random perimeter cell for entry/exit."""
    while True:
        side = random.randint(0, 3)
        if side == 0:  # Top
            cell = (random.randint(0, width - 1), 0)
        elif side == 1:  # Right
            cell = (width - 1, random.randint(0, height - 1))
        elif side == 2:  # Bottom
            cell = (random.randint(0, width - 1), height - 1)
        elif side == 3:  # Left
            cell = (0, random.randint(0, height - 1))

        if exclude_cell is None or cell != exclude_cell:
            return cell

def draw_3d_maze(grid, unit_size, wall_height, start, end):
    mesh = bpy.data.meshes.new("Maze")
    obj = bpy.data.objects.new("Maze", mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()

    # Create walls without assigning materials
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            cell = grid[y][x]
            base_x = x * unit_size
            base_y = y * unit_size

            if cell['top']:
                v1 = bm.verts.new((base_x, base_y, 0))
                v2 = bm.verts.new((base_x + unit_size, base_y, 0))
                v3 = bm.verts.new((base_x + unit_size, base_y, wall_height))
                v4 = bm.verts.new((base_x, base_y, wall_height))
                bm.faces.new((v1, v2, v3, v4))

            if cell['right']:
                v1 = bm.verts.new((base_x + unit_size, base_y, 0))
                v2 = bm.verts.new((base_x + unit_size, base_y + unit_size, 0))
                v3 = bm.verts.new((base_x + unit_size, base_y + unit_size, wall_height))
                v4 = bm.verts.new((base_x + unit_size, base_y, wall_height))
                bm.faces.new((v1, v2, v3, v4))

            if cell['bottom']:
                v1 = bm.verts.new((base_x, base_y + unit_size, 0))
                v2 = bm.verts.new((base_x + unit_size, base_y + unit_size, 0))
                v3 = bm.verts.new((base_x + unit_size, base_y + unit_size, wall_height))
                v4 = bm.verts.new((base_x, base_y + unit_size, wall_height))
                bm.faces.new((v1, v2, v3, v4))

            if cell['left']:
                v1 = bm.verts.new((base_x, base_y, 0))
                v2 = bm.verts.new((base_x, base_y + unit_size, 0))
                v3 = bm.verts.new((base_x, base_y + unit_size, wall_height))
                v4 = bm.verts.new((base_x, base_y, wall_height))
                bm.faces.new((v1, v2, v3, v4))

    bm.to_mesh(mesh)
    bm.free()
    center_geometry(obj)  # Center the geometry after mesh creation
    obj.location = (-len(grid[0]) * unit_size / 2, -len(grid) * unit_size / 2, 0)  # Center the maze

def solve_maze(grid, start, end, unit_size, wall_height):
    width = len(grid[0])
    height = len(grid)
    grid_size = (width, height)  # Added to pass the grid size to draw_path
    stack = [(start[0], start[1], [])]
    visited = set()

    while stack:
        x, y, path = stack.pop()
        if (x, y) == end:
            draw_path(path, unit_size, wall_height, grid_size)  # Pass the grid size
            return

        if (x, y) in visited:
            continue

        visited.add((x, y))
        path = path + [(x, y)]

        for nx, ny in get_neighbors_for_solve(x, y, grid, width, height):
            if (nx, ny) not in visited:
                stack.append((nx, ny, path))

def get_neighbors_for_solve(x, y, grid, width, height):
    neighbors = []
    if x > 0 and not grid[y][x]['left']:  # Check if left wall is open
        neighbors.append((x - 1, y))
    if x < width - 1 and not grid[y][x]['right']:  # Check if right wall is open
        neighbors.append((x + 1, y))
    if y > 0 and not grid[y][x]['top']:  # Check if top wall is open
        neighbors.append((x, y - 1))
    if y < height - 1 and not grid[y][x]['bottom']:  # Check if bottom wall is open
        neighbors.append((x, y + 1))
    return neighbors

def draw_path(path, unit_size, wall_height, grid_size):
    mesh = bpy.data.meshes.new("MazePath")
    obj = bpy.data.objects.new("MazePath", mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()

    # Compute the offset to center the path in the maze
    offset_x = (grid_size[0] * unit_size) / 2
    offset_y = (grid_size[1] * unit_size) / 2

    for (px, py) in path:
        base_x = (px * unit_size) - offset_x
        base_y = (py * unit_size) - offset_y
        v1 = bm.verts.new((base_x, base_y, wall_height))
        v2 = bm.verts.new((base_x + unit_size, base_y, wall_height))
        v3 = bm.verts.new((base_x + unit_size, base_y + unit_size, wall_height))
        v4 = bm.verts.new((base_x, base_y + unit_size, wall_height))
        bm.faces.new((v1, v2, v3, v4))

    bm.to_mesh(mesh)
    bm.free()
    center_geometry(obj)

    # Optionally, adjust the object's location to be exactly over the maze
    obj.location = (0, 0, 0)

def center_geometry(obj):
    # Set origin to geometry center
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)  # Center the object at the origin of the scene

class GenerateMaze(bpy.types.Operator):
    """Generate a 3D maze"""
    bl_idname = "mesh.generate_maze"
    bl_label = "Generate Maze"

    def execute(self, context):
        scene = context.scene
        width = scene.maze_width
        height = scene.maze_height
        unit_size = scene.maze_unit_size
        wall_height = scene.maze_wall_height

        # Generate maze and store in global dictionary
        grid, start, end = generate_maze(width, height)
        maze_data["grid"] = grid
        maze_data["start"] = start
        maze_data["end"] = end

        draw_3d_maze(grid, unit_size, wall_height, start, end)
        return {'FINISHED'}

class SolveMaze(bpy.types.Operator):
    """Solve the maze path"""
    bl_idname = "mesh.solve_maze"
    bl_label = "(InDev!) Solve Lead Edge Ash"

    def execute(self, context):
        # Use the stored maze grid from the global dictionary
        grid = maze_data.get("grid")
        start = maze_data.get("start")
        end = maze_data.get("end")

        if grid is None or start is None or end is None:
            self.report({'ERROR'}, "No maze found to solve.")
            return {'CANCELLED'}

        # Solve the maze and draw the path
        solve_maze(grid, start, end, context.scene.maze_unit_size, context.scene.maze_wall_height)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MazePanel)
    bpy.utils.register_class(GenerateMaze)
    bpy.utils.register_class(SolveMaze)
    bpy.types.Scene.maze_width = bpy.props.IntProperty(name="Width", default=10, min=1)
    bpy.types.Scene.maze_height = bpy.props.IntProperty(name="Height", default=10, min=1)
    bpy.types.Scene.maze_unit_size = bpy.props.FloatProperty(name="Unit Size", default=1)
    bpy.types.Scene.maze_wall_height = bpy.props.FloatProperty(name="Wall Height", default=2)

def unregister():
    bpy.utils.unregister_class(MazePanel)
    bpy.utils.unregister_class(GenerateMaze)
    bpy.utils.unregister_class(SolveMaze)
    del bpy.types.Scene.maze_width
    del bpy.types.Scene.maze_height
    del bpy.types.Scene.maze_unit_size
    del bpy.types.Scene.maze_wall_height

if __name__ == "__main__":
    register()
