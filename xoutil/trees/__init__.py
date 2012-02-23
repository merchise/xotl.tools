# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.trees
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise Autrement
# All rights reserved.
#
# Author: Medardo Rodriguez
#       
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#       
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#       
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.


'''
Tree structures can be traversed in many different ways. Starting at
the root of a binary tree, there are three main steps that can be
performed and the order in which they are performed defines the
traversal type. These steps (in no particular order) are:

- performing an action on the current node (referred to as "visiting"
  the node),
- traversing to the left child node, and 
- traversing to the right child node.

The names given for particular style of traversal came from the
position of root element with regard to the left and right nodes:

* Depth-first Traversal: Imagine that the left and right nodes are
  constant in space, then

     - pre-order, the root node could be placed to the left of the
       left node
     - in-order, between the left and right node
     - post-order, to the right of the right node

* Breadth-first traversal: where we visit every node on a level before
  going to a lower level:

     - level-order

This module is intended to contain all requirements for "Tree
Traversal".
'''

from __future__ import (division as _py3_division, print_function as _py3_print, unicode_literals as _py3_unicode)

class Tree(object):
    pass


class Node(object):
    NAME_SEPARATOR = ' :: '

    def full_name(self):
        '''Requires that node sub-classes define "name" and "parents" attributes.'''
        name_list = [parent.name for parent in self.parents]
        name_list.reverse()
        name_list.append(self.name)
        return self.NAME_SEPARATOR.join(name_list)



__all__ = (b'Tree', b'Node')
