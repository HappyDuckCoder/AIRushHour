import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque
import copy

class Vehicle:
    def __init__(self, name, row, col, length, orientation, color='blue'):
        self.name = name
        self.row = row
        self.col = col
        self.length = length
        self.orientation = orientation  # 'H' for horizontal, 'V' for vertical
        self.color = color
        self.is_target = (name == 'X')  # Red car is the target
    
    def get_positions(self):
        """Get all positions occupied by this vehicle"""
        positions = []
        if self.orientation == 'H':
            for i in range(self.length):
                positions.append((self.row, self.col + i))
        else:  # Vertical
            for i in range(self.length):
                positions.append((self.row + i, self.col))
        return positions
    
    def can_move(self, direction, board_size):
        """Check if vehicle can move in given direction"""
        if self.orientation == 'H':
            if direction == 'left':
                return self.col > 0
            elif direction == 'right':
                return self.col + self.length < board_size
        else:  # Vertical
            if direction == 'up':
                return self.row > 0
            elif direction == 'down':
                return self.row + self.length < board_size
        return False
    
    def move(self, direction):
        """Move vehicle in given direction"""
        if self.orientation == 'H':
            if direction == 'left':
                self.col -= 1
            elif direction == 'right':
                self.col += 1
        else:  # Vertical
            if direction == 'up':
                self.row -= 1
            elif direction == 'down':
                self.row += 1

