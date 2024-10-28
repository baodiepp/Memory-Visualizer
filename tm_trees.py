"""
Assignment 2: Trees for Treemap

=== CSC148 Summer 2022 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2022 Bogdan Simion, David Liu, Diane Horton,
                   Haocheng Hu, Jacqueline Smith

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations

import math
import os
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None
        self._expanded = False

        # 1. Initialize self._colour
        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))

        # 2. Initialize self.data_size if empty
        if self._name is not None:
            # get this trees data size if not empty
            for subtree in self._subtrees:
                data_size += subtree.data_size
        self.data_size = data_size

        # 3. Set this tree as the parent for each of its subtrees.
        for sub in self._subtrees:
            sub._parent_tree = self

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def get_parent(self) -> Optional[TMTree]:
        """Returns the parent of this tree.
        """
        return self._parent_tree

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """

        x, y, width, height = rect
        top_right = width + x
        left_button = height + y
        zero_area = (0, 0, 0, 0)
        self.rect = (x, y, width, height)

        if self.is_empty() or self.data_size == 0:
            self.rect = zero_area

        for sub in self._subtrees:
            if self.data_size != 0 and width > height:
                sub_width = math.floor(width * sub.data_size / self.data_size)
                sub_height = height
                if sub == self._subtrees[-1]:
                    sub_width = top_right - x
                sub.update_rectangles((x, y, sub_width, sub_height))
                x += sub_width

            else:
                sub_width = width
                sub_height = math.floor(
                    height * sub.data_size / self.data_size) \
                    if self.data_size != 0 else 0

                if sub == self._subtrees[-1]:
                    sub_height = left_button - y
                sub.update_rectangles((x, y, sub_width, sub_height))
                y += sub_height

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """

        if self.data_size == 0:
            return []
        elif self._expanded and self.is_empty():
            return []
        elif (self._expanded and not self.is_empty() and not self._subtrees) \
                or (not self._expanded):
            return [(self.rect, self._colour)]
        else:
            rec_colour = []
            for subtree in self._subtrees:
                rec_colour.extend(subtree.get_rectangles())
            return rec_colour

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside this
        tree's rectangle.

        If <pos> is on the shared edge between two or more rectangles,
        always return the leftmost and topmost rectangle (wherever applicable).
        """

        if not self._subtrees or not self._expanded:
            return self
        for subtree in self._subtrees:
            opt_1 = pos[0] in [
                subtree.rect[0], subtree.rect[0] + subtree.rect[2]
            ]
            opt_2 = pos[1] in [
                subtree.rect[1], subtree.rect[1] + subtree.rect[3]
            ]
            opt_3 = subtree.rect[0] < pos[0] < (
                subtree.rect[0] + subtree.rect[2]) and subtree.rect[1] \
                < pos[1] < (subtree.rect[1] + subtree.rect[3])

            if opt_1:
                return subtree.get_tree_at_position((pos[0] - 1, pos[1]))

            elif opt_2:
                return subtree.get_tree_at_position((pos[0], pos[1] - 1))

            elif opt_3:
                return subtree.get_tree_at_position(pos)
        return None

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """

        if self.is_empty():
            return 0
        elif not self._subtrees:
            return self.data_size
        else:
            size = 0
            for subtree in self._subtrees:
                size += subtree.update_data_sizes()
                self.data_size = size
            return size

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """

        if not self._subtrees and destination._subtrees:
            destination._subtrees.append(self)
            if self._parent_tree is not None:
                if self in self._parent_tree._subtrees:
                    self._parent_tree._subtrees.remove(self)
                self._parent_tree.update_data_sizes()
        destination.update_data_sizes()
        return None

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """

        if self._subtrees or self.is_empty():
            return None

        change = math.ceil(self.data_size * (abs(factor)))
        self.data_size += -(abs(change)) if factor < 0 else abs(change)
        return None

    def delete_self(self) -> bool:
        """Removes the current node from the visualization and
        returns whether the deletion was successful.

        Only do this if this node has a parent tree.

        Do not set self._parent_tree to None, because it might be used
        by the visualiser to go back to the parent folder.
        """

        if self._parent_tree is not None:
            self._parent_tree._subtrees.remove(self)
            return True
        return False

    def expand(self) -> None:
        """
        expand this tree only if it is a folder
        """
        if self._subtrees:
            self._expanded = True
        return None

    def expand_all(self) -> None:
        """
        expand the entire tree
        """
        self.expand()
        for subtree in self._subtrees:
            subtree.expand_all()
        return None

    def collapse(self) -> None:
        """
        collapse the parent folder
        """

        if self._parent_tree is not None:
            self._parent_tree._col_sub()

    def _col_sub(self) -> None:
        """
        collapse subtrees of the parent tree
        """
        self._expanded = False
        for subtree in self._subtrees:
            subtree._col_sub()

    def collapse_all(self) -> None:
        """
        collapse the entire tree
        """

        self._root()._col_sub()

    def _root(self) -> TMTree:
        """
        return the root of this tree
        """
        return self if self._parent_tree is None else self._parent_tree._root()

    # Methods for the string representation
    def get_path_string(self) -> str:
        """
        Return a string representing the path containing this tree
        and its ancestors, using the separator for this OS between each
        tree's name.
        """
        if self._parent_tree is None:
            return self._name
        else:
            return self._parent_tree.get_path_string() \
                + self.get_separator() + self._name

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError

    def __str__(self) -> str:

        return f'Name: {self._name} --- Parent: {self._parent_tree._name}'


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """

        # check if the path is valid
        subtrees = []
        if os.path.isdir(path):
            # create new file system trees for files and folders encountered
            file_names = os.listdir(path)
            subtrees.extend(
                FileSystemTree(os.path.join(path, name)) for name in file_names
            )

            # initialize folders to get TMTree attributes
            super().__init__(
                os.path.basename(path), subtrees, 0
            )

        else:
            # initialize the file to get TMTree attributes
            super().__init__(
                os.path.basename(path), subtrees, os.path.getsize(path)
            )

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """

        def convert_size(data_size: float, suffix: str = 'B') -> str:
            suffixes = {'B': 'kB', 'kB': 'MB', 'MB': 'GB', 'GB': 'TB'}
            if data_size < 1024 or suffix == 'TB':
                return f'{data_size:.2f}{suffix}'
            return convert_size(data_size / 1024, suffixes[suffix])

        components = []
        if len(self._subtrees) == 0:
            components.append('file')
        else:
            components.append('folder')
            components.append(f'{len(self._subtrees)} items')
        components.append(convert_size(self.data_size))
        return f' ({", ".join(components)})'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
