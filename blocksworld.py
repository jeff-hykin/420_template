import dataclasses
from collections import defaultdict, namedtuple

flatten = lambda *m: (i for n in m for i in (flatten(*n) if isinstance(n, (tuple, list)) else (n,)))
StateReactionPair = namedtuple('StateReactionPair', ['state', 'reaction'])

class BlocksWorld:
    class Block:
        def __init__(self, *, name, x, y):
            self.name = name
            self._x = x
            self._y = y
            self.location = (x,y)
            
        @property
        def x(self): return self._x
        @x.setter
        def x(self, value): raise Exception(f'''Don't change block.x value, create a new block with the new x value''')
        
        @property
        def y(self): return self._y
        @y.setter
        def y(self, value): raise Exception(f'''Don't change block.y value, create a new block with the new y value''')
        
        def __repr__(self):
            return f"Block(name={repr(self.name)},x={self.x},y={self.y})"
    
    class Action:
        def __init__(self, *, move, to):
            assert isinstance(move, BlocksWorld.Block), "when calling Action(move=thing), make sure the thing is of type BlocksWorld.Block"
            assert isinstance(to, (tuple, list)), "when calling Action(move=a, to=b), make sure the 'b' is a tuple or list with x,y values"
            self.move = move
            self.to = to
        
        def visualize(self, state):
            blocks_row_then_column = [
                [" "]*state.number_of_rows
                    for _ in range(state.number_of_columns)
            ]
            blocks_row_then_column[self.move.y][self.move.x]
        
        def __repr__(self):
            return f"Action(move={self.move},to={self.to})"
    
    class State:
        columns = tuple()
        history = tuple()
        
        def __init__(self, obj, *, history=tuple()):
            self.history = history
            def list_to_column_list(a_list):
                locations = (block.location for block in a_list)
                max_x = max(x for x,y in locations)
                column_list = [None]*(max_x+1)
                for x_index, _ in enumerate(tuple(column_list)):
                    # filter by x, then sort by y
                    column_list[x_index] = sorted(
                        [ each_block for each_block in a_list if each_block.x == x_index ],
                        key=lambda each_block: each_block.y,
                    )
                return column_list
        
            if isinstance(obj, BlocksWorld.State):
                self.columns = tuple(obj.columns)
            elif type(obj) == str:
                self.columns = list_to_column_list(
                    BlocksWorld.State.string_to_blocks(obj)
                )
            elif type(obj) in (tuple, list) and all(isinstance(block, BlocksWorld.Block) for block in obj):
                self.columns = tuple(obj)
                sorted(self.columns, key=lambda each: each.x)
            else:
                raise Exception(f'''
                    Expected a value of type
                        - BlocksWorld.State
                        - str
                        - list (every element in the list of type BlocksWorld.Block)
                        - tuple (every element in the tuple of type BlocksWorld.Block)
                    However instead I recevived a value of:
                        {obj}
                ''')
        
        @property
        def blocks(self): return tuple(flatten(self.columns))
        
        @property
        def number_of_columns(self): return max(block.x for block in self.blocks)+1
        
        @property
        def number_of_rows(self): return max(block.y for block in self.blocks)+1
            
        @property
        def possible_actions(self):
            canidate_locations = []
            for each_column in self.columns:
                canidate_locations.append(len(each_column))
            
            actions = []
            for x_of_this_block, each_column in enumerate(self.columns):
                has_at_least_one_block = len(each_column) > 0
                if has_at_least_one_block:
                    block_to_move = each_column[-1]
                    canidate_locations_for_this_block = list(canidate_locations)
                    for new_x_location, new_y_location in enumerate(canidate_locations):
                        # cant move block to same location
                        if new_x_location == x_of_this_block:
                            continue
                        actions.append(
                            BlocksWorld.Action(
                                move=block_to_move,
                                to=(new_x_location, new_y_location),
                            )
                        )
            return actions
        
        @property
        def reason_is_invalid(self):
            
            # note: returns a generator, not a list
            locations = (block.location for block in self.blocks)
            non_zero_y_locations = ((x,y) for x,y in locations if y > 0)
            block_exists_at = defaultdict(
                lambda : None, 
                {
                    tuple(block.location) : block
                        for block in self.blocks
                }
            )
            # no two blocks can be in the same location
            if len(set(locations)) != len(locations):
                return "Two blocks are in the same location"
            # all blocks above 0 there must be a block underneath it
            for x,y in non_zero_y_locations:
                if not block_exists_at[x,y-1]:
                    return f"There's a block at ({x},{y}) but there's no block underneath it"
            
            return None
        
        def after_this_action(self, action):
            if not isinstance(action, BlocksWorld.Action):
                raise Exception(f'''
                    Called some_state.after_this_action(action={action})
                    However the action wasn't of type BlocksWorld.Action
                    and I don't know how to apply anything else
                ''')
            blocks_except_moving_block = tuple(block for block in self.blocks if block.location != action.move.location)
            new_block = BlocksWorld.Block(
                name=action.move.name,
                x=action.to[0],
                y=action.to[1],
            )
            # 
            # check validity of move
            # 
            blocks_with_same_location = tuple(each for each in blocks_except_moving_block if each.location == new_block.location)
            if len(blocks_with_same_location) > 0:
                raise Exception(f'''
                    Given this state:\n{self}
                    
                    I can't perform this action: {action}
                    Because then this block: {action.move}
                    Would be in the same location as: {blocks_with_same_location[0]}
                ''')
            # if stacking on top of another block
            if action.move.y > 0:
                block_underneath_location = (action.move.x, action.move.y-1)
                block_underneath_exists = any(each.location == block_underneath_location for each in blocks_except_moving_block)
                if not block_underneath_exists:
                    raise Exception(f'''
                        Given this state:\n{self}
                        
                        I can't perform this action: {action}
                        Because then this block: {action.move}
                        Would be floating in space (there's no block at {block_underneath_location})
                    ''')
            # 
            # perform move
            # 
            blocks_and_new_block = blocks_except_moving_block + tuple([new_block])
            return BlocksWorld.State(
                blocks_and_new_block,
                history=self.history + tuple([
                    StateReactionPair(
                        state=self,
                        reaction=action,
                    )  
                ]),
            )
        
        def __repr__(self):
            number_of_columns = self.number_of_columns
            blocks_row_then_column = [
                [" "]*number_of_columns
                    for _ in range(self.number_of_rows)
            ]
            for block in self.blocks:
                blocks_row_then_column[block.y][block.x] = block.name
            output_string = ""
            for each_line in reversed(blocks_row_then_column):
                output_string += " ".join(each_line)+"\n"
            output_string += "¯ "*number_of_columns
            return "\n"+output_string[0:-1]
        
        def __eq__(self, other):
            return repr(other) == repr(self)
        
        @staticmethod
        def string_to_blocks(a_string):
            list_of_blocks = []
            lines = a_string.split("\n")
            hit_first_line = False
            char_is_block = lambda each_char: not each_char.isspace() and each_char not in ('¯', '-', '_')
            y_index = -1
            for each_line in reversed(lines):
                # skip first block-less lines
                if not hit_first_line and not any(char_is_block(each_char) for each_char in each_line):
                    continue
                y_index += 1
                hit_first_line = True
                for x_index, each_char in enumerate(each_line):
                    if char_is_block(each_char):
                        list_of_blocks.append(
                            BlocksWorld.Block(
                                name=each_char,
                                x=x_index,
                                y=y_index,
                            )
                        )
            return list_of_blocks
    
start_state = BlocksWorld.State(
    """
        A
        B C
        ¯¯¯
    """.replace("\n        ","\n"),
)
goal_state = BlocksWorld.State(
    """
          A
        B C
        ¯¯¯
    """.replace("\n        ","\n"),
)
print(f'''start_state.possible_actions = {start_state.possible_actions}''')
print(f'''start_state = {start_state}''')
next_state = start_state.after_this_action(start_state.possible_actions[0])
next_state = start_state.after_this_action(start_state.possible_actions[1])
print(f'''next_state = {next_state}''')
print(f'''goal_state == start_state = {goal_state == start_state}''')