class RushHourGame:
    def __init__(self):
        self.board_size = 6
        self.vehicles = {}
        self.target_vehicle = 'X'
        self.exit_row = 2  # Row where the red car needs to exit
        self.exit_col = 5  # Exit is at the right edge
        
        # GUI setup
        self.root = tk.Tk()
        self.root.title("Rush Hour Puzzle Game")
        self.root.geometry("800x700")
        
        # Game state
        self.selected_vehicle = None
        self.placing_mode = False
        self.placing_vehicle_type = None
        self.placing_orientation = 'H'
        
        self.setup_gui()
        self.reset_board()
    
    def setup_gui(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = tk.Frame(main_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Vehicle placement controls
        place_frame = tk.LabelFrame(control_frame, text="Place Vehicles", font=('Arial', 10, 'bold'))
        place_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(place_frame, text="Place Red Car (2×1)", 
                 command=lambda: self.start_placing('red_car'), bg='red', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(place_frame, text="Place Car (2×1)", 
                 command=lambda: self.start_placing('car'), bg='blue', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(place_frame, text="Place Truck (3×1)", 
                 command=lambda: self.start_placing('truck'), bg='green', fg='white').pack(side=tk.LEFT, padx=2)
        
        orientation_frame = tk.Frame(place_frame)
        orientation_frame.pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(orientation_frame, text="Orientation:").pack()
        self.orientation_var = tk.StringVar(value='H')
        tk.Radiobutton(orientation_frame, text="Horizontal", variable=self.orientation_var, 
                      value='H', command=self.update_orientation).pack()
        tk.Radiobutton(orientation_frame, text="Vertical", variable=self.orientation_var, 
                      value='V', command=self.update_orientation).pack()
        
        # Game controls
        game_frame = tk.LabelFrame(control_frame, text="Game Controls", font=('Arial', 10, 'bold'))
        game_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(game_frame, text="Clear Board", command=self.reset_board).pack(side=tk.LEFT, padx=2)
        tk.Button(game_frame, text="Solve with BFS", command=self.solve_bfs, bg='orange').pack(side=tk.LEFT, padx=2)
        tk.Button(game_frame, text="Load Sample", command=self.load_sample_puzzle).pack(side=tk.LEFT, padx=2)
        
        # Status
        self.status_label = tk.Label(control_frame, text="Click 'Place Red Car' and then click on the board to place the target vehicle", 
                                   font=('Arial', 9), fg='blue')
        self.status_label.pack(side=tk.RIGHT)
        
        # Game board
        self.board_frame = tk.Frame(main_frame, bg='lightgray', relief=tk.RAISED, bd=2)
        self.board_frame.pack(expand=True, fill=tk.BOTH)
        
        # Create grid
        self.cells = []
        for row in range(self.board_size):
            cell_row = []
            for col in range(self.board_size):
                cell = tk.Button(self.board_frame, width=8, height=4, 
                               command=lambda r=row, c=col: self.cell_clicked(r, c),
                               font=('Arial', 8, 'bold'))
                cell.grid(row=row, column=col, padx=1, pady=1)
                cell_row.append(cell)
            self.cells.append(cell_row)
        
        # Add exit indicator
        exit_label = tk.Label(self.board_frame, text="EXIT", bg='red', fg='white', font=('Arial', 8, 'bold'))
        exit_label.grid(row=self.exit_row, column=self.board_size, padx=5)
        
        # Move counter and solution display
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.move_counter = tk.Label(info_frame, text="Moves: 0", font=('Arial', 10))
        self.move_counter.pack(side=tk.LEFT)
        
        self.solution_text = tk.Text(info_frame, height=4, width=50)
        self.solution_text.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        self.moves_made = 0
    
    def start_placing(self, vehicle_type):
        self.placing_mode = True
        self.placing_vehicle_type = vehicle_type
        self.placing_orientation = self.orientation_var.get()
        self.status_label.config(text=f"Click on the board to place {vehicle_type} ({'Horizontal' if self.placing_orientation == 'H' else 'Vertical'})")
    
    def update_orientation(self):
        self.placing_orientation = self.orientation_var.get()
        if self.placing_mode:
            self.status_label.config(text=f"Click on the board to place {self.placing_vehicle_type} ({'Horizontal' if self.placing_orientation == 'H' else 'Vertical'})")
    
    def cell_clicked(self, row, col):
        if self.placing_mode:
            self.place_vehicle(row, col)
        else:
            self.handle_vehicle_interaction(row, col)
    
    def place_vehicle(self, row, col):
        # Determine vehicle properties
        if self.placing_vehicle_type == 'red_car':
            name = 'X'
            length = 2
            color = 'red'
        elif self.placing_vehicle_type == 'car':
            name = f"C{len([v for v in self.vehicles.values() if not v.is_target]) + 1}"
            length = 2
            color = 'lightblue'
        elif self.placing_vehicle_type == 'truck':
            name = f"T{len([v for v in self.vehicles.values() if v.length == 3]) + 1}"
            length = 3
            color = 'lightgreen'
        
        # Check if placement is valid
        if self.can_place_vehicle(row, col, length, self.placing_orientation):
            # Remove existing red car if placing a new one
            if self.placing_vehicle_type == 'red_car' and 'X' in self.vehicles:
                del self.vehicles['X']
            
            vehicle = Vehicle(name, row, col, length, self.placing_orientation, color)
            self.vehicles[name] = vehicle
            self.update_display()
            self.placing_mode = False
            self.status_label.config(text="Vehicle placed! Select a vehicle to move it or place another vehicle.")
        else:
            messagebox.showerror("Invalid Placement", "Cannot place vehicle here - space is occupied or out of bounds!")
    
    def can_place_vehicle(self, row, col, length, orientation):
        # Check bounds
        if orientation == 'H':
            if col + length > self.board_size:
                return False
        else:  # Vertical
            if row + length > self.board_size:
                return False
        
        # Check for collisions
        occupied_positions = set()
        for vehicle in self.vehicles.values():
            occupied_positions.update(vehicle.get_positions())
        
        new_positions = []
        if orientation == 'H':
            for i in range(length):
                new_positions.append((row, col + i))
        else:
            for i in range(length):
                new_positions.append((row + i, col))
        
        for pos in new_positions:
            if pos in occupied_positions:
                return False
        
        return True
    
    def handle_vehicle_interaction(self, row, col):
        # Find vehicle at this position
        clicked_vehicle = None
        for vehicle in self.vehicles.values():
            if (row, col) in vehicle.get_positions():
                clicked_vehicle = vehicle
                break
        
        if clicked_vehicle:
            if self.selected_vehicle == clicked_vehicle:
                # Deselect
                self.selected_vehicle = None
                self.status_label.config(text="Vehicle deselected")
            else:
                # Select vehicle
                self.selected_vehicle = clicked_vehicle
                self.status_label.config(text=f"Selected {clicked_vehicle.name}. Use arrow keys or click adjacent empty cells to move.")
        else:
            # Try to move selected vehicle to this position
            if self.selected_vehicle:
                self.try_move_vehicle_to_position(row, col)
        
        self.update_display()
    
    def try_move_vehicle_to_position(self, target_row, target_col):
        if not self.selected_vehicle:
            return
        
        vehicle = self.selected_vehicle
        current_positions = vehicle.get_positions()
        
        # Determine direction and distance
        if vehicle.orientation == 'H':
            if target_row != vehicle.row:
                return  # Can't move vertically
            
            if target_col < vehicle.col:
                direction = 'left'
                distance = vehicle.col - target_col
            elif target_col >= vehicle.col + vehicle.length:
                direction = 'right'
                distance = target_col - (vehicle.col + vehicle.length - 1)
            else:
                return  # Invalid target
        else:  # Vertical
            if target_col != vehicle.col:
                return  # Can't move horizontally
            
            if target_row < vehicle.row:
                direction = 'up'
                distance = vehicle.row - target_row
            elif target_row >= vehicle.row + vehicle.length:
                direction = 'down'
                distance = target_row - (vehicle.row + vehicle.length - 1)
            else:
                return  # Invalid target
        
        # Try to move step by step
        for _ in range(distance):
            if self.can_move_vehicle(vehicle, direction):
                vehicle.move(direction)
                self.moves_made += 1
            else:
                break
        
        self.move_counter.config(text=f"Moves: {self.moves_made}")
        self.check_win_condition()
    
    def can_move_vehicle(self, vehicle, direction):
        if not vehicle.can_move(direction, self.board_size):
            return False
        
        # Create temporary vehicle to check new position
        temp_vehicle = copy.deepcopy(vehicle)
        temp_vehicle.move(direction)
        new_positions = set(temp_vehicle.get_positions())
        
        # Check for collisions with other vehicles
        for other_vehicle in self.vehicles.values():
            if other_vehicle.name != vehicle.name:
                other_positions = set(other_vehicle.get_positions())
                if new_positions & other_positions:
                    return False
        
        return True
    
    def update_display(self):
        # Clear board
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.cells[row][col].config(text='', bg='white', relief=tk.RAISED)
        
        # Draw vehicles
        for vehicle in self.vehicles.values():
            positions = vehicle.get_positions()
            for i, (row, col) in enumerate(positions):
                cell = self.cells[row][col]
                if vehicle.is_target:
                    cell.config(bg='red', text='X', fg='white')
                else:
                    cell.config(bg=vehicle.color, text=vehicle.name, fg='black')
                
                # Highlight selected vehicle
                if vehicle == self.selected_vehicle:
                    cell.config(relief=tk.SUNKEN, bd=3)
    
    def reset_board(self):
        self.vehicles = {}
        self.selected_vehicle = None
        self.placing_mode = False
        self.moves_made = 0
        self.move_counter.config(text="Moves: 0")
        self.solution_text.delete(1.0, tk.END)
        self.update_display()
        self.status_label.config(text="Board cleared. Place vehicles to start a new puzzle.")
    
    def load_sample_puzzle(self):
        """Load a sample puzzle for testing"""
        self.reset_board()
        
        # Add sample vehicles
        self.vehicles['X'] = Vehicle('X', 2, 0, 2, 'H', 'red')  # Red car (target)
        self.vehicles['C1'] = Vehicle('C1', 0, 0, 2, 'V', 'lightblue')  # Vertical car
        self.vehicles['C2'] = Vehicle('C2', 0, 2, 2, 'H', 'lightblue')  # Horizontal car
        self.vehicles['T1'] = Vehicle('T1', 3, 0, 3, 'H', 'lightgreen')  # Horizontal truck
        self.vehicles['C3'] = Vehicle('C3', 4, 3, 2, 'V', 'lightblue')  # Vertical car
        self.vehicles['C4'] = Vehicle('C4', 1, 4, 2, 'V', 'lightblue')  # Vertical car
        
        self.update_display()
        self.status_label.config(text="Sample puzzle loaded! Try to get the red car to the exit.")
    
    def check_win_condition(self):
        if 'X' in self.vehicles:
            red_car = self.vehicles['X']
            if (red_car.orientation == 'H' and 
                red_car.row == self.exit_row and 
                red_car.col + red_car.length == self.board_size):
                messagebox.showinfo("Congratulations!", f"You solved the puzzle in {self.moves_made} moves!")
                return True
        return False

    def get_board_state(self):
        """Get current board state for BFS"""
        state = {}
        for name, vehicle in self.vehicles.items():
            state[name] = (vehicle.row, vehicle.col, vehicle.length, vehicle.orientation)
        return tuple(sorted(state.items()))
    
    def set_board_state(self, state):
        """Set board state from BFS result"""
        self.vehicles = {}
        for name, (row, col, length, orientation) in dict(state).items():
            color = 'red' if name == 'X' else ('lightgreen' if length == 3 else 'lightblue')
            self.vehicles[name] = Vehicle(name, row, col, length, orientation, color)
    
    def get_possible_moves(self, state):
        """Get all possible moves from current state"""
        self.set_board_state(state)
        moves = []
        
        for vehicle_name, vehicle in self.vehicles.items():
            # Try all four directions
            for direction in ['up', 'down', 'left', 'right']:
                if self.can_move_vehicle(vehicle, direction):
                    # Create new state after move
                    new_vehicles = copy.deepcopy(self.vehicles)
                    new_vehicles[vehicle_name].move(direction)
                    
                    new_state = {}
                    for name, v in new_vehicles.items():
                        new_state[name] = (v.row, v.col, v.length, v.orientation)
                    new_state = tuple(sorted(new_state.items()))
                    
                    moves.append((new_state, f"{vehicle_name} {direction}"))
        
        return moves
    
    def is_solved(self, state):
        """Check if red car has exited the board"""
        state_dict = dict(state)
        if 'X' not in state_dict:
            return False

        row, col, length, orientation = state_dict['X']

        # Xe đỏ phải ở đúng hàng EXIT, nằm ngang, và vượt ra ngoài biên phải
        return (
            orientation == 'H' and
            row == self.exit_row and
            col + length == self.board_size
        )

    def solve_bfs(self):
        """Solve puzzle using BFS algorithm"""
        if 'X' not in self.vehicles:
            messagebox.showerror("Error", "Place the red car (target vehicle) first!")
            return
        
        self.solution_text.delete(1.0, tk.END)
        self.solution_text.insert(tk.END, "Solving with BFS...\n")
        self.root.update()
        
        start_state = self.get_board_state()
        
        if self.is_solved(start_state):
            self.solution_text.insert(tk.END, "Puzzle is already solved!\n")
            return
        
            
        visited = {start_state}
        
        max_iterations = 50000  # Prevent infinite loops
        iterations = 0
        
        while queue and iterations < max_iterations:
            iterations += 1
            current_state, path = queue.popleft()
            
            if iterations % 1000 == 0:
                self.solution_text.insert(tk.END, f"Searched {iterations} states...\n")
                self.root.update()
            
            if self.is_solved(current_state):
                self.solution_text.insert(tk.END, f"\nSolution found in {len(path)} moves after searching {iterations} states!\n")
                self.solution_text.insert(tk.END, "Solution steps:\n")
                for i, move in enumerate(path, 1):
                    self.solution_text.insert(tk.END, f"{i}. {move}\n")
                return
            
            # Get all possible moves
            for next_state, move in self.get_possible_moves(current_state):
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append((next_state, path + [move]))
        
        if iterations >= max_iterations:
            self.solution_text.insert(tk.END, f"\nSearch stopped after {max_iterations} iterations.\n")
            self.solution_text.insert(tk.END, "Puzzle might be unsolvable or require more computation.\n")
        else:
            self.solution_text.insert(tk.END, f"\nNo solution found after searching {iterations} states.\n")
            self.solution_text.insert(tk.END, "Puzzle might be unsolvable.\n")
    
    def run(self):
        # Bind keyboard events
        self.root.bind('<Key>', self.key_pressed)
        self.root.focus_set()
        self.root.mainloop()
    
    def key_pressed(self, event):
        if not self.selected_vehicle:
            return
        
        direction_map = {
            'Up': 'up',
            'Down': 'down', 
            'Left': 'left',
            'Right': 'right'
        }
        
        if event.keysym in direction_map:
            direction = direction_map[event.keysym]
            if self.can_move_vehicle(self.selected_vehicle, direction):
                self.selected_vehicle.move(direction)
                self.moves_made += 1
                self.move_counter.config(text=f"Moves: {self.moves_made}")
                self.update_display()
                self.check_win_condition()

if __name__ == "__main__":
    game = RushHourGame()
    game.run